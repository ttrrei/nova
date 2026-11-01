"""Own raw sources, validate/deduplicate bars, and preserve bid/ask through aggregation."""

import csv
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pyarrow.parquet as pq

from .common import file_hash, identity, sql_string, write_json
from .store import connect, dataset, parquet_view, register

DATA_VERSION = "nova-market-v1"
PRICES = [
    f"{side}{point}"
    for side in ("", "bid_", "ask_")
    for point in ("open", "high", "low", "close")
]
QUOTES = PRICES[4:]
OANDA_REQUIRED = {
    "instrument",
    "time",
    "is_complete",
    "volume",
    "mid_o",
    "mid_h",
    "mid_l",
    "mid_c",
}
CANONICAL_REQUIRED = {
    "instrument",
    "bar_open_time",
    "bar_close_time",
    "is_complete",
    "volume",
    "open",
    "high",
    "low",
    "close",
}
OHLCV_REQUIRED = {
    "instrument",
    "time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "n_bars",
}


def archive_sources(source, root):
    """Hard links use no duplicate disk space; copy when filesystems differ.

    Files are immutable inputs: ingestion always hashes their current contents.
    Neither Nova nor its commands edit archived CSV or Parquet sources.
    """
    source, root = Path(source).resolve(), Path(root).resolve()
    paths = (
        sorted(
            p
            for p in source.rglob("*")
            if p.is_file() and p.suffix.lower() in {".csv", ".parquet"}
        )
        if source.is_dir()
        else [source]
    )
    formats = {p.suffix.lower() for p in paths}
    if (
        not paths
        or formats not in ({".csv"}, {".parquet"})
        or any(not p.is_file() for p in paths)
    ):
        raise ValueError("Select a homogeneous CSV or Parquet dataset")
    destination = root / ("raw_csv" if formats == {".csv"} else "raw_parquet")
    records = []
    for index, path in enumerate(paths):
        relative = path.relative_to(source) if source.is_dir() else Path(path.name)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        digest = file_hash(path)
        if target.exists():
            if not os.path.samefile(path, target) and file_hash(target) != digest:
                raise ValueError(
                    f"Archived source differs: {target}. Use a new store for a different source snapshot"
                )
        else:
            try:
                os.link(path, target)
            except OSError:
                shutil.copy2(path, target)
        records.append(
            {
                "path": str(target),
                "relative_path": str(relative),
                "bytes": target.stat().st_size,
                "sha256": digest,
            }
        )
        if (index + 1) % 100 == 0:
            print(f"Archived and hashed {index + 1}/{len(paths)} raw files", flush=True)
    return records


def _source_schema(records, kind):
    required = {
        "oanda": OANDA_REQUIRED,
        "canonical": CANONICAL_REQUIRED,
        "ohlcv": OHLCV_REQUIRED,
    }[kind]
    input_columns = set()
    for record in records:
        if Path(record["path"]).suffix.lower() == ".parquet":
            fields = pq.read_schema(record["path"]).names
        else:
            with Path(record["path"]).open(newline="", encoding="utf-8-sig") as stream:
                fields = next(csv.reader(stream), [])
        if len(fields) != len(set(fields)) or not required <= set(fields):
            raise ValueError(f"Invalid {kind} source schema: {record['path']}")
        input_columns.update(fields)
        quote_names = (
            [f"{side}_{p}" for side in ("bid", "ask") for p in ("o", "h", "l", "c")]
            if kind == "oanda"
            else QUOTES
        )
        short_quotes = [
            f"{s}_{p}" for s in ("bid", "ask") for p in ("o", "h", "l", "c")
        ]
        if kind == "ohlcv" and set(short_quotes) & set(fields):
            if set(QUOTES) & set(fields):
                raise ValueError("Do not mix short and canonical quote names")
            quote_names = short_quotes
        if sum(name in fields for name in quote_names) not in (0, 8):
            raise ValueError("Provide all eight bid/ask columns or none")
    if (
        kind == "ohlcv"
        and set(QUOTES) & input_columns
        and set(short_quotes) & input_columns
    ):
        raise ValueError("Import quote naming formats separately")
    return input_columns


