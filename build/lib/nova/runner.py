"""Execute universal YAML rules per instrument and publish auditable run artifacts."""

import csv
import importlib.metadata
import json
import platform
import uuid
from dataclasses import fields
from datetime import datetime, timezone
from pathlib import Path


from .catalog import FEATURES, FEATURE_PARAMS, FEATURE_VERSION
from .common import file_hash, identity, write_json
from .compiler import compile_strategy
from .config import load_strategy
from .data import _verify_files
from .features import current_market, feature_runtime, instrument_view
from .metrics import summarize
from .store import connect, dataset
from .trades import Trade, simulate


def bound(value):
    if value is None:
        return None
    try:
        result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if len(str(value)) == 10:
            result = result.replace(tzinfo=timezone.utc)
        if result.tzinfo is None:
            raise ValueError("Use an ISO date or timezone-aware timestamp")
        return result.astimezone(timezone.utc)
    except (ValueError, TypeError) as error:
        raise ValueError(f"Invalid UTC bound: {value}") from error


def runtime_versions():
    return {
        "python": platform.python_version(),
        **{
            name: importlib.metadata.version(name)
            for name in ("duckdb", "numpy", "pyarrow", "pandas", "TA-Lib", "PyYAML")
        },
    }


def engine_hash():
    return identity(
        {p.name: file_hash(p) for p in sorted(Path(__file__).parent.glob("*.py"))}
    )


def write_csv(path, rows, names):
    with Path(path).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=names)
        writer.writeheader()
        writer.writerows(rows)


