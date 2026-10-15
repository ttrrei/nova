from pathlib import Path

import duckdb


def drop_all_duckdb_objects(db_path: str | Path = "data/metadata.duckdb") -> None:
    """Drop all user tables and views from the DuckDB database.

    Args:
        db_path: Path to the DuckDB metadata/database file.
    """
    database_path = Path(db_path)
    if not database_path.exists():
        print(f"Database file not found at {database_path.resolve()}. Nothing to drop.")
        return

    print(f"Connecting to DuckDB at {database_path.resolve()}...")
    conn = duckdb.connect(str(database_path))

    # Fetch all user tables and views in the main schema
    query = """
        SELECT table_name, table_type 
        FROM information_schema.tables 
        WHERE table_schema = 'main';
    """
    results = conn.execute(query).fetchall()

    if not results:
        print("No tables or views found in the 'main' schema.")
        conn.close()
        return

    print(f"Found {len(results)} objects to drop in schema 'main'.")

    for table_name, table_type in results:
        obj_type = "VIEW" if "VIEW" in table_type.upper() else "TABLE"
        print(f"Dropping {obj_type} 'main.{table_name}'...")
        conn.execute(f"DROP {obj_type} IF EXISTS main.{table_name} CASCADE;")

    conn.close()
    print("All tables and views have been successfully dropped from DuckDB.")


if __name__ == "__main__":
    drop_all_duckdb_objects()