def _validate(con, relation, minutes):
    """Validate before dropping incomplete rows, so malformed inputs cannot hide."""
    errors = {}
    checks = {
        "instrument": "instrument IS NULL OR NOT regexp_full_match(instrument, '[A-Za-z0-9_.-]+')",
        "timestamp": "bar_open_time IS NULL OR bar_close_time IS NULL OR bar_close_time <= bar_open_time",
        "duration": f"epoch(bar_close_time-bar_open_time) != {minutes * 60}",
        "volume": "volume IS NULL OR NOT isfinite(volume) OR volume < 0",
        "partial_quotes": "("
        + " + ".join(f"({p} IS NOT NULL)::INT" for p in QUOTES)
        + ") NOT IN (0,8)",
    }
    for prefix in ("", "bid_", "ask_"):
        o, h, low, c = [prefix + p for p in ("open", "high", "low", "close")]
        clauses = [
            f"{p} IS NULL OR NOT isfinite({p}) OR {p} <= 0" for p in (o, h, low, c)
        ]
        clauses += [f"{low}>{h}", f"{o}<{low}", f"{o}>{h}", f"{c}<{low}", f"{c}>{h}"]
        expr = "(" + " OR ".join(clauses) + ")"
        if prefix:
            expr = f"({o} IS NOT NULL AND {expr})"
        checks[prefix + "ohlc"] = expr
    checks["negative_spread"] = " OR ".join(
        f"ask_{p}<bid_{p}" for p in ("open", "high", "low", "close")
    )
    expressions = ",".join(f"count(*) FILTER(WHERE {expr})" for expr in checks.values())
    counts = con.execute(f"SELECT {expressions} FROM {relation}").fetchone()
    errors = {name: count for name, count in zip(checks, counts) if count}
    if errors:
        raise ValueError(f"Invalid bars: {errors}")


