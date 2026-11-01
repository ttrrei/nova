"""Execute one auditable round of the explicitly requested 12-family campaign.

The agent chooses a YAML hypothesis, examines the returned results and then
chooses its next round. This helper never generates or modifies a strategy.
"""

import argparse
from contextlib import redirect_stdout
from datetime import datetime, timezone
import json
import math
from pathlib import Path
from statistics import median
import time

import duckdb

from nova.audit import audit_run
from nova.catalog import FAMILIES
from nova.common import file_hash, identity, write_json
from nova.compiler import compile_strategy
from nova.config import load_strategy
from nova.runner import engine_hash, run


def effective_rules(spec):
    """Descriptions and display names cannot turn repeated rules into research."""
    return {
        key: value for key, value in spec.items() if key not in {"id", "hypothesis"}
    }


def summarize_instruments(summary):
    rows = {}
    for name, stats in sorted(summary["per_instrument"].items()):
        complete = [
            row for row in stats["monthly_entries"] if row["complete_calendar_month"]
        ]
        years = stats["yearly_net_trade_return_sum"]
        score = stats["annualized_trade_return_score"]
        if score is None or not math.isfinite(score):
            raise ValueError(f"Missing/nonfinite annualized score for {name}")
        zero_months = [row["month"] for row in complete if row["actual_entries"] == 0]
        rows[name] = {
            "annualized_trade_return_score": score,
            "trade_count": stats["trade_count"],
            "net_trade_return_sum": stats["net_trade_return_sum"],
            "mean_net_trade_return": stats["mean_net_trade_return"],
            "win_rate": stats["win_rate"],
            "complete_months": len(complete),
            "zero_entry_complete_months": len(zero_months),
            "zero_entry_months": zero_months,
            "positive_years": [year for year, value in years.items() if value > 0],
            "negative_years": [year for year, value in years.items() if value < 0],
            "reported_years": len(years),
            "yearly_net_trade_return_sum": years,
            "net_sum_excluding_best_reported_year": (
                stats["net_trade_return_sum"] - max(years.values()) if years else None
            ),
            "passes_initial_screen": stats["passes_initial_screen"],
            "window": stats["window"],
        }
    return rows


def print_result(result):
    print(
        f"{result['family']} phase={result['phase']} round={result['round']:02d} "
        f"run={result['run_id']} audit={result['audit']['status']} "
        f"trades={result['total_trades']} pass={len(result['passing_instruments'])}/21 "
        f"positive={len(result['positive_score_instruments'])}/21 "
        f"rank={result['ranking_key']} replay={result.get('replayed', False)}",
        flush=True,
    )
    for name, stats in result["per_instrument"].items():
        print(
            f"{name:11} score={stats['annualized_trade_return_score']:+.6f} "
            f"trades={stats['trade_count']:5d} zero_months={stats['zero_entry_complete_months']:2d} "
            f"positive_years={len(stats['positive_years'])}/{stats['reported_years']} "
            f"pass={stats['passes_initial_screen']}",
            flush=True,
        )
    print(result["automatic_diagnosis"], flush=True)


