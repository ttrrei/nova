from pathlib import Path

import duckdb


def ensure_data_dirs() -> None:
    """Ensure necessary data directories exist."""
    Path("data").mkdir(parents=True, exist_ok=True)
    Path("data/parquet").mkdir(parents=True, exist_ok=True)


def load_csvs_to_duckdb(
    csv_dir: str | Path = "data/raw_csv",
    db_path: str | Path = "data/metadata.duckdb",
    parquet_output_path: str | Path = "data/parquet/all_data.parquet",
) -> None:
    """Load all raw CSV files combined into one and only one unified table

    in DuckDB, and export the combined dataset to a single Parquet file.

    Args:
        csv_dir: Directory containing raw CSV files.
        db_path: Path to the DuckDB metadata/database file.
        parquet_output_path: Path to the single output Parquet file.
    """
    ensure_data_dirs()
    source_csv_dir = Path(csv_dir)
    target_parquet = Path(parquet_output_path)
    target_parquet.parent.mkdir(parents=True, exist_ok=True)

    csv_glob = (source_csv_dir / "**" / "*.csv").as_posix()
    csv_files = list(source_csv_dir.rglob("*.csv"))

    if not csv_files:
        print(f"No CSV files found in {source_csv_dir.resolve()}")
        return

    print(f"Found {len(csv_files)} CSV files to combine into a single table.")

    # Connect to DuckDB metadata database
    conn = duckdb.connect(str(db_path))

    # Ensure a metadata tracking table exists
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS loaded_tables (
            table_name VARCHAR,
            csv_path VARCHAR,
            parquet_path VARCHAR,
            row_count BIGINT,
            loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    try:
        table_name = "main.all_data"
        print(f"Loading and uniting all CSV files into table '{table_name}' ...")

        # Create or replace single unified table using glob pattern and union_by_name
        conn.execute(
            f"""
            CREATE OR REPLACE TABLE {table_name} AS 
            SELECT * 
            FROM read_csv(
                '{csv_glob}',
                header=true,
                auto_detect=true,
                union_by_name=true
            );
            """
        )

        row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name};").fetchone()[0]

        # Export the unified table to a single Parquet file
        print(f"Exporting unified table to Parquet: {target_parquet}")
        conn.execute(f"COPY {table_name} TO '{target_parquet.as_posix()}' (FORMAT PARQUET);")

        # Record metadata
        conn.execute(
            """
            INSERT INTO loaded_tables (table_name, csv_path, parquet_path, row_count)
            VALUES (?, ?, ?, ?);
            """,
            (table_name, str(source_csv_dir), str(target_parquet), row_count),
        )

        print(f"-> Done! Successfully loaded {row_count} total rows into '{table_name}' and saved to {target_parquet}")

    except (duckdb.Error, OSError) as e:
        print(f"-> Error processing CSV files: {e}")

    conn.close()
    print("Unified CSV loading and Parquet export process completed.")


if __name__ == "__main__":
    load_csvs_to_duckdb()
