"""Legacy schema adapters and quote-preserving UTC aggregation.

Inherits the old pipeline's Parquet, deterministic deduplication, UTC and
atomic-output conventions; replaces its Mid-only aggregation. Old inputs
are read only. DuckDB is imported only when conversion is requested.
"""
import argparse
import csv
import json
from pathlib import Path

from .features import QUOTES, _validate_bars, file_hash
from .legacy_catalog import ORIGINAL_FEATURE_NAMES, BLOCKED_CACHED_FEATURES, LEGACY_COMMIT

DATASETS = {
    "raw": ("raw_csv", 1), "all_data": ("all_data/all_data.parquet", 1),
    "ohlcv_5m": ("ohlcv_5m/ohlcv_5m.parquet", 5), "ohlcv_1h": ("ohlcv_1h/ohlcv_1h.parquet", 60),
    "features_5m": ("ohlcv_5m_features/ohlcv_5m_features.parquet", 5),
    "features_1h": ("ohlcv_1h_features/ohlcv_1h_features.parquet", 60),
}


def ident(name):
    return '"' + name.replace('"', '""') + '"'


def literal(value):
    return "'" + str(value).replace("'", "''") + "'"


def schema_mapping(columns):
    """Pure schema classifier, tested independently of DuckDB."""
    columns = set(columns)
    if {"instrument", "bar_open_time", "bar_close_time", "open", "high", "low", "close", "volume", "is_complete"} <= columns:
        mode, time_name = "canonical", "bar_open_time"
        price = {point: point for point in ("open", "high", "low", "close")}
    elif {"instrument", "time", "mid_o", "mid_h", "mid_l", "mid_c", "volume", "is_complete"} <= columns:
        mode, time_name = "legacy_raw", "time"
        price = dict(zip(("open", "high", "low", "close"), ("mid_o", "mid_h", "mid_l", "mid_c")))
    elif {"instrument", "time", "open", "high", "low", "close", "volume", "n_bars"} <= columns:
        mode, time_name = "legacy_ohlcv_or_gold", "time"
        price = {point: point for point in ("open", "high", "low", "close")}
    else:
        raise ValueError("Unrecognized legacy/canonical schema; see migration/DATA_CONTRACT.md")
    quote = {}
    for side in ("bid", "ask"):
        for point, old in zip(("open", "high", "low", "close"), ("o", "h", "l", "c")):
            candidate = f"{side}_{point}" if f"{side}_{point}" in columns else f"{side}_{old}"
            if candidate in columns:
                quote[f"{side}_{point}"] = candidate
    if len(quote) not in (0, 8):
        raise ValueError("Bid/Ask columns must be absent or provide all eight fields")
    return {"mode": mode, "time": time_name, "price": price, "quotes": quote}


def selected_legacy_features(columns, reuse):
    if not reuse:
        return []
    # Stored VWAP is known to be stale in the pinned source's documentation.
    # H1 projections and experimental catalogue columns need separate review.
    return sorted((set(columns) & ORIGINAL_FEATURE_NAMES) - BLOCKED_CACHED_FEATURES)


def aggregate_sql(minutes):
    if type(minutes) is not int or minutes <= 0:
        raise ValueError("Positive integer target minutes required")
    quotes = []
    for side in ("bid", "ask"):
        for point in ("open", "high", "low", "close"):
            name = f"{side}_{point}"
            expr = {"open": f"arg_min({name}, bar_open_time)", "close": f"arg_max({name}, bar_open_time)",
                    "high": f"max({name})", "low": f"min({name})"}[point]
            quotes.append(f"CASE WHEN count({name})=count(*) THEN {expr} END AS {name}")
    return f"""CREATE OR REPLACE TEMP TABLE canonical_output AS
        SELECT instrument, bucket AS bar_open_time, bucket+INTERVAL '{minutes} minutes' AS bar_close_time,
            arg_min(open, bar_open_time) AS open, max(high) AS high, min(low) AS low,
            arg_max(close, bar_open_time) AS close, sum(volume) AS volume,
            true AS is_complete, sum(n_bars)::BIGINT AS n_bars, {', '.join(quotes)}
        FROM (SELECT *, time_bucket(INTERVAL '{minutes} minutes', bar_open_time) AS bucket FROM normalized)
        GROUP BY instrument, bucket
        HAVING sum(n_bars)={minutes} AND min(bar_open_time)=bucket
           AND max(bar_close_time)=bucket+INTERVAL '{minutes} minutes'
        ORDER BY instrument, bar_open_time"""