def run(strategy, root="data", output="runs", instruments=None, since=None, until=None):
    spec = load_strategy(strategy)
    sql = compile_strategy(spec)
    since, until = bound(since), bound(until)
    if since and until and since >= until:
        raise ValueError("since must precede exclusive until")
    with connect(root) as con:
        manifest = dataset(con, "features", spec["timeframe_minutes"])
        market = current_market(con, spec["timeframe_minutes"])
        if (
            manifest["feature_version"] != FEATURE_VERSION
            or manifest["parameters"] != FEATURE_PARAMS
            or manifest["runtime"] != feature_runtime()
            or manifest["market_snapshot_id"] != market["snapshot_id"]
        ):
            raise ValueError("Feature version changed; run nova features again")
        _verify_files(manifest)
        available = set(manifest["windows"])
        selected = sorted(set(instruments) if instruments else available)
        if not selected or set(selected) - available:
            raise ValueError(
                f"Unknown/empty instrument selection: {set(selected) - available}"
            )
        versions = runtime_versions()
        source_hash = engine_hash()
        strategy_hash = identity(spec)
        inputs = {
            "strategy_hash": strategy_hash,
            "feature_snapshot": manifest["snapshot_id"],
            "engine_hash": source_hash,
            "instruments": selected,
            "since": since,
            "until_exclusive": until,
            "runtime": versions,
        }
        run_id = identity(inputs)[:20]
        destination = Path(output).resolve() / run_id
        if (destination / "manifest.json").exists():
            previous = json.loads((destination / "manifest.json").read_text())
            for name, digest in previous["artifact_hashes"].items():
                if file_hash(destination / name) != digest:
                    raise ValueError(f"Run artifact changed: {destination / name}")
            summary = json.loads((destination / "summary.json").read_text())
            con.execute(
                "INSERT OR REPLACE INTO experiment_runs VALUES (?,?,?,?,?,?)",
                [
                    run_id,
                    strategy_hash,
                    manifest["snapshot_id"],
                    source_hash,
                    str(destination),
                    json.dumps(summary, allow_nan=False),
                ],
            )
            return destination, summary
        if destination.exists():
            raise ValueError(f"Unfinished run exists: {destination}")
        work = destination.with_name(destination.name + ".tmp-" + uuid.uuid4().hex[:8])
        work.mkdir(parents=True)
        all_trades = []
        windows = {}
        coverage = {}
        signal_counts = {}
        signal_fields = [
            "instrument",
            "bar_open_time",
            "bar_close_time",
            "entry_long",
            "entry_short",
            "exit_long",
            "exit_short",
        ]
        with (work / "signals.csv").open("w", newline="") as signal_stream:
            writer = csv.DictWriter(signal_stream, fieldnames=signal_fields)
            writer.writeheader()
            for instrument in selected:
                instrument_view(con, manifest, instrument)
                filters = []
                parameters = []
                if since:
                    filters.append("b.bar_open_time >= ?")
                    parameters.append(since)
                if until:
                    filters.append("b.bar_close_time <= ?")
                    parameters.append(until)
                where = " AND ".join(filters) or "TRUE"
                # Windows are evaluated over full causal feature history before the requested run slice.
                query = f"""SELECT b.*,s.entry_long,s.entry_short,s.exit_long,s.exit_short FROM features b
                    JOIN ({sql}) s USING(instrument,bar_open_time,bar_close_time) WHERE {where} ORDER BY b.bar_open_time"""
                # Split one cursor stream for the generic bars/signals contract;
                # simulate consumes the two iterators in lockstep.
                cursor = con.execute(query, parameters)
                names = [c[0] for c in cursor.description]
                counts = {key: 0 for key in signal_fields[3:]}
                monthly = {}
                first = None
                last = None

                def stream():
                    nonlocal first, last
                    while chunk := cursor.fetchmany(4096):
                        for row in chunk:
                            bar = dict(zip(names, row))
                            signal = {key: bar[key] for key in signal_fields}
                            first = first or bar["bar_open_time"]
                            last = bar["bar_close_time"]
                            month = bar["bar_open_time"].strftime("%Y-%m")
                            monthly[month] = monthly.get(month, 0) + 1
                            for key in counts:
                                counts[key] += bool(signal[key])
                            if any(signal[key] for key in counts):
                                writer.writerow(signal)
                            yield bar, signal

                from itertools import tee

                bars, signals = tee(stream())
                trades = simulate((p[0] for p in bars), (p[1] for p in signals), spec)
                if first is None:
                    raise ValueError(
                        f"No complete bars for {instrument} in requested interval"
                    )
                original = manifest["windows"][instrument]
                start = (
                    max(bound(original["start"]), since)
                    if since
                    else bound(original["start"])
                )
                end = (
                    min(bound(original["end"]), until)
                    if until
                    else bound(original["end"])
                )
                windows[instrument] = (start, end)
                coverage[instrument] = monthly
                signal_counts[instrument] = counts
                all_trades.extend(trades)
                print(f"{spec['id']}: {instrument}: {len(trades):,} trades", flush=True)
        summary = summarize(all_trades, windows)
        summary["signal_counts"] = signal_counts
        for instrument, stats in summary["per_instrument"].items():
            stats["window"] = {
                "start": windows[instrument][0].isoformat(),
                "end_exclusive": windows[instrument][1].isoformat(),
            }
            for row in stats["monthly_entries"]:
                row["observed_bars"] = coverage[instrument].get(row["month"], 0)
        write_csv(work / "trades.csv", all_trades, [f.name for f in fields(Trade)])
        write_json(work / "summary.json", summary)
        write_json(work / "feature_catalog.json", FEATURES)
        (work / "compiled.sql").write_text(sql + "\n")
        (work / "strategy.yaml").write_text(Path(strategy).read_text())
        report = _report(spec, summary)
        (work / "report.md").write_text(report)
        artifacts = {p.name: file_hash(p) for p in sorted(work.iterdir())}
        run_manifest = {
            "run_id": run_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "inputs": inputs,
            "strategy": spec,
            "features": {k: v for k, v in manifest.items() if k != "files"},
            "artifact_hashes": artifacts,
            "assumptions": {
                "unit": "trade; no quantity, leverage, account or portfolio return",
                "annualization": "arithmetic net trade-return sum / full calendar years",
                "signal_execution": "close confirmation then next observed open",
                "temporal_windows": "observed complete bars; no gap filling",
                "intrabar_order": "stop first when unknown; known open chronology first",
                "intrabar_exit_timestamp": "bar-close reporting proxy; financing uses that approximation",
                "volume": manifest["volume_semantics"],
                "validation": "historical exploration; no legacy OOS machinery",
                "signals_csv": "only rows with at least one true entry/exit condition; includes signals while holding",
                "target_gap": "conservative fill at target; no favorable gap improvement",
                "costs": "observed bid/ask when present, configured full spread otherwise; adverse per-side slippage; flat commission and daily financing",
            },
        }
        write_json(work / "manifest.json", run_manifest)
        work.rename(destination)
        con.execute(
            "INSERT OR REPLACE INTO experiment_runs VALUES (?,?,?,?,?,?)",
            [
                run_id,
                strategy_hash,
                manifest["snapshot_id"],
                source_hash,
                str(destination),
                json.dumps(summary, allow_nan=False),
            ],
        )
        return destination, summary


def _report(spec, summary):
    lines = [
        f"# {spec['id']}",
        "",
        spec.get("hypothesis", spec["family"]),
        "",
        "Historical trade research. Annualized score is an arithmetic trade-return sum per calendar year.",
        "",
        "| Instrument | Trades | Net return sum | Annualized score | Every full month | Pass |",
        "|---|---:|---:|---:|---|---|",
    ]
    for name, row in summary["per_instrument"].items():
        lines.append(
            f"| {name} | {row['trade_count']} | {row['net_trade_return_sum']:.2%} | {row['annualized_trade_return_score']:.2%} | {row['every_full_month_has_entry']} | {row['passes_initial_screen']} |"
        )
    lines.extend(
        [
            "",
            "Individual instrument scores are not combined into a portfolio return.",
            "",
        ]
    )
    return "\n".join(lines)
