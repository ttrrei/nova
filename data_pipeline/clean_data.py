from pathlib import Path

import duckdb


def clean_all_data(
    db_path: str | Path = "data/metadata.duckdb",
    parquet_output_path: str | Path = "data/parquet/all_data.parquet",
) -> None:
    """Clean the all_data table by removing records where is_complete is false

    and deduplicating rows based on 'instrument' and 'time'.
    Updates both the DuckDB table and the Parquet file.

    Args:
        db_path: Path to the DuckDB metadata/database file.
        parquet_output_path: Path to the single output Parquet file to update.
    """
    database_path = Path(db_path)
    if not database_path.exists():
        print(f"Database file not found at {database_path.resolve()}. Please load data first.")
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

    print("Cleaning data: filtering out incomplete records and removing duplicates by instrument and time...")

    try:
        # Use ROW_NUMBER() or DISTINCT ON to deduplicate based on instrument and time,
        # filtering out records where is_complete is false.
        # Assuming is_complete is BOOLEAN or can be checked as truthy.
        conn.execute(
            """
            CREATE OR REPLACE TABLE main.all_data_cleaned AS 
            WITH filtered AS (
                SELECT *
                FROM main.all_data
                WHERE is_complete = true
            ),
            deduped AS (
                SELECT *,
                       ROW_NUMBER() OVER (PARTITION BY instrument, time) as rn
                FROM filtered
            )
            SELECT * EXCLUDE (rn)
            FROM deduped
            WHERE rn = 1;
            """
        )

        # Replace original table with cleaned table
        conn.execute("DROP TABLE main.all_data;")
        conn.execute("ALTER TABLE main.all_data_cleaned RENAME TO all_data;")

        row_count = conn.execute("SELECT COUNT(*) FROM main.all_data;").fetchone()[0]

        # Update the Parquet file
        target_parquet = Path(parquet_output_path)
        target_parquet.parent.mkdir(parents=True, exist_ok=True)
        print(f"Exporting cleaned data to Parquet: {target_parquet}")
        conn.execute(f"COPY main.all_data TO '{target_parquet.as_posix()}' (FORMAT PARQUET);")

        print(f"-> Done! Cleaned data contains {row_count} rows.")

    except (duckdb.Error, OSError) as e:
        print(f"-> Error during data cleaning: {e}")

    conn.close()


if __name__ == "__main__":
    clean_all_data()