def convert(source, output, source_minutes, target_minutes=None, reuse_features=False, assume_utc=False):
    import duckdb
    if type(source_minutes) is not int or source_minutes <= 0:
        raise ValueError("Positive integer source minutes required")
    target_minutes = target_minutes or source_minutes
    if type(target_minutes) is not int or target_minutes < source_minutes or target_minutes % source_minutes:
        raise ValueError("Target minutes must be a positive multiple of source minutes")
    if reuse_features and target_minutes != source_minutes:
        raise ValueError("Cached features cannot be reused across resampling; recompute on the target bars")
    source, output = Path(source).resolve(), Path(output).resolve()
    if source.is_dir():
        if output.is_relative_to(source):
            raise ValueError("Put output outside the legacy source tree")
        files = sorted(source.rglob("*.csv")) + sorted(source.rglob("*.parquet"))
    else:
        files = [source]
    if not files or any(not path.is_file() for path in files):
        raise FileNotFoundError("No local CSV/Parquet data found; market data is not committed to the legacy Git repository")
    if output in files:
        raise ValueError("Output must not replace legacy input")
    suffixes = {path.suffix.lower() for path in files}
    if suffixes not in ({".csv"}, {".parquet"}):
        raise ValueError("Select one homogeneous CSV or Parquet dataset")
    if output.suffix not in {".csv", ".parquet"}:
        raise ValueError("Output extension must be .csv or .parquet")
    with duckdb.connect() as con:
        con.execute("SET TimeZone='UTC'")
        reader = "read_parquet(?, union_by_name=true, filename=true)" if suffixes == {".parquet"} else "read_csv(?, union_by_name=true, all_varchar=true, header=true, filename=true)"
        # Check every source file, rather than only the first file in a glob.
        mappings = []
        for path in files:
            names = [row[0] for row in con.execute("DESCRIBE SELECT * FROM " + reader, [[str(path)]]).fetchall()]
            mappings.append(schema_mapping(names))
        if any(item != mappings[0] for item in mappings):
            raise ValueError("Source files have different schema mappings; import those datasets separately")
        mapping = mappings[0]
        con.execute("CREATE TEMP TABLE incoming AS SELECT * FROM " + reader, [[str(path) for path in files]])
        columns = {row[0] for row in con.execute("DESCRIBE incoming").fetchall()}
        time = ident(mapping["time"])
        if not assume_utc:
            timezone_missing = con.execute(f"SELECT count(*) FROM incoming WHERE {time} IS NULL OR NOT regexp_matches(CAST({time} AS VARCHAR), '[T ][0-9]{{2}}:[0-9]{{2}}.*(Z|[+-][0-9]{{2}}(:?[0-9]{{2}})?)$')").fetchone()[0]
            if timezone_missing:
                raise ValueError("Naive timestamps require explicit --assume-utc after checking the source")
        features = selected_legacy_features(columns, reuse_features)
        complete = "coalesce(try_cast(is_complete AS BOOLEAN), false)" if "is_complete" in columns else "true"
        n_bars = "CAST(n_bars AS BIGINT)" if "n_bars" in columns else str(source_minutes)
        closing = "CAST(bar_close_time AS TIMESTAMPTZ)" if mapping["mode"] == "canonical" else f"CAST({time} AS TIMESTAMPTZ)+INTERVAL '{source_minutes} minutes'"
        prices = [f"CAST({ident(original)} AS DOUBLE) AS {name}" for name, original in mapping["price"].items()]
        quotes = [f"CAST({ident(mapping['quotes'][name])} AS DOUBLE) AS {name}" if name in mapping["quotes"] else f"NULL::DOUBLE AS {name}" for name in QUOTES]
        extra = [f"CASE WHEN isnan(CAST({ident(name)} AS DOUBLE)) THEN NULL ELSE CAST({ident(name)} AS DOUBLE) END AS {ident(name)}" for name in features]
        con.execute(f"""CREATE TEMP TABLE normalized_candidates AS SELECT instrument,
            CAST({time} AS TIMESTAMPTZ) AS bar_open_time, {closing} AS bar_close_time,
            {', '.join(prices)}, CAST(volume AS DOUBLE) AS volume, true AS is_complete,
            {n_bars} AS n_bars, {', '.join(quotes+extra)}, filename AS _source_file
            FROM incoming WHERE {complete} AND {n_bars}={source_minutes}""")
        qscore = "+".join(f"({name} IS NOT NULL)::INTEGER" for name in QUOTES)
        tie_columns = ["open", "high", "low", "close", "volume", *QUOTES, *features]
        con.execute(f"""CREATE TEMP TABLE normalized AS
            SELECT * EXCLUDE(_source_file, _row) FROM (
                SELECT *, row_number() OVER (PARTITION BY instrument, bar_open_time
                    ORDER BY ({qscore}) DESC, _source_file, {', '.join(map(ident, tie_columns))}) AS _row
                FROM normalized_candidates) WHERE _row=1""")
        con.execute("CREATE TEMP VIEW bars AS SELECT * FROM normalized")
        _validate_bars(con, True)
        bad_duration = con.execute("SELECT count(*) FROM normalized WHERE epoch(bar_close_time-bar_open_time) != ? OR epoch(bar_open_time) % ? != 0", [source_minutes*60, source_minutes*60]).fetchone()[0]
        if bad_duration:
            raise ValueError("Source duration/alignment does not match --source-minutes")
        if target_minutes == source_minutes:
            con.execute("CREATE TEMP VIEW canonical_output AS SELECT * FROM normalized")
        else:
            con.execute(aggregate_sql(target_minutes))
        count = con.execute("SELECT count(*) FROM canonical_output").fetchone()[0]
        if not count:
            raise ValueError("No complete output bars")
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_name(output.name+".tmp")
        format_sql = "PARQUET" if output.suffix == ".parquet" else "CSV, HEADER true"
        try:
            con.execute(f"COPY (SELECT * FROM canonical_output ORDER BY instrument, bar_open_time) TO {literal(temporary)} (FORMAT {format_sql})")
            temporary.replace(output)
        except Exception:
            temporary.unlink(missing_ok=True)
            raise
        report = {"source_schema": mapping["mode"], "source_code_revision_reviewed": LEGACY_COMMIT,
            "data_producer_revision": "unknown; not inferred from the inspected code revision",
            "source_files": [{"path": str(path), "sha256": file_hash(path), "bytes": path.stat().st_size} for path in files],
            "input_rows": con.execute("SELECT count(*) FROM incoming").fetchone()[0],
            "complete_candidates": con.execute("SELECT count(*) FROM normalized_candidates").fetchone()[0],
            "deduplicated_rows": con.execute("SELECT count(*) FROM normalized").fetchone()[0],
            "output_rows": count, "source_minutes": source_minutes, "target_minutes": target_minutes,
            "partial_bar_policy": "drop", "quote_policy": "preserve full observed Bid/Ask or retain nulls; no reconstruction",
            "cached_feature_columns": features, "excluded_cached_columns": sorted(name for name in columns if name in BLOCKED_CACHED_FEATURES or name.startswith("h1_")),
            "output_sha256": file_hash(output), "output": str(output)}
    output.with_suffix(output.suffix+".import.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description="Import legacy raw, OHLCV or Gold files into the new data contract")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--source")
    group.add_argument("--legacy-root", help="Local path to the old moneta repository")
    parser.add_argument("--dataset", choices=DATASETS, default="ohlcv_1h")
    parser.add_argument("--source-minutes", type=int)
    parser.add_argument("--target-minutes", type=int)
    parser.add_argument("--reuse-features", action="store_true")
    parser.add_argument("--assume-utc", action="store_true")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    source = args.source
    minutes = args.source_minutes
    if args.legacy_root:
        relative, dataset_minutes = DATASETS[args.dataset]
        source = Path(args.legacy_root)/"data"/relative
        minutes = minutes or dataset_minutes
    if not minutes:
        parser.error("--source-minutes is required with --source")
    try:
        report = convert(source, args.output, minutes, args.target_minutes, args.reuse_features, args.assume_utc)
    except (ImportError, ValueError, OSError) as error:
        parser.exit(2, f"Import failed: {error}\n")
    print(json.dumps({"output": report["output"], "rows": report["output_rows"], "cached_features": len(report["cached_feature_columns"])}, indent=2))


if __name__ == "__main__":
    main()
