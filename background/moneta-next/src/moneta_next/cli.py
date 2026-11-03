import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import yaml

from . import __version__
from .catalog import FEATURES
from .compiler import compile_strategy, required_features
from .config import load_strategy
from .features import prepare_features
from .feature_profiles import computation_hash
from .metrics import summarize
from .trades import simulate


def dictionaries(cursor):
    names = [column[0] for column in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]


def write_csv(path, rows, empty_columns=()):
    with Path(path).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]) if rows else empty_columns)
        writer.writeheader()
        writer.writerows(rows)


def run(data, strategy, database, output, profile="starter"):
    spec = load_strategy(strategy)
    sql = compile_strategy(spec)
    Path(database).parent.mkdir(parents=True, exist_ok=True)
    engine_hash = computation_hash()
    strategy_hash = hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest()
    with duckdb.connect(str(database)) as connection:
        snapshot = prepare_features(connection, data, spec["timeframe_minutes"], profile,
                                    Path(database).resolve().parent/"feature_store")
        available = {row[0] for row in connection.execute("DESCRIBE features").fetchall()}
        missing = required_features(spec)-available
        if missing:
            raise ValueError(f"Features unavailable in profile {profile}: {sorted(missing)}; choose --profile imported or legacy")
        runtime_key = sys.version.split()[0]+":"+duckdb.__version__+":"+yaml.__version__
        run_id = hashlib.sha256((snapshot["data_hash"]+snapshot["feature_version"]+strategy_hash+engine_hash+runtime_key).encode()).hexdigest()[:16]
        destination = Path(output) / run_id
        destination.mkdir(parents=True, exist_ok=True)
        trades, windows = [], {}
        instrument_sql = compile_strategy(spec, instrument_filter=True)
        instruments = [row[0] for row in connection.execute("SELECT DISTINCT instrument FROM bars ORDER BY instrument").fetchall()]
        with (destination/"signals.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = None
            for instrument in instruments:
                rows = dictionaries(connection.execute("SELECT * FROM bars WHERE instrument=? ORDER BY bar_open_time", [instrument]))
                signals = dictionaries(connection.execute(instrument_sql, [instrument]))
                if writer is None:
                    writer = csv.DictWriter(stream, fieldnames=list(signals[0]))
                    writer.writeheader()
                writer.writerows(signals)
                trades.extend(simulate(rows, signals, spec))
                windows[instrument] = (rows[0]["bar_open_time"], rows[-1]["bar_close_time"])
                del rows, signals
        summary = summarize(trades, windows)
        manifest = {"run_id": run_id, "created_at": datetime.now(timezone.utc).isoformat(),
                    "engine_version": __version__, "engine_source_hash": engine_hash,
                    "runtime": {"python": sys.version.split()[0], "duckdb": duckdb.__version__, "pyyaml": yaml.__version__},
                    "strategy_hash": strategy_hash, "strategy": spec, "data": snapshot,
                    "assumptions": {"research_unit": "trade", "sizing": "not_modelled", "leverage": "not_modelled",
                        "volume": "source activity used as market-volume proxy", "validation": "historical exploration",
                        "temporal_windows": "observed bars, not clock intervals; no gap filling",
                        "unknown_intrabar_order": "stop before target", "intrabar_exit_timestamp": "bar close reporting proxy",
                        "end_of_data": "close open trade at final close", "entry_conflict": "skip both",
                        "financing": "flat daily approximation; intrabar timing uses bar close"}}
        write_csv(destination/"trades.csv", trades, ["instrument", "entry_time", "exit_time", "net_return"])
        import_report = Path(data).with_suffix(Path(data).suffix+".import.json")
        if import_report.exists():
            manifest["data_import"] = json.loads(import_report.read_text(encoding="utf-8"))
        for name, value in [("summary.json", summary), ("manifest.json", manifest), ("feature_catalog.json", FEATURES)]:
            (destination/name).write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str, allow_nan=False)+"\n", encoding="utf-8")
        (destination/"compiled.sql").write_text(sql+"\n", encoding="utf-8")
        connection.execute("CREATE TABLE IF NOT EXISTS experiment_runs (run_id VARCHAR PRIMARY KEY, strategy_hash VARCHAR, data_hash VARCHAR, engine_hash VARCHAR, summary_json VARCHAR)")
        connection.execute("INSERT OR REPLACE INTO experiment_runs VALUES (?, ?, ?, ?, ?)", [run_id, strategy_hash, snapshot["data_hash"], engine_hash, json.dumps(summary, allow_nan=False)])
    return destination, summary


def main():
    parser = argparse.ArgumentParser(description="Compile YAML, evaluate SQL and discover trades")
    parser.add_argument("--data", required=True, help="Completed OHLC CSV")
    parser.add_argument("--strategy", required=True, help="YAML strategy")
    parser.add_argument("--db", default="data/research.duckdb")
    parser.add_argument("--output", default="runs")
    parser.add_argument("--profile", choices=["starter", "imported", "legacy"], default="starter")
    args = parser.parse_args()
    try:
        destination, summary = run(args.data, args.strategy, args.db, args.output, args.profile)
    except (ValueError, OSError, yaml.YAMLError, duckdb.Error) as error:
        parser.exit(2, f"Invalid experiment: {error}\n")
    print(f"Saved {summary['total_trades']} trades to {destination}")
    print("Annualization is a trade-return score, not account CAGR.")
