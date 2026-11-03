"""Attach optional reused features to the small, always-available core."""
import hashlib
import json
from pathlib import Path

from .catalog import FEATURES, STARTER_FEATURES, TREND_COLUMNS
from .legacy_catalog import LEGACY_FEATURES, ORIGINAL_FEATURE_NAMES, BLOCKED_CACHED_FEATURES, DIRECTION_TRANSITIONS, direction_transitions


def computation_hash():
    root = Path(__file__).parent
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*.py")):
        digest.update(str(path.relative_to(root)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def attach_profile(connection, profile, input_columns, minutes):
    connection.execute("CREATE TABLE IF NOT EXISTS profile_domains (table_name VARCHAR, columns_json VARCHAR)")
    connection.execute("DELETE FROM profile_domains")
    if profile == "starter":
        return
    if profile == "imported":
        names = sorted((set(input_columns) & ORIGINAL_FEATURE_NAMES) - STARTER_FEATURES - BLOCKED_CACHED_FEATURES)
        if not names:
            raise ValueError("No reviewed legacy features in this input; use moneta-data --reuse-features on a Gold file")
        groups = _groups(names)
        for domain, columns in groups.items():
            expressions = [f"CASE WHEN isnan(CAST({name} AS DOUBLE)) THEN NULL ELSE CAST({name} AS DOUBLE) END AS {name}" for name in columns]
            infinities = " OR ".join(f"isinf(CAST({name} AS DOUBLE))" for name in columns)
            if connection.execute("SELECT count(*) FROM raw_csv WHERE " + infinities).fetchone()[0]:
                raise ValueError("Infinite cached legacy feature")
            table = "features_legacy_" + domain
            connection.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT instrument, CAST(bar_open_time AS TIMESTAMPTZ) AS bar_open_time, CAST(bar_close_time AS TIMESTAMPTZ) AS bar_close_time, {', '.join(expressions)} FROM raw_csv")
            _record(connection, table, columns)
        events = {name: details for name, details in DIRECTION_TRANSITIONS.items() if details[0] in names}
        if events:
            expressions = []
            for name, (source, before, after) in sorted(events.items()):
                previous = f"lag(CAST({source} AS DOUBLE)) OVER (PARTITION BY instrument ORDER BY bar_open_time)"
                current = f"CAST({source} AS DOUBLE)"
                expressions.append(f"CASE WHEN NOT coalesce(isfinite({previous}), false) OR NOT coalesce(isfinite({current}), false) THEN NULL ELSE {previous}={before} AND {current}={after} END AS {name}")
            table = "features_legacy_events"
            connection.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT instrument, CAST(bar_open_time AS TIMESTAMPTZ) AS bar_open_time, CAST(bar_close_time AS TIMESTAMPTZ) AS bar_close_time, {', '.join(expressions)} FROM raw_csv")
            _record(connection, table, sorted(events))
        return
    try:
        import numpy as np
        import pandas as pd
        from .legacy_engine import compute_instrument_features, WARMUP_DROP
    except ImportError as error:
        raise ValueError("Legacy recomputation needs optional dependencies: pip install -e '.[legacy]'") from error
    groups = _groups(set(LEGACY_FEATURES)-STARTER_FEATURES)
    for domain, columns in groups.items():
        table = "features_legacy_" + domain
        definitions = [f"{name} {'BOOLEAN' if FEATURES[name]['unit']=='boolean' else 'DOUBLE'}" for name in columns]
        connection.execute(f"CREATE OR REPLACE TABLE {table} (instrument VARCHAR, bar_open_time TIMESTAMPTZ, bar_close_time TIMESTAMPTZ, {', '.join(definitions)})")
        _record(connection, table, columns)
    instruments = [row[0] for row in connection.execute("SELECT DISTINCT instrument FROM bars ORDER BY instrument").fetchall()]
    for instrument in instruments:
        frame = connection.execute("SELECT instrument, bar_open_time AS time, bar_close_time, open, high, low, close, volume, n_bars FROM bars WHERE instrument=? ORDER BY bar_open_time", [instrument]).fetchdf()
        calculated = compute_instrument_features(frame, minutes*60)
        if set(calculated.columns) != ORIGINAL_FEATURE_NAMES:
            raise ValueError("Legacy registry and computed feature names disagree")
        # Legacy Gold discarded these rows; retain core bars but mask the
        # optional recursive features so scoring keeps the full test window.
        calculated.iloc[:WARMUP_DROP] = np.nan
        for name, values in direction_transitions(calculated).items():
            calculated[name] = values
        if np.isinf(calculated.to_numpy(dtype=float)).any():
            raise ValueError("Infinite legacy feature output")
        calculated["instrument"] = instrument
        calculated["bar_open_time"] = frame["time"]
        calculated["bar_close_time"] = frame["bar_close_time"]
        connection.register("_calculated_legacy", calculated)
        try:
            for domain, columns in groups.items():
                names = ["instrument", "bar_open_time", "bar_close_time", *columns]
                connection.execute(f"INSERT INTO features_legacy_{domain} SELECT {', '.join(names)} FROM _calculated_legacy")
        finally:
            connection.unregister("_calculated_legacy")


def _groups(names):
    groups = {}
    for name in sorted(names):
        groups.setdefault(LEGACY_FEATURES[name]["domain"], []).append(name)
    return groups


def _record(connection, table, columns):
    connection.execute("INSERT INTO profile_domains VALUES (?, ?)", [table, json.dumps(columns)])


def rebuild_view(connection):
    columns = [f"t.{name}" for name in TREND_COLUMNS]
    joins = ["JOIN features_trend t USING(instrument, bar_open_time, bar_close_time)"]
    domains = connection.execute("SELECT table_name, columns_json FROM profile_domains ORDER BY table_name").fetchall()
    for index, (table, names_json) in enumerate(domains):
        alias = f"d{index}"
        columns.extend(f"{alias}.{name}" for name in json.loads(names_json))
        joins.append(f"LEFT JOIN {table} {alias} USING(instrument, bar_open_time, bar_close_time)")
    connection.execute("CREATE OR REPLACE VIEW features AS SELECT c.*, " + ", ".join(columns) + " FROM features_core c " + " ".join(joins))


def export_store(connection, directory, data_hash, version):
    """Atomic Parquet snapshots + the reused legacy metadata/view catalogue."""
    from .storage import register_parquet_table
    folder = Path(directory).resolve() / (data_hash[:16]+"_"+hashlib.sha256(version.encode()).hexdigest()[:12])
    folder.mkdir(parents=True, exist_ok=True)
    tables = ["features_core", "features_trend"] + [row[0] for row in connection.execute("SELECT table_name FROM profile_domains ORDER BY table_name").fetchall()]
    exported = []
    for table in tables:
        path = folder/(table+".parquet")
        if not path.exists():
            temporary = path.with_name(path.name+".tmp")
            escaped = str(temporary).replace("'", "''")
            try:
                connection.execute(f"COPY (SELECT * FROM {table} ORDER BY instrument, bar_open_time) TO '{escaped}' (FORMAT PARQUET)")
                temporary.replace(path)
            except Exception:
                temporary.unlink(missing_ok=True)
                raise
        register_parquet_table(connection, "store_"+table, path)
        exported.append(str(path))
    return exported
