import csv
import hashlib
from pathlib import Path

from .catalog import FEATURE_VERSION, TREND_COLUMNS

REQUIRED = {"instrument", "bar_open_time", "bar_close_time", "open", "high", "low", "close", "volume", "is_complete"}
QUOTES = [f"{side}_{point}" for side in ("bid", "ask") for point in ("open", "high", "low", "close")]


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def prepare_features(connection, path, timeframe_minutes, profile="starter", feature_dir=None):
    """One input snapshot per DB; unchanged snapshots reuse feature tables."""
    path = Path(path).resolve()
    if profile not in {"starter", "legacy", "imported"}:
        raise ValueError("Unknown feature profile")
    if path.suffix != ".parquet":
        with path.open(newline="", encoding="utf-8") as stream:
            original_header = next(csv.reader(stream), [])
        if len(original_header) != len(set(original_header)):
            raise ValueError("Duplicate CSV column names")
    connection.execute("SET TimeZone='UTC'")
    escaped = str(path).replace("'", "''")
    reader = f"read_parquet('{escaped}')" if path.suffix == ".parquet" else f"read_csv('{escaped}', header=true, all_varchar=true)"
    connection.execute("CREATE OR REPLACE TEMP VIEW raw_csv AS SELECT * FROM " + reader)
    header = [row[0] for row in connection.execute("DESCRIBE raw_csv").fetchall()]
    if len(header) != len(set(header)) or not REQUIRED.issubset(header):
        raise ValueError(f"CSV needs unique columns including {sorted(REQUIRED)}")
    quote_count = sum(name in header for name in QUOTES)
    if quote_count not in (0, len(QUOTES)):
        raise ValueError("Provide all eight bid/ask OHLC columns or none")
    snapshot = file_hash(path)
    from .feature_profiles import computation_hash, attach_profile, rebuild_view, export_store
    version = FEATURE_VERSION + ":" + profile + ":" + computation_hash()[:16]
    connection.execute("CREATE TABLE IF NOT EXISTS feature_snapshot (data_hash VARCHAR, feature_version VARCHAR)")
    old = connection.execute("SELECT data_hash, feature_version FROM feature_snapshot").fetchone()
    reused = old == (snapshot, version)
    if not reused:
        connection.execute("BEGIN")
        try:
            invalid = connection.execute("""
                SELECT count(*) FROM raw_csv WHERE
                instrument IS NULL OR trim(instrument) = '' OR
                NOT coalesce(regexp_matches(CAST(bar_open_time AS VARCHAR), '[T ][0-9]{2}:[0-9]{2}.*(Z|[+-][0-9]{2}(:?[0-9]{2})?)$'), false) OR
                NOT coalesce(regexp_matches(CAST(bar_close_time AS VARCHAR), '[T ][0-9]{2}:[0-9]{2}.*(Z|[+-][0-9]{2}(:?[0-9]{2})?)$'), false) OR
                lower(coalesce(CAST(is_complete AS VARCHAR), '')) NOT IN ('true', '1')
            """).fetchone()[0]
            if invalid:
                raise ValueError("Require nonempty instruments, timezone-aware timestamps and complete bars")
            quote_sql = ", ".join(f"CAST({name} AS DOUBLE) AS {name}" if quote_count else f"NULL::DOUBLE AS {name}" for name in QUOTES)
            n_bars_sql = "CAST(n_bars AS BIGINT)" if "n_bars" in header else str(timeframe_minutes)
            connection.execute(f"""CREATE OR REPLACE TABLE bars AS SELECT
                instrument, CAST(bar_open_time AS TIMESTAMPTZ) AS bar_open_time,
                CAST(bar_close_time AS TIMESTAMPTZ) AS bar_close_time,
                CAST(open AS DOUBLE) AS open, CAST(high AS DOUBLE) AS high,
                CAST(low AS DOUBLE) AS low, CAST(close AS DOUBLE) AS close,
                CAST(volume AS DOUBLE) AS volume, {n_bars_sql} AS n_bars, {quote_sql} FROM raw_csv""")
            _validate_bars(connection, bool(quote_count))
            connection.execute("""CREATE OR REPLACE TABLE features_core AS
                WITH tr AS (SELECT *, greatest(high-low,
                    abs(high-lag(close, 1, close) OVER w), abs(low-lag(close, 1, close) OVER w)) AS true_range
                    FROM bars WINDOW w AS (PARTITION BY instrument ORDER BY bar_open_time))
                SELECT *, CASE WHEN count(true_range) OVER w = 14 THEN avg(true_range) OVER w END AS atr_sma_14
                FROM tr WINDOW w AS (PARTITION BY instrument ORDER BY bar_open_time ROWS BETWEEN 13 PRECEDING AND CURRENT ROW)
            """)
            connection.execute("""CREATE OR REPLACE TABLE features_trend AS
                WITH ma AS (SELECT instrument, bar_open_time, bar_close_time, close, atr_sma_14,
                    CASE WHEN count(close) OVER w6 = 6 THEN avg(close) OVER w6 END AS sma_6,
                    CASE WHEN count(close) OVER w24 = 24 THEN avg(close) OVER w24 END AS sma_24
                    FROM features_core WINDOW
                    w6 AS (PARTITION BY instrument ORDER BY bar_open_time ROWS BETWEEN 5 PRECEDING AND CURRENT ROW),
                    w24 AS (PARTITION BY instrument ORDER BY bar_open_time ROWS BETWEEN 23 PRECEDING AND CURRENT ROW))
                SELECT instrument, bar_open_time, bar_close_time, sma_6, sma_24,
                    CASE WHEN sma_24 IS NOT NULL THEN sign(sma_6-sma_24) END AS sma_alignment_6_24,
                    CASE WHEN lag(sma_24) OVER w IS NOT NULL THEN
                        sma_6 > sma_24 AND lag(sma_6) OVER w <= lag(sma_24) OVER w END AS sma_cross_up_6_24,
                    CASE WHEN lag(sma_24) OVER w IS NOT NULL THEN
                        sma_6 < sma_24 AND lag(sma_6) OVER w >= lag(sma_24) OVER w END AS sma_cross_down_6_24,
                    (close-sma_24)/nullif(atr_sma_14, 0) AS close_sma24_distance_atr
                FROM ma WINDOW w AS (PARTITION BY instrument ORDER BY bar_open_time)
            """)
            attach_profile(connection, profile, header, timeframe_minutes)
            connection.execute("DELETE FROM feature_snapshot")
            connection.execute("INSERT INTO feature_snapshot VALUES (?, ?)", [snapshot, version])
            connection.execute("COMMIT")
        except Exception:
            connection.execute("ROLLBACK")
            raise
    invalid_duration = connection.execute("SELECT count(*) FROM bars WHERE epoch(bar_close_time-bar_open_time) != ?", [timeframe_minutes * 60]).fetchone()[0]
    if invalid_duration:
        raise ValueError("Bar duration does not match strategy timeframe_minutes")
    rebuild_view(connection)
    observed, total = connection.execute("SELECT count(bid_open), count(*) FROM bars").fetchone()
    price_source = "bid_ask" if observed == total else "mixed_bid_ask_and_mid" if observed else "mid_with_configured_spread"
    exports = export_store(connection, feature_dir, snapshot, version) if feature_dir else []
    return {"data_hash": snapshot, "feature_version": version, "feature_profile": profile,
            "feature_cache_reused": reused, "price_source": price_source, "parquet_exports": exports}


