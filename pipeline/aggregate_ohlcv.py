from pathlib import Path

import duckdb


def aggregate_ohlcv_data(
    db_path: str | Path = "data/metadata.duckdb",
    parquet_5m_path: str | Path = "data/parquet/ohlcv_5m.parquet",
    parquet_1h_path: str | Path = "data/parquet/ohlcv_1h.parquet",
) -> None:
    """Aggregate clean 1-minute OHLCV data from main.all_data into 5-minute

    and 1-hour OHLCV tables in DuckDB, and export them to Parquet files.

    Args:
        db_path: Path to the DuckDB metadata/database file.
        parquet_5m_path: Path to output Parquet file for 5-minute aggregated data.
        parquet_1h_path: Path to output Parquet file for 1-hour aggregated data.
    """
    database_path = Path(db_path)
    if not database_path.exists():
        print(f"Database file not found at {database_path.resolve()}. Please load and clean data first.")
        return

    print(f"Connecting to DuckDB at {database_path.resolve()}...")
    conn = duckdb.connect(str(database_path))

    # Check if table exists
    table_check = conn.execute(
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'main' AND table_name = 'all_data';"
    ).fetchone()[0]

    if table_check == 0:
        print("Table 'main.all_data' does not exist in DuckDB.")
        conn.close()
        return

    # Dynamically find the exact column names (case-insensitive search)
    cols = conn.execute(
        "SELECT column_name FROM information_schema.columns WHERE table_schema = 'main' AND table_name = 'all_data';"
    ).fetchall()
    col_names_lower = {col[0].lower(): col[0] for col in cols}

    required = ["instrument", "time", "mid_o", "mid_h", "mid_l", "mid_c", "volume"]
    resolved_cols = {}
    for req in required:
        if req not in col_names_lower:
            print(f"-> Error: Required column '{req}' not found in main.all_data columns: {list(col_names_lower.values())}")
            conn.close()
            return
        resolved_cols[req] = col_names_lower[req]

    inst_col = f'"{resolved_cols["instrument"]}"'
    time_col = f'"{resolved_cols["time"]}"'
    open_col = f'"{resolved_cols["mid_o"]}"'
    high_col = f'"{resolved_cols["mid_h"]}"'
    low_col = f'"{resolved_cols["mid_l"]}"'
    close_col = f'"{resolved_cols["mid_c"]}"'
    volume_col = f'"{resolved_cols["volume"]}"'

    try:
        # 1. Aggregate to 5-minute OHLCV table
        print("Aggregating 1-minute data into 5-minute OHLCV table (main.ohlcv_5m)...")
        conn.execute(
            f"""
            CREATE OR REPLACE TABLE main.ohlcv_5m AS 
            SELECT 
                {inst_col} AS instrument,
                time_bucket(INTERVAL '5 minutes', CAST({time_col} AS TIMESTAMP)) AS time,
                arg_min(CAST({open_col} AS DOUBLE), CAST({time_col} AS TIMESTAMP)) AS "open",
                MAX(CAST({high_col} AS DOUBLE)) AS high,
                MIN(CAST({low_col} AS DOUBLE)) AS low,
                arg_max(CAST({close_col} AS DOUBLE), CAST({time_col} AS TIMESTAMP)) AS close,
                SUM(CAST({volume_col} AS DOUBLE)) AS volume
            FROM main.all_data
            GROUP BY {inst_col}, time_bucket(INTERVAL '5 minutes', CAST({time_col} AS TIMESTAMP))
            ORDER BY {inst_col}, time;
            """
        )
        count_5m = conn.execute("SELECT COUNT(*) FROM main.ohlcv_5m;").fetchone()[0]
        
        target_5m = Path(parquet_5m_path)
        target_5m.parent.mkdir(parents=True, exist_ok=True)
        conn.execute(f"COPY main.ohlcv_5m TO '{target_5m.as_posix()}' (FORMAT PARQUET);")
        print(f"-> Created main.ohlcv_5m with {count_5m} rows. Saved to {target_5m}")

        # 2. Aggregate to 1-hour OHLCV table
        print("Aggregating 1-minute data into 1-hour OHLCV table (main.ohlcv_1h)...")
        conn.execute(
            f"""
            CREATE OR REPLACE TABLE main.ohlcv_1h AS 
            SELECT 
                {inst_col} AS instrument,
                time_bucket(INTERVAL '1 hour', CAST({time_col} AS TIMESTAMP)) AS time,
                arg_min(CAST({open_col} AS DOUBLE), CAST({time_col} AS TIMESTAMP)) AS "open",
                MAX(CAST({high_col} AS DOUBLE)) AS high,
                MIN(CAST({low_col} AS DOUBLE)) AS low,
                arg_max(CAST({close_col} AS DOUBLE), CAST({time_col} AS TIMESTAMP)) AS close,
                SUM(CAST({volume_col} AS DOUBLE)) AS volume
            FROM main.all_data
            GROUP BY {inst_col}, time_bucket(INTERVAL '1 hour', CAST({time_col} AS TIMESTAMP))
            ORDER BY {inst_col}, time;
            """
        )
        count_1h = conn.execute("SELECT COUNT(*) FROM main.ohlcv_1h;").fetchone()[0]

        target_1h = Path(parquet_1h_path)
        target_1h.parent.mkdir(parents=True, exist_ok=True)
        conn.execute(f"COPY main.ohlcv_1h TO '{target_1h.as_posix()}' (FORMAT PARQUET);")
        print(f"-> Created main.ohlcv_1h with {count_1h} rows. Saved to {target_1h}")

    except (duckdb.Error, OSError) as e:
        print(f"-> Error during OHLCV aggregation: {e}")

    conn.close()
    print("OHLCV aggregation process completed successfully.")


if __name__ == "__main__":
    aggregate_ohlcv_data()
