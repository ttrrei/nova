from pathlib import Path

import duckdb


def ensure_data_dirs() -> None:
    """Ensure necessary data directories exist."""
    Path("data").mkdir(parents=True, exist_ok=True)
    Path("data/parquet").mkdir(parents=True, exist_ok=True)


def load_csvs_to_duckdb(
    csv_dir: str | Path = "data/raw_csv",
    db_path: str | Path = "data/metadata.duckdb",
    parquet_output_dir: str | Path = "data/parquet",
) -> None:
    """Read each raw CSV file individually using DuckDB's fastest parallel reader,

    register them in metadata.duckdb, and export each to its own Parquet file
    with real-time progress logging.

    Args:
        csv_dir: Directory containing raw CSV files.
        db_path: Path to the DuckDB metadata/database file.
        parquet_output_dir: Directory to store individual Parquet files.
    """
    ensure_data_dirs()
    source_csv_dir = Path(csv_dir)
    target_parquet_dir = Path(parquet_output_dir)

    csv_files = sorted(source_csv_dir.rglob("*.csv"))
    total_files = len(csv_files)

    if total_files == 0:
        print(f"No CSV files found in {source_csv_dir.resolve()}")
        return

    print(f"Found {total_files} CSV files to process.")

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

    for idx, csv_path in enumerate(csv_files, start=1):
        # Generate clean table name based on relative path
        rel_path = csv_path.relative_to(source_csv_dir)
        table_base_name = f"raw_{'_'.join(rel_path.with_suffix('').parts)}".lower()
        # Sanitize table name
        table_name = "".join(c if c.isalnum() else "_" for c in table_base_name)

        parquet_file_path = target_parquet_dir / rel_path.with_suffix(".parquet")
        parquet_file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            print(f"[{idx}/{total_files}] Processing: {rel_path} -> table '{table_name}' ...")

            # Quick load using DuckDB optimized CSV reader directly into individual parquet, explicitly in main schema
            conn.execute(
                f"""
                CREATE OR REPLACE TABLE main.{table_name} AS 
                SELECT * 
                FROM read_csv(
                    '{csv_path.as_posix()}',
                    header=true,
                    auto_detect=true,
                    union_by_name=true
                );
                """
            )

            row_count = conn.execute(f"SELECT COUNT(*) FROM main.{table_name};").fetchone()[0]

            # Export to individual Parquet file
            conn.execute(f"COPY main.{table_name} TO '{parquet_file_path.as_posix()}' (FORMAT PARQUET);")

            # Record metadata
            conn.execute(
                """
                INSERT INTO loaded_tables (table_name, csv_path, parquet_path, row_count)
                VALUES (?, ?, ?, ?);
                """,
                (table_name, str(csv_path), str(parquet_file_path), row_count),
            )

            print(f"  -> Done! Loaded {row_count} rows. Saved to {parquet_file_path}")

        except (duckdb.Error, OSError) as e:
            print(f"  -> Error processing {csv_path}: {e}")

    conn.close()
    print("All CSV files have been processed and exported to individual Parquet files successfully.")


if __name__ == "__main__":
    load_csvs_to_duckdb()
