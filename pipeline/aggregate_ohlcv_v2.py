"""Aggregate clean 1-minute OHLCV bars into 5-minute and 1-hour bars.

Timestamps are read as UTC and bucketed on UTC boundaries. Every output bar
carries ``n_bars``, the number of 1-minute bars it was built from, so partial
bars (gaps, session edges) can be identified downstream.
"""

from pathlib import Path

import duckdb

REQUIRED_COLUMNS = ("instrument", "time", "mid_o", "mid_h", "mid_l", "mid_c", "volume")


def _sql_literal(value: str) -> str:
    """Return ``value`` as a SQL string literal with single quotes escaped."""
    return "'" + value.replace("'", "''") + "'"


def _resolve_columns(conn: duckdb.DuckDBPyConnection) -> dict[str, str]:
    """Map each required column to its actual name in ``main.all_data``.

    Matching is case-insensitive. Raises ValueError if a column is missing.
    """
    rows = conn.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = 'main' AND table_name = 'all_data';"
    ).fetchall()
    actual = {name.lower(): name for (name,) in rows}
    missing = [col for col in REQUIRED_COLUMNS if col not in actual]
    if missing:
        raise ValueError(f"Required columns {missing} not found in main.all_data (have {sorted(actual.values())})")
    return {col: actual[col] for col in REQUIRED_COLUMNS}


def _build_bars(conn: duckdb.DuckDBPyConnection, table: str, interval: str, cols: dict[str, str]) -> None:
    """Create ``table`` with OHLCV bars of the given interval from the 1-minute data."""

    def q(name: str) -> str:
        return f'"{cols[name]}"'

    conn.execute(
        f"""
        CREATE OR REPLACE TABLE {table} AS
        SELECT
            instrument,
            bucket AS time,
            arg_min(mid_o, ts) AS open,
            MAX(mid_h) AS high,
            MIN(mid_l) AS low,
            arg_max(mid_c, ts) AS close,
            SUM(volume) AS volume,
            COUNT(*) AS n_bars
        FROM (
            SELECT
                {q("instrument")} AS instrument,
                CAST({q("time")} AS TIMESTAMP) AS ts,
                CAST({q("mid_o")} AS DOUBLE) AS mid_o,
                CAST({q("mid_h")} AS DOUBLE) AS mid_h,
                CAST({q("mid_l")} AS DOUBLE) AS mid_l,
                CAST({q("mid_c")} AS DOUBLE) AS mid_c,
                CAST({q("volume")} AS DOUBLE) AS volume,
                time_bucket(INTERVAL '{interval}', CAST({q("time")} AS TIMESTAMP)) AS bucket
            FROM main.all_data
        )
        GROUP BY instrument, bucket
        ORDER BY instrument, bucket;
        """
    )


def aggregate_ohlcv_data(
    db_path: str | Path = "data/metadata.duckdb",
    parquet_5m_path: str | Path = "data/parquet/ohlcv_5m.parquet",
    parquet_1h_path: str | Path = "data/parquet/ohlcv_1h.parquet",
) -> dict[str, int]:
    """Build ``main.ohlcv_5m`` and ``main.ohlcv_1h`` from ``main.all_data``.

    Args:
        db_path: Path to the DuckDB database file.
        parquet_5m_path: Path of the 5-minute Parquet export.
        parquet_1h_path: Path of the 1-hour Parquet export.

    Returns:
        Row count per output table.

    Raises:
        FileNotFoundError: If the database file does not exist.
        ValueError: If ``main.all_data`` or a required column is missing.
    """
    database_path = Path(db_path)
    if not database_path.exists():
        raise FileNotFoundError(f"Database file not found at {database_path.resolve()}. Load and clean data first.")

    outputs = [
        ("main.ohlcv_5m", "5 minutes", Path(parquet_5m_path)),
        ("main.ohlcv_1h", "1 hour", Path(parquet_1h_path)),
    ]

    conn = duckdb.connect(str(database_path))
    counts: dict[str, int] = {}
    try:
        conn.execute("SET TimeZone = 'UTC'")
        table_exists = conn.execute(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema = 'main' AND table_name = 'all_data';"
        ).fetchone()[0]
        if table_exists == 0:
            raise ValueError("Table 'main.all_data' does not exist; run the load and clean steps first.")

        cols = _resolve_columns(conn)
        for table, interval, target in outputs:
            _build_bars(conn, table, interval, cols)
            target.parent.mkdir(parents=True, exist_ok=True)
            conn.execute(f"COPY {table} TO {_sql_literal(target.as_posix())} (FORMAT PARQUET);")
            counts[table] = int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
            print(f"-> Created {table} with {counts[table]} rows; saved to {target}")
    finally:
        conn.close()

    return counts


if __name__ == "__main__":
    aggregate_ohlcv_data()