def _validate_bars(connection, has_quotes):
    if connection.execute("SELECT count(*) FROM bars").fetchone()[0] == 0:
        raise ValueError("CSV has no bars")
    if connection.execute("SELECT count(*) FROM bars WHERE instrument IS NULL OR trim(instrument)='' OR bar_open_time IS NULL OR bar_close_time IS NULL").fetchone()[0]:
        raise ValueError("Missing instrument or timestamps")
    for prefix in ([""] + (["bid_", "ask_"] if has_quotes else [])):
        o, h, l, c = [prefix + name for name in ("open", "high", "low", "close")]
        checks = [f"{x} IS NULL OR NOT isfinite({x}) OR {x} <= 0" for x in (o, h, l, c)]
        checks += [f"{l} > {h}", f"{o} < {l}", f"{o} > {h}", f"{c} < {l}", f"{c} > {h}"]
        where = "(" + " OR ".join(checks) + ")"
        if prefix:
            where = f"{o} IS NOT NULL AND " + where
        if connection.execute("SELECT count(*) FROM bars WHERE " + where).fetchone()[0]:
            raise ValueError(f"Invalid {prefix or 'mid '}OHLC values")
    if has_quotes:
        score = "+".join(f"({name} IS NOT NULL)::INTEGER" for name in QUOTES)
        if connection.execute(f"SELECT count(*) FROM bars WHERE ({score}) NOT IN (0, 8)").fetchone()[0]:
            raise ValueError("Each bar must have all eight Bid/Ask values or none")
    if connection.execute("SELECT count(*) FROM bars WHERE volume IS NULL OR NOT isfinite(volume) OR volume < 0 OR bar_close_time <= bar_open_time").fetchone()[0]:
        raise ValueError("Invalid volume or bar timestamps")
    if connection.execute("SELECT count(*) FROM (SELECT instrument, bar_open_time FROM bars GROUP BY ALL HAVING count(*) > 1)").fetchone()[0]:
        raise ValueError("Duplicate instrument/bar_open_time")
    if connection.execute("SELECT count(*) FROM (SELECT bar_open_time, lag(bar_close_time) OVER (PARTITION BY instrument ORDER BY bar_open_time) AS previous_close FROM bars) WHERE previous_close > bar_open_time").fetchone()[0]:
        raise ValueError("Overlapping bars")
    if has_quotes and connection.execute("SELECT count(*) FROM bars WHERE " + " OR ".join(f"ask_{x} < bid_{x}" for x in ("open", "high", "low", "close"))).fetchone()[0]:
        raise ValueError("Negative bid/ask spread")
