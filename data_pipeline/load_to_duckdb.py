from pathlib import Path

import duckdb


def ensure_data_dirs() -> None:
    """Ensure necessary data directories exist."""
    Path("data").mkdir(parents=True, exist_ok=True)


def load_csvs_to_duckdb(
    csv_dir: str | Path = "data/raw_csv",
    db_path: str | Path = "data/metadata.duckdb",
    parquet_output: str | Path = "data/raw_data.parquet",
) -> None:
    """Read all raw CSV files, ingest them into DuckDB, and export to a parquet file.

    Args:
        csv_dir: Directory containing raw CSV files.
        db_path: Path to the DuckDB metadata/database file.
        parquet_output: Path to export the combined parquet file.
    """
    ensure_data_dirs()
    source_csv_dir = Path(csv_dir)

    csv_files = list(source_csv_dir.rglob("*.csv"))
    if not csv_files:
        print(f"No CSV files found in {source_csv_dir.resolve()}")
        return

    print(f"Found {len(csv_files)} CSV files to process.")

    # Connect to DuckDB (creates metadata.duckdb if it doesn't exist)
    conn = duckdb.connect(str(db_path))

    # Pattern to glob all CSVs recursively
    glob_pattern = str(source_csv_dir / "**" / "*.csv")

    print(f"Ingesting CSV data into DuckDB from: {glob_pattern}")

    # Create or replace the raw_data table directly using DuckDB's optimized CSV reader
    conn.execute(
        f"""
        CREATE OR REPLACE TABLE raw_data AS 
        SELECT * 
        FROM read_csv(
            '{glob_pattern}',
            header=true,
            filename=true,
            union_by_name=true
        );
        """
    )

    row_count = conn.execute("SELECT COUNT(*) FROM raw_data;").fetchone()[0]
    print(f"Successfully loaded {row_count} rows into DuckDB table 'raw_data'.")

    # Export to Parquet file
    parquet_path = Path(parquet_output)
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Exporting table 'raw_data' to parquet file: {parquet_path.resolve()}")
    conn.execute(f"COPY raw_data TO '{parquet_path}' (FORMAT PARQUET);")

    conn.close()
    print("DuckDB ingestion and parquet export completed successfully.")


if __name__ == "__main__":
    load_csvs_to_duckdb()
