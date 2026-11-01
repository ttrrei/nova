"""Audit real experiment ledgers and cross-check representative fills against stored quotes."""

import argparse
import csv
import json
import math
from pathlib import Path

from nova.audit import audit_run
from nova.common import csv_artifact, open_text, write_json
from nova.runner import bound, engine_hash
from nova.store import connect, dataset


def review(root, runs, output, include_history=False):
    results = []
    samples = []
    with connect(root) as con:
        for directory in sorted(Path(runs).iterdir()):
            if not (directory / "manifest.json").is_file():
                continue
            manifest = json.loads((directory / "manifest.json").read_text())
            if (
                not include_history
                and manifest["inputs"]["engine_hash"] != engine_hash()
            ):
                continue
            summary = json.loads((directory / "summary.json").read_text())
            audit = audit_run(directory)
            settings = manifest["strategy"]["execution"]
            minutes = manifest["strategy"]["timeframe_minutes"]
            features = dataset(con, "features", minutes)
            if features["snapshot_id"] != manifest["inputs"]["feature_snapshot"]:
                raise ValueError(
                    "Review requires the matching current feature snapshot"
                )
            core = {
                r["instrument"]: r["path"]
                for r in features["files"]
                if r["domain"] == "core"
            }
            seen = set()
            with open_text(csv_artifact(directory, "trades.csv")) as stream:
                for trade in csv.DictReader(stream):
                    group = (trade["exit_reason"], trade["direction"])
                    if group in seen:
                        continue
                    seen.add(group)
                    side = int(trade["direction"])
                    slip = settings["slippage_bps_per_side"] / 10000
                    entry_cursor = con.execute(
                        "SELECT * FROM read_parquet(?) WHERE bar_open_time=?",
                        [core[trade["instrument"]], bound(trade["entry_time"])],
                    )
                    entry = dict(
                        zip(
                            [r[0] for r in entry_cursor.description],
                            entry_cursor.fetchone(),
                        )
                    )
                    exit_field = (
                        "bar_open_time"
                        if trade["exit_time_precision"] == "bar_open"
                        else "bar_close_time"
                    )
                    exit_cursor = con.execute(
                        f"SELECT * FROM read_parquet(?) WHERE {exit_field}=?",
                        [core[trade["instrument"]], bound(trade["exit_time"])],
                    )
                    exit_bar = dict(
                        zip(
                            [r[0] for r in exit_cursor.description],
                            exit_cursor.fetchone(),
                        )
                    )
                    opening = entry[("ask_" if side == 1 else "bid_") + "open"]
                    if opening is None:
                        opening = entry["open"] * (
                            1 + side * settings["spread_bps"] / 20000
                        )
                    assert math.isclose(
                        opening * (1 + side * slip),
                        float(trade["entry_price"]),
                        rel_tol=1e-12,
                    )
                    quote_side = "bid_" if side == 1 else "ask_"

                    def liquidation(point):
                        value = exit_bar[quote_side + point]
                        return (
                            value
                            if value is not None
                            else exit_bar[point]
                            * (1 - side * settings["spread_bps"] / 20000)
                        )

                    reason = trade["exit_reason"]
                    stop = float(trade["stop_price"])
                    if reason == "stop_loss":
                        assert (
                            liquidation("low") <= stop
                            if side == 1
                            else liquidation("high") >= stop
                        )
                        raw = stop
                    elif reason == "take_profit":
                        target = float(trade["take_profit_price"])
                        assert (
                            liquidation("high") >= target
                            if side == 1
                            else liquidation("low") <= target
                        )
                        if trade["exit_time_precision"] == "bar_interval":
                            assert (
                                liquidation("low") > stop
                                if side == 1
                                else liquidation("high") < stop
                            )
                        raw = target
                    elif reason == "end_of_data":
                        raw = liquidation("close")
                    else:
                        raw = liquidation("open")
                        if reason == "stop_gap":
                            assert raw <= stop if side == 1 else raw >= stop
                    assert math.isclose(
                        raw * (1 - side * slip),
                        float(trade["exit_price"]),
                        rel_tol=1e-12,
                    )
                    samples.append(
                        {
                            "run_id": manifest["run_id"],
                            **trade,
                            "source_quote_fill_check": "passed",
                        }
                    )
            results.append(
                {
                    "run_id": manifest["run_id"],
                    "directory": str(directory),
                    "strategy": manifest["strategy"]["id"],
                    "timeframe_minutes": minutes,
                    "audit": audit,
                    "per_instrument": summary["per_instrument"],
                }
            )
    if not results:
        raise ValueError(
            "No runs match the current engine; run the examples first or request --include-history"
        )
    output = Path(output)
    write_json(
        output / "trade_audit.json",
        {
            "status": "passed",
            "runs": len(results),
            "trades_checked": sum(r["audit"]["trades_checked"] for r in results),
            "quote_fill_samples_checked": len(samples),
            "results": results,
        },
    )
    if samples:
        with (output / "trade_samples.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(samples[0]))
            writer.writeheader()
            writer.writerows(samples)
    print(
        f"Audited {len(results)} runs, {sum(r['audit']['trades_checked'] for r in results):,} trades, {len(samples)} quote-fill samples"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--store", default="data")
    parser.add_argument("--runs", default="runs")
    parser.add_argument("--output", default="docs/verification")
    parser.add_argument(
        "--include-history",
        action="store_true",
        help="Also audit prior engine versions with matching data snapshots",
    )
    args = parser.parse_args()
    review(args.store, args.runs, args.output, args.include_history)