def ingest(source, root="data", kind="oanda", minutes=1):
    if (
        kind not in {"oanda", "canonical", "ohlcv"}
        or type(minutes) is not int
        or not 1 <= minutes <= 1440
    ):
        raise ValueError("Invalid input kind or timeframe")
    if kind == "oanda" and minutes != 1:
        raise ValueError("OANDA raw CSV contract is one-minute candles")
    root = Path(root).resolve()
    records = archive_sources(source, root)
    input_columns = _source_schema(records, kind)
    snapshot = identity(
        {
            "version": DATA_VERSION,
            "kind": kind,
            "minutes": minutes,
            "files": [(r["relative_path"], r["sha256"]) for r in records],
        }
    )
    dest = root / "market" / f"{minutes}m" / snapshot[:16]
    manifest_path = dest / "manifest.json"
    with connect(root) as con:
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text())
            _verify_files(manifest)
            _register_market(con, manifest, manifest_path)
            return manifest
        dest.mkdir(parents=True, exist_ok=True)
        paths = ",".join(sql_string(r["path"]) for r in records)
        # One scan into a disk-backed staging database; bounded DuckDB memory/spill.
        stage = root / "tmp" / f"ingest-{snapshot[:16]}.duckdb"
        con.execute(f"ATTACH {sql_string(stage)} AS stage")
        parquet = Path(records[0]["path"]).suffix.lower() == ".parquet"
        reader = (
            f"read_parquet([{paths}],union_by_name=true,filename=true,hive_partitioning=false)"
            if parquet
            else f"read_csv([{paths}],header=true,all_varchar=true,union_by_name=true,filename=true)"
        )
        short_quotes = [
            f"{s}_{p}" for s in ("bid", "ask") for p in ("o", "h", "l", "c")
        ]
        market_columns = (
            {
                "oanda": OANDA_REQUIRED,
                "canonical": CANONICAL_REQUIRED,
                "ohlcv": OHLCV_REQUIRED,
            }[kind]
            | set(
                short_quotes
                if kind == "oanda"
                else QUOTES + (short_quotes if kind == "ohlcv" else [])
            )
            | {"is_complete"}
        )
        selected = sorted(input_columns & market_columns)
        expressions = [f'CAST("{name}" AS VARCHAR) AS "{name}"' for name in selected]
        con.execute(
            f"CREATE OR REPLACE TEMP VIEW raw_input AS SELECT {','.join(expressions)}, filename FROM {reader}"
        )
        fields = {row[0] for row in con.execute("DESCRIBE raw_input").fetchall()}
        time_col = "bar_open_time" if kind == "canonical" else "time"
        timezone_pattern = "[T ][0-9]{2}:[0-9]{2}.*(Z|[+-][0-9]{2}(:?[0-9]{2})?)$"
        stamp_check = (
            f"NOT coalesce(regexp_matches({time_col}, '{timezone_pattern}'), false)"
        )
        if kind == "canonical":
            stamp_check += f" OR NOT coalesce(regexp_matches(bar_close_time, '{timezone_pattern}'), false)"
        invalid_complete = (
            " OR lower(coalesce(is_complete,'')) NOT IN ('true','false','1','0')"
            if "is_complete" in fields
            else ""
        )
        # This light preflight also rejects ambiguous booleans and local timestamps.
        invalid = con.execute(
            f"SELECT count(*) FROM raw_input WHERE {stamp_check}{invalid_complete}"
        ).fetchone()[0]
        if invalid:
            raise ValueError(
                f"{invalid} rows have invalid completeness or timezone-free timestamps"
            )
        mapping = {}
        for side in ("", "bid_", "ask_"):
            for point, short in zip(
                ("open", "high", "low", "close"), ("o", "h", "l", "c")
            ):
                source_col = (
                    (("mid_" if side == "" else side) + short)
                    if kind == "oanda"
                    else side + point
                )
                if kind == "ohlcv" and side and source_col not in fields:
                    source_col = side + short
                mapping[side + point] = (
                    f"CAST({source_col} AS DOUBLE)"
                    if source_col in fields
                    else "NULL::DOUBLE"
                )
        prices = ",".join(f"{expr} AS {name}" for name, expr in mapping.items())
        complete = (
            "lower(is_complete) IN ('true','1')" if "is_complete" in fields else "true"
        )
        source_bars = "1::INTEGER"
        if kind == "ohlcv":
            invalid_count = con.execute(
                "SELECT count(*) FROM raw_input WHERE try_cast(n_bars AS DOUBLE) IS NULL OR NOT isfinite(try_cast(n_bars AS DOUBLE)) OR try_cast(n_bars AS DOUBLE) <= 0 OR try_cast(n_bars AS DOUBLE)>? OR try_cast(n_bars AS DOUBLE)!=floor(try_cast(n_bars AS DOUBLE))",
                [minutes],
            ).fetchone()[0]
            if invalid_count:
                raise ValueError("Invalid OHLCV n_bars count")
            complete = f"({complete}) AND CAST(n_bars AS INTEGER)={minutes}"
            source_bars = "CAST(n_bars AS INTEGER)"
        close = (
            f"CAST({time_col} AS TIMESTAMPTZ)+INTERVAL '{minutes} minutes'"
            if kind != "canonical"
            else "CAST(bar_close_time AS TIMESTAMPTZ)"
        )
        complete_exists = con.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_catalog='stage' AND table_name='complete'"
        ).fetchone()[0]
        if complete_exists:
            print("Resuming content-identified validated staging…", flush=True)
            _validate(con, "stage.complete", minutes)
            if "source_bars" not in {
                r[0] for r in con.execute("DESCRIBE stage.complete").fetchall()
            }:
                con.execute(
                    "ALTER TABLE stage.complete ADD COLUMN source_bars INTEGER DEFAULT 1"
                )
            total, incomplete = con.execute(
                f"SELECT count(*),count(*) FILTER(WHERE NOT ({complete})) FROM raw_input"
            ).fetchone()
        else:
            print("Normalizing raw CSVs into disk-backed staging…", flush=True)
            con.execute(f"""CREATE OR REPLACE TABLE stage.normalized AS SELECT trim(instrument) AS instrument,
                CAST({time_col} AS TIMESTAMPTZ) AS bar_open_time, {close} AS bar_close_time,
                {prices}, CAST(volume AS DOUBLE) AS volume,
                {complete} AS is_complete, {source_bars} AS source_bars, filename AS source_file FROM raw_input""")
            _validate(con, "stage.normalized", minutes)
            total, incomplete = con.execute(
                "SELECT count(*),count(*) FILTER(WHERE NOT is_complete) FROM stage.normalized"
            ).fetchone()
            payload = (
                "struct_pack("
                + ",".join(f"{p}:={p}" for p in PRICES + ["volume"])
                + ")"
            )
            con.execute(f"""CREATE OR REPLACE TABLE stage.complete AS SELECT *,sha256(CAST({payload} AS VARCHAR)) AS payload_hash
                FROM stage.normalized WHERE is_complete""")
            con.execute("DROP TABLE stage.normalized")
        complete_count = total - incomplete
        if not complete_count:
            raise ValueError("Source has no complete bars")
        if (
            kind == "ohlcv"
            and con.execute(
                "SELECT count(*) FROM stage.complete WHERE epoch(bar_open_time)%? != 0",
                [minutes * 60],
            ).fetchone()[0]
        ):
            raise ValueError("OHLCV candles must align to the declared UTC timeframe")
        if (
            minutes == 1
            and con.execute(
                "SELECT count(*) FROM stage.complete WHERE epoch(bar_open_time)%60 != 0"
            ).fetchone()[0]
        ):
            raise ValueError(
                "One-minute source candles must start on exact UTC minute boundaries"
            )
        instruments = [
            row[0]
            for row in con.execute(
                "SELECT DISTINCT instrument FROM stage.complete ORDER BY 1"
            ).fetchall()
        ]
        files = []
        conflicts = 0
        print("Deduplicating one instrument at a time…", flush=True)
        for instrument in instruments:
            # Partition before expensive distinct/window operations. This also
            # bounds memory when the archive contains millions of distinct keys.
            con.execute(
                "CREATE OR REPLACE TEMP TABLE instrument_input AS SELECT * FROM stage.complete WHERE instrument=?",
                [instrument],
            )
            conflicts += con.execute("""SELECT count(*) FROM (SELECT bar_open_time FROM instrument_input
                GROUP BY ALL HAVING count(DISTINCT payload_hash)>1)""").fetchone()[0]
            con.execute("""CREATE OR REPLACE TEMP TABLE clean AS SELECT * EXCLUDE(source_file,payload_hash,rn)
                FROM (SELECT *,row_number() OVER (PARTITION BY bar_open_time ORDER BY
                    (bid_open IS NOT NULL) DESC,source_file ASC,payload_hash ASC) AS rn FROM instrument_input) WHERE rn=1""")
            con.execute("DROP TABLE instrument_input")
            overlap = con.execute("""SELECT count(*) FROM (SELECT bar_open_time,lag(bar_close_time) OVER
                (ORDER BY bar_open_time) AS previous_close FROM clean) WHERE previous_close>bar_open_time""").fetchone()[
                0
            ]
            if overlap:
                raise ValueError("Overlapping candles are not allowed")
            path = dest / f"{instrument}.parquet"
            con.execute(
                f"COPY (SELECT * FROM clean ORDER BY bar_open_time) TO {sql_string(path)} (FORMAT PARQUET,COMPRESSION ZSTD)"
            )
            files.append(_file_record(con, path, instrument))
            con.execute("DROP TABLE clean")
            print(f"Cleaned {instrument}: {files[-1]['rows']:,} candles", flush=True)
        manifest = {
            "snapshot_id": snapshot,
            "data_version": DATA_VERSION,
            "timeframe_minutes": minutes,
            "kind": "market",
            "source_kind": kind,
            "input_format": "parquet" if parquet else "csv",
            "ignored_columns": sorted(input_columns - market_columns),
            "data_producer_revision": "unknown; not inferred from the inspected source code commit",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "raw_files": records,
            "volume_semantics": "OANDA quote/tick activity; used as market-volume proxy"
            if kind == "oanda"
            else "source-provided activity; used as market-volume proxy",
            "quality": {
                "input_rows": total,
                "incomplete_rows_dropped": incomplete,
                "duplicate_complete_rows_removed": complete_count
                - sum(f["rows"] for f in files),
                "conflicting_duplicate_keys": conflicts,
                "duplicate_policy": "complete first; observed bid/ask first; source filename then payload SHA256 ascending",
            },
            "files": files,
        }
        write_json(manifest_path, manifest)
        _register_market(con, manifest, manifest_path)
        # Remove large staging tables after successful export; keep failure state for diagnosis.
        con.execute("DETACH stage")
        stage.unlink()
        return manifest