def execute_round(args):
    for name in ("hypothesis", "change", "lesson"):
        if not isinstance(getattr(args, name), str) or not getattr(args, name).strip():
            raise ValueError(f"{name} must be nonempty text")
    campaign = Path(args.campaign).resolve()
    family_root = campaign / args.family
    phase_root = family_root / f"phase_{args.phase}"
    phase_root.mkdir(parents=True, exist_ok=True)
    record_path = phase_root / f"round_{args.round:02d}.json"
    strategy_path = Path(args.strategy).resolve()
    spec = load_strategy(strategy_path)
    compile_strategy(spec)
    if spec["family"] != args.family or spec["timeframe_minutes"] != 60:
        raise ValueError("Campaign rounds require the assigned family and 60m bars")
    if spec["exit"]["stop_loss_pct"] != 0.02:
        raise ValueError("Mandatory entry-fill 2% stop cannot change")
    if spec["execution"]["slippage_bps_per_side"] < 0.2:
        raise ValueError("Campaign may stress costs but cannot lower baseline slippage")

    # Guidance is an explicit stage boundary, not a timeout or an inferred approval.
    guidance = None
    if args.phase > 1:
        guidance_path = campaign / f"guidance_phase_{args.phase}.md"
        if not guidance_path.is_file():
            raise ValueError(f"Coordinator guidance is required: {guidance_path}")
        guidance = {"path": str(guidance_path), "sha256": file_hash(guidance_path)}
    for phase in range(1, args.phase + 1):
        stop = 21 if phase < args.phase else args.round
        for number in range(1, stop):
            previous = family_root / f"phase_{phase}" / f"round_{number:02d}.json"
            if (
                not previous.is_file()
                or json.loads(previous.read_text()).get("status") != "passed"
            ):
                raise ValueError(
                    f"Complete and audit preceding round first: {previous}"
                )

    store = campaign / "stores" / args.family
    database = store / "nova.duckdb"
    if not database.is_file():
        raise ValueError(f"Coordinator must prepare an isolated catalog: {database}")
    with duckdb.connect(str(database), read_only=True) as con:
        manifest_row = con.execute(
            "SELECT manifest_path FROM datasets WHERE kind='features' AND timeframe_minutes=60"
        ).fetchone()
    if manifest_row is None:
        raise ValueError("Isolated catalog has no hourly feature snapshot")
    feature_manifest = json.loads(Path(manifest_row[0]).read_text())
    instruments = sorted(feature_manifest["windows"])
    if len(instruments) != 21:
        raise ValueError(
            "Campaign requires all 21 instruments, with full available history"
        )

    request = {
        "protocol_version": 1,
        "family": args.family,
        "phase": args.phase,
        "round": args.round,
        "hypothesis": args.hypothesis,
        "change": args.change,
        "lesson": args.lesson,
        "parent_run_id": args.parent,
        "effective_strategy_hash": identity(effective_rules(spec)),
        "strategy_hash": identity(spec),
        "strategy_path": str(strategy_path),
        "engine_hash": engine_hash(),
        "feature_snapshot": feature_manifest["snapshot_id"],
        "guidance": guidance,
        "instruments": instruments,
    }
    ready_path = campaign / "READY.json"
    if not ready_path.is_file():
        raise ValueError(
            f"Coordinator must publish the verified engine freeze: {ready_path}"
        )
    frozen_engine = json.loads(ready_path.read_text()).get("engine_hash")
    if frozen_engine != request["engine_hash"]:
        raise ValueError("Campaign engine changed after READY.json was published")
    request_hash = identity(request)
    if record_path.is_file():
        previous = json.loads(record_path.read_text())
        if previous.get("request_hash") != request_hash:
            raise ValueError(
                f"Refusing to overwrite a different completed round: {record_path}"
            )
        # A resumed round still verifies published bytes and ledger arithmetic.
        replay_audit = audit_run(previous["directory"])
        if replay_audit != previous["audit"]:
            raise ValueError("Replayed audit differs from the completed round")
        print_result({**previous, "replayed": True})
        return previous

    for previous_path in sorted(family_root.glob("phase_*/round_??.json")):
        previous = json.loads(previous_path.read_text())
        if (
            previous.get("effective_strategy_hash")
            == request["effective_strategy_hash"]
        ):
            raise ValueError(
                "Duplicate trading rules are not a new research round: "
                f"already tested in {previous_path}"
            )
    output = family_root / "experiments"
    output.mkdir(parents=True, exist_ok=True)
    attempt = 1
    while (phase_root / f"round_{args.round:02d}.attempt_{attempt:02d}.json").exists():
        attempt += 1
    attempt_path = phase_root / f"round_{args.round:02d}.attempt_{attempt:02d}.json"
    log_path = phase_root / f"round_{args.round:02d}.attempt_{attempt:02d}.log"
    attempt_record = {
        **request,
        "request_hash": request_hash,
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "log_path": str(log_path),
    }
    write_json(attempt_path, attempt_record)
    before = {p.name for p in output.iterdir() if (p / "manifest.json").is_file()}
    started = time.monotonic()
    try:
        with log_path.open("w", encoding="utf-8") as stream, redirect_stdout(stream):
            directory, summary = run(
                strategy_path,
                root=store,
                output=output,
                instruments=instruments,
                compress_artifacts=True,
            )
        if sorted(summary["per_instrument"]) != instruments:
            raise ValueError("Runner did not report all assigned instruments")
        audit = audit_run(directory)
        rows = summarize_instruments(summary)
        passing = [
            name for name, stats in rows.items() if stats["passes_initial_screen"]
        ]
        positive = [
            name
            for name, stats in rows.items()
            if stats["annualized_trade_return_score"] > 0
        ]
        no_trades = [name for name, stats in rows.items() if stats["trade_count"] == 0]
        positive_missing_months = [name for name in positive if name not in passing]
        passing_median = (
            median(rows[name]["annualized_trade_return_score"] for name in passing)
            if passing
            else 0.0
        )
        all_median = median(
            stats["annualized_trade_return_score"] for stats in rows.values()
        )
        elapsed = round(time.monotonic() - started, 3)
        result = {
            **request,
            "request_hash": request_hash,
            "status": "passed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "seconds": elapsed,
            "elapsed_seconds": elapsed,
            "run_id": directory.name,
            "directory": str(directory),
            "run_is_new": directory.name not in before,
            "is_duplicate": directory.name in before,
            "audit": audit,
            "total_trades": summary["total_trades"],
            "passing_instruments": passing,
            "positive_score_instruments": positive,
            "no_trade_instruments": no_trades,
            "positive_score_but_fails_monthly": positive_missing_months,
            "ranking_key": [len(passing), passing_median, all_median],
            "ranking_definition": (
                "Lexicographic passing-instrument count, median passing-instrument "
                "score (zero if none), median score over all 21 instruments; "
                "instrument returns are never summed into a portfolio"
            ),
            "automatic_diagnosis": (
                f"{len(passing)}/21 pass; {len(positive_missing_months)} additional "
                f"positive-score instruments fail monthly frequency; "
                f"{21 - len(positive)}/21 have nonpositive scores; "
                f"{len(no_trades)} instruments have no trades. "
                "Yearly concentration is descriptive, not another acceptance gate."
            ),
            "per_instrument": rows,
            "attempt_record": str(attempt_path),
            "post_run_learning": (
                "Agent must interpret these observed results in its phase notes before "
                "choosing the next round; submitted lesson records the pre-run expectation."
            ),
        }
        write_json(record_path, result)
        write_json(
            attempt_path,
            {**attempt_record, "status": "passed", "run_id": directory.name},
        )
    except Exception as error:
        write_json(
            attempt_path,
            {
                **attempt_record,
                "status": "failed",
                "seconds": round(time.monotonic() - started, 3),
                "error_type": type(error).__name__,
                "error": str(error),
            },
        )
        raise
    print_result(result)
    return result


def parser():
    app = argparse.ArgumentParser(description=__doc__)
    app.add_argument("--campaign", default="runs/research_campaign")
    app.add_argument("--family", choices=FAMILIES, required=True)
    app.add_argument("--phase", type=int, choices=(1, 2, 3), required=True)
    app.add_argument("--round", type=int, choices=range(1, 21), required=True)
    app.add_argument("--strategy", required=True)
    app.add_argument("--hypothesis", required=True)
    app.add_argument("--change", required=True)
    app.add_argument("--lesson", required=True)
    app.add_argument("--parent")
    return app


if __name__ == "__main__":
    execute_round(parser().parse_args())
