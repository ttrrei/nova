"""Small command-line research workflow; all strategy logic remains YAML."""

import argparse
import json
from pathlib import Path

import duckdb
import yaml

from . import __version__
from .catalog import FEATURES, FEATURE_PARAMS, FEATURE_VERSION
from .common import write_json
from .compiler import compile_strategy
from .config import load_strategy
from .data import aggregate, ingest
from .features import build
from .runner import run
from .store import connect


def parser():
    app = argparse.ArgumentParser(
        description="Nova — YAML → causal SQL → actual trades"
    )
    app.add_argument("--version", action="version", version=__version__)
    commands = app.add_subparsers(dest="command", required=True)
    for name in (
        "ingest",
        "aggregate",
        "features",
        "rebuild",
        "inspect",
        "run",
        "batch",
    ):
        command = commands.add_parser(name)
        command.add_argument(
            "--store",
            default="data",
            help="Nova-owned Parquet store and DuckDB catalog",
        )
        if name in ("ingest", "rebuild"):
            command.add_argument(
                "--source",
                required=True,
                help="Homogeneous CSV/Parquet file or directory; source is archived read-only",
            )
            command.add_argument(
                "--kind", choices=["oanda", "canonical", "ohlcv"], default="oanda"
            )
        if name in ("ingest", "aggregate", "features"):
            command.add_argument(
                "--minutes", type=int, default=1 if name == "ingest" else 60
            )
        if name == "rebuild":
            command.add_argument("--timeframes", nargs="+", type=int, default=[5, 60])
        if name in ("run", "batch"):
            command.add_argument("--output", default="runs")
            command.add_argument("--instruments", nargs="+")
            command.add_argument(
                "--since", help="Inclusive ISO date or timezone-aware timestamp"
            )
            command.add_argument(
                "--until", help="Exclusive ISO date or timezone-aware timestamp"
            )
            command.add_argument(
                "--strategy" if name == "run" else "--strategies",
                required=True,
                help="Strategy YAML"
                if name == "run"
                else "Directory of reviewed YAML strategies",
            )
    command = commands.add_parser("validate")
    command.add_argument("strategy")
    commands.add_parser("catalog")
    commands.add_parser("doctor")
    command = commands.add_parser("audit")
    command.add_argument("directory")
    return app


def main(argv=None):
    app = parser()
    args = app.parse_args(argv)
    try:
        if args.command == "doctor":
            from .doctor import main as doctor_main

            doctor_main()
        elif args.command == "validate":
            spec = load_strategy(args.strategy)
            compile_strategy(spec)
            print(f"Valid: {spec['id']}")
        elif args.command == "catalog":
            print(
                json.dumps(
                    {
                        "version": FEATURE_VERSION,
                        "parameters": FEATURE_PARAMS,
                        "features": FEATURES,
                    },
                    indent=2,
                )
            )
        elif args.command == "ingest":
            result = ingest(args.source, args.store, args.kind, args.minutes)
            _print_dataset(result)
        elif args.command in ("aggregate", "features"):
            result = (aggregate if args.command == "aggregate" else build)(
                args.store, args.minutes
            )
            _print_dataset(result)
        elif args.command == "rebuild":
            _print_dataset(ingest(args.source, args.store, args.kind, 1))
            for minutes in sorted(set(args.timeframes)):
                if minutes != 1:
                    _print_dataset(aggregate(args.store, minutes))
                _print_dataset(build(args.store, minutes))
        elif args.command == "inspect":
            with connect(args.store) as con:
                rows = con.execute(
                    "SELECT kind,timeframe_minutes,snapshot_id,manifest_path FROM datasets ORDER BY 1,2"
                ).fetchall()
                for kind, minutes, snapshot, path in rows:
                    manifest = json.loads(Path(path).read_text())
                    count = sum(
                        r["rows"]
                        for r in manifest["files"]
                        if r.get("domain", "core") == "core"
                    )
                    print(f"{kind:8} {minutes:4}m {count:12,} bars {snapshot[:16]}")
                print(
                    f"Experiments: {con.execute('SELECT count(*) FROM experiment_runs').fetchone()[0]}"
                )
        elif args.command in ("run", "batch"):
            paths = (
                [Path(args.strategy)]
                if args.command == "run"
                else sorted(Path(args.strategies).glob("*.yaml"))
            )
            if not paths:
                raise ValueError("No strategy YAML files found")
            # Validate the entire requested batch before starting experiments.
            for path in paths:
                compile_strategy(load_strategy(path))
            results = []
            for path in paths:
                destination, summary = run(
                    path,
                    args.store,
                    args.output,
                    args.instruments,
                    args.since,
                    args.until,
                )
                results.append(
                    {
                        "strategy": str(path),
                        "run": str(destination),
                        "total_trades": summary["total_trades"],
                    }
                )
                print(f"Saved {summary['total_trades']:,} trades: {destination}")
            if args.command == "batch":
                write_json(Path(args.output) / "batch_latest.json", results)
        elif args.command == "audit":
            from .audit import audit_run

            print(json.dumps(audit_run(args.directory), indent=2))
    except (ValueError, OSError, yaml.YAMLError, duckdb.Error) as error:
        app.exit(2, f"Nova: {error}\n")


def _print_dataset(result):
    rows = sum(r["rows"] for r in result["files"] if r.get("domain", "core") == "core")
    print(
        f"Ready: {result['timeframe_minutes']}m, {rows:,} bars, snapshot {result['snapshot_id'][:16]}"
    )