def _file_record(con, path, instrument):
    rows, start, end, quoted = con.execute(
        "SELECT count(*), min(bar_open_time),max(bar_close_time),count(bid_open) FROM read_parquet(?)",
        [str(path)],
    ).fetchone()
    return {
        "instrument": instrument,
        "path": str(path.resolve()),
        "sha256": file_hash(path),
        "rows": rows,
        "start": start.isoformat() if start is not None else None,
        "end": end.isoformat() if end is not None else None,
        "quoted_bars": quoted,
    }


def _verify_files(manifest):
    for record in manifest["files"]:
        if file_hash(record["path"]) != record["sha256"]:
            raise ValueError(f"Snapshot file changed: {record['path']}")


def _register_market(con, manifest, manifest_path):
    minutes = manifest["timeframe_minutes"]
    register(con, "market", minutes, manifest["snapshot_id"], manifest_path)
    parquet_view(con, f"bars_{minutes}m", [r["path"] for r in manifest["files"]])


def aggregate(root="data", minutes=60):
    if type(minutes) is not int or not 2 <= minutes <= 1440 or 1440 % minutes:
        raise ValueError(
            "Aggregation timeframe must divide one UTC day and exceed one minute"
        )
    root = Path(root).resolve()
    with connect(root) as con:
        source = dataset(con, "market", 1)
        _verify_files(source)
        snapshot = identity(
            {
                "version": DATA_VERSION,
                "source": source["snapshot_id"],
                "minutes": minutes,
                "complete_buckets_only": True,
            }
        )
        dest = root / "market" / f"{minutes}m" / snapshot[:16]
        manifest_path = dest / "manifest.json"
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text())
            _verify_files(manifest)
            _register_market(con, manifest, manifest_path)
            return manifest
        dest.mkdir(parents=True, exist_ok=True)
        files = []
        partial = 0
        for record in source["files"]:
            fields = [
                "instrument",
                f"time_bucket(INTERVAL '{minutes} minutes',bar_open_time) AS bar_open_time",
                f"time_bucket(INTERVAL '{minutes} minutes',bar_open_time)+INTERVAL '{minutes} minutes' AS bar_close_time",
            ]
            quoted = "count(bid_open)=count(*)"
            for side in ("", "bid_", "ask_"):
                for point, expr in [
                    ("open", f"arg_min({side}open,bar_open_time)"),
                    ("high", f"max({side}high)"),
                    ("low", f"min({side}low)"),
                    ("close", f"arg_max({side}close,bar_open_time)"),
                ]:
                    if side:
                        expr = f"CASE WHEN {quoted} THEN {expr} END"
                    fields.append(f"{expr} AS {side}{point}")
            fields.extend(
                [
                    "sum(volume) AS volume",
                    "count(*)::INTEGER AS source_bars",
                    "true AS is_complete",
                ]
            )
            con.execute(
                f"CREATE OR REPLACE TEMP TABLE aggregated AS SELECT {','.join(fields)} FROM read_parquet(?) GROUP BY instrument, time_bucket(INTERVAL '{minutes} minutes',bar_open_time)",
                [record["path"]],
            )
            partial += con.execute(
                "SELECT count(*) FROM aggregated WHERE source_bars != ?", [minutes]
            ).fetchone()[0]
            path = dest / f"{record['instrument']}.parquet"
            con.execute(
                f"COPY (SELECT * FROM aggregated WHERE source_bars={minutes} ORDER BY bar_open_time) TO {sql_string(path)} (FORMAT PARQUET, COMPRESSION ZSTD)"
            )
            info = _file_record(con, path, record["instrument"])
            if info["rows"]:
                files.append(info)
            else:
                path.unlink()
        if not files:
            raise ValueError("No complete aggregation buckets")
        manifest = {
            "snapshot_id": snapshot,
            "data_version": DATA_VERSION,
            "kind": "market",
            "timeframe_minutes": minutes,
            "parent_snapshot_id": source["snapshot_id"],
            "source_kind": source["source_kind"],
            "volume_semantics": source["volume_semantics"],
            "files": files,
            "quality": {
                "partial_buckets_dropped": partial,
                "gap_filling": False,
                "quote_policy": "all minutes quoted, otherwise configured mid-price spread",
            },
        }
        write_json(manifest_path, manifest)
        _register_market(con, manifest, manifest_path)
        return manifest
