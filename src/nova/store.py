"""DuckDB catalogs immutable, content-identified Parquet snapshots."""

from pathlib import Path

import duckdb

from .common import sql_string


def connect(root):
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(root / "nova.duckdb"))
    con.execute("SET TimeZone='UTC'")
    con.execute("SET threads=2")
    con.execute("SET memory_limit='1GB'")
    con.execute("SET preserve_insertion_order=false")
    (root / "tmp").mkdir(exist_ok=True)
    con.execute(f"SET temp_directory={sql_string(root / 'tmp')}")
    con.execute("""CREATE TABLE IF NOT EXISTS datasets (
        kind VARCHAR, timeframe_minutes INTEGER, snapshot_id VARCHAR,
        manifest_path VARCHAR, PRIMARY KEY(kind, timeframe_minutes))""")
    con.execute("""CREATE TABLE IF NOT EXISTS experiment_runs (
        run_id VARCHAR PRIMARY KEY, strategy_hash VARCHAR, data_hash VARCHAR,
        engine_hash VARCHAR, output_path VARCHAR, summary_json VARCHAR)""")
    return con


def register(con, kind, minutes, snapshot_id, manifest):
    con.execute(
        "INSERT OR REPLACE INTO datasets VALUES (?, ?, ?, ?)",
        [kind, minutes, snapshot_id, str(Path(manifest).resolve())],
    )


def dataset(con, kind, minutes):
    import json

    row = con.execute(
        "SELECT manifest_path FROM datasets WHERE kind=? AND timeframe_minutes=?",
        [kind, minutes],
    ).fetchone()
    if row is None:
        raise ValueError(
            f"No {kind} dataset for {minutes}m; import/aggregate/build it first"
        )
    return json.loads(Path(row[0]).read_text())


def parquet_view(con, name, files):
    # Names are internal constants, never supplied by a strategy.
    paths = ",".join(sql_string(Path(path).resolve()) for path in files)
    con.execute(
        f'CREATE OR REPLACE VIEW "{name}" AS SELECT * FROM read_parquet([{paths}], hive_partitioning=false)'
    )
