"""Independent checks of published trade arithmetic, chronology and artifact integrity."""

import csv
import json
import math
from collections import Counter
from pathlib import Path

from .common import csv_artifact, file_hash, open_text
from .runner import bound


def audit_run(directory):
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text())
    for name, digest in manifest["artifact_hashes"].items():
        if file_hash(directory / name) != digest:
            raise ValueError(f"Artifact hash mismatch: {name}")
    settings = manifest["strategy"]["execution"]
    exits = manifest["strategy"]["exit"]
    with open_text(csv_artifact(directory, "trades.csv"), newline="") as stream:
        trades = list(csv.DictReader(stream))
    last_exit = {}
    reasons = Counter()
    entries = Counter()
    returns = Counter()
    signals = {}
    with open_text(csv_artifact(directory, "signals.csv"), newline="") as stream:
        for row in csv.DictReader(stream):
            if row["entry_long"] == "True" or row["entry_short"] == "True":
                signals[row["instrument"], bound(row["bar_close_time"])] = row
    for trade in trades:
        name = trade["instrument"]
        side = int(trade["direction"])
        entry, exit_ = float(trade["entry_price"]), float(trade["exit_price"])
        signal_time, entry_time, exit_time = [
            bound(trade[n]) for n in ("signal_time", "entry_time", "exit_time")
        ]
        if side not in (-1, 1) or not signal_time <= entry_time <= exit_time:
            raise ValueError("Invalid trade chronology/direction")
        if name in last_exit and entry_time < last_exit[name]:
            raise ValueError("Overlapping trades")
        last_exit[name] = exit_time
        source = signals.get((name, signal_time))
        if (
            source is None
            or source["entry_long"] == source["entry_short"]
            or source["entry_long"] != str(side == 1)
        ):
            raise ValueError(
                "Actual opening is not backed by an unambiguous candidate signal"
            )
        stop = entry * (1 - side * 0.02)
        if not math.isclose(float(trade["stop_price"]), stop, rel_tol=1e-12):
            raise ValueError("Incorrect mandatory stop")
        gross = side * (exit_ - entry) / entry
        cost = (
            settings["commission_bps_round_trip"] / 10000
            + settings["financing_bps_per_day"]
            / 10000
            * (exit_time - entry_time).total_seconds()
            / 86400
        )
        for column, expected in [
            ("gross_return", gross),
            ("cost_return", cost),
            ("net_return", gross - cost),
        ]:
            if not math.isclose(
                float(trade[column]), expected, rel_tol=1e-10, abs_tol=1e-12
            ):
                raise ValueError(f"Incorrect {column}")
        if trade["exit_reason"] == "stop_loss":
            price = stop * (1 - side * settings["slippage_bps_per_side"] / 10000)
            if not math.isclose(price, exit_, rel_tol=1e-12):
                raise ValueError("Incorrect stop fill")
        if trade["exit_reason"] == "take_profit":
            price = (
                entry
                * (1 + side * exits["take_profit_pct"])
                * (1 - side * settings["slippage_bps_per_side"] / 10000)
            )
            if not math.isclose(price, exit_, rel_tol=1e-12):
                raise ValueError("Incorrect target fill")
        reasons[trade["exit_reason"]] += 1
        entries[name, entry_time.strftime("%Y-%m")] += 1
        returns[name] += gross - cost
    summary = json.loads((directory / "summary.json").read_text())
    if summary["total_trades"] != len(trades):
        raise ValueError("Trade count disagrees with summary")
    for name, stats in summary["per_instrument"].items():
        for row in stats["monthly_entries"]:
            if entries[name, row["month"]] != row["actual_entries"]:
                raise ValueError("Monthly actual opening count mismatch")
        if not math.isclose(
            returns[name], stats["net_trade_return_sum"], rel_tol=1e-10, abs_tol=1e-12
        ):
            raise ValueError("Return sum mismatch")
        window = stats["window"]
        years = (
            bound(window["end_exclusive"]) - bound(window["start"])
        ).total_seconds() / (365.25 * 86400)
        if not math.isclose(
            returns[name] / years,
            stats["annualized_trade_return_score"],
            rel_tol=1e-10,
            abs_tol=1e-12,
        ):
            raise ValueError("Annualization mismatch")
    return {
        "status": "passed",
        "trades_checked": len(trades),
        "exit_reasons": dict(reasons),
        "artifact_hashes_checked": len(manifest["artifact_hashes"]),
    }
