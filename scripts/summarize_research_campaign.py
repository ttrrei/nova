"""Verify a completed campaign stage and preserve compact review evidence."""

import argparse
import csv
import json
from pathlib import Path
import shutil

from nova.catalog import FAMILIES
from nova.common import file_hash, identity, write_json


def summarize(campaign, phase, evidence):
    campaign, evidence = Path(campaign).resolve(), Path(evidence).resolve()
    ready = json.loads((campaign / "READY.json").read_text())
    families = {}
    table = []
    audited_trades = 0
    all_run_ids = set()
    for family in FAMILIES:
        rounds = []
        rules = set()
        for stage in range(1, phase + 1):
            for number in range(1, 21):
                path = campaign / family / f"phase_{stage}" / f"round_{number:02d}.json"
                record = json.loads(path.read_text())
                assert (
                    record["status"] == "passed"
                    and record["audit"]["status"] == "passed"
                ), path
                assert record["engine_hash"] == ready["engine_hash"], path
                assert len(record["per_instrument"]) == 21, path
                assert record["effective_strategy_hash"] not in rules, path
                rules.add(record["effective_strategy_hash"])
                directory = Path(record["directory"])
                manifest = json.loads((directory / "manifest.json").read_text())
                effective = {
                    k: v
                    for k, v in manifest["strategy"].items()
                    if k not in {"id", "hypothesis"}
                }
                assert identity(effective) == record["effective_strategy_hash"], path
                assert manifest["inputs"]["engine_hash"] == ready["engine_hash"], path
                assert manifest["inputs"]["csv_compression"] == "gzip-v1", path
                spec = manifest["strategy"]
                assert spec["family"] == family and spec["timeframe_minutes"] == 60, (
                    path
                )
                assert spec["exit"]["stop_loss_pct"] == 0.02, path
                assert spec["execution"]["spread_bps"] == 2, path
                assert spec["execution"]["slippage_bps_per_side"] >= 0.2, path
                assert len(manifest["inputs"]["instruments"]) == 21, path
                assert manifest["inputs"]["since"] is None, path
                assert manifest["inputs"]["until_exclusive"] is None, path
                if stage > 1:
                    guidance = campaign / f"guidance_phase_{stage}.md"
                    assert record["guidance"]["sha256"] == file_hash(guidance), path
                rounds.append(record)
                all_run_ids.add(record["run_id"])
                audited_trades += record["audit"]["trades_checked"]
                for instrument, stats in record["per_instrument"].items():
                    table.append(
                        {
                            "family": family,
                            "phase": stage,
                            "round": number,
                            "run_id": record["run_id"],
                            "instrument": instrument,
                            "score": stats["annualized_trade_return_score"],
                            "trade_count": stats["trade_count"],
                            "zero_entry_complete_months": stats[
                                "zero_entry_complete_months"
                            ],
                            "passes_initial_screen": stats["passes_initial_screen"],
                            "positive_reported_years": len(stats["positive_years"]),
                            "negative_reported_years": len(stats["negative_years"]),
                            "net_sum_excluding_best_reported_year": stats[
                                "net_sum_excluding_best_reported_year"
                            ],
                        }
                    )
        stage_rounds = [r for r in rounds if r["phase"] == phase]
        stage_best = max(stage_rounds, key=lambda r: r["ranking_key"])
        overall_best = max(rounds, key=lambda r: r["ranking_key"])
        winner_dir = evidence / "strategies" / f"phase_{phase}"
        winner_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(
            Path(overall_best["directory"]) / "strategy.yaml",
            winner_dir / f"{family}.yaml",
        )
        families[family] = {
            "rounds_completed": len(rounds),
            "stage_rounds_completed": len(stage_rounds),
            "stage_best": stage_best,
            "overall_best": overall_best,
            "stage_passing_counts": [
                len(r["passing_instruments"]) for r in stage_rounds
            ],
            "stage_max_positive_count": max(
                len(r["positive_score_instruments"]) for r in stage_rounds
            ),
            "stage_audited_trades": sum(
                r["audit"]["trades_checked"] for r in stage_rounds
            ),
        }
    result = {
        "status": "passed",
        "through_phase": phase,
        "rounds_completed": phase * 240,
        "instrument_evaluations": len(table),
        "unique_run_ids": len(all_run_ids),
        "audited_trades": audited_trades,
        "engine_hash": ready["engine_hash"],
        "selection": "Pass count, then median passing score, then median score over all21; no combined portfolio returns",
        "families": families,
    }
    write_json(evidence / f"phase_{phase}_summary.json", result)
    with (evidence / f"phase_{phase}_instrument_results.csv").open(
        "w", newline=""
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=list(table[0]))
        writer.writeheader()
        writer.writerows(table)
    print(
        f"Verified {phase * 240} rounds; {len(table)} individual instrument evaluations"
    )
    for family, rows in families.items():
        a, b = rows["stage_best"], rows["overall_best"]
        print(
            f"{family}: stage {len(a['passing_instruments'])}/21 at round{a['round']}; overall {len(b['passing_instruments'])}/21 phase{b['phase']} round{b['round']}"
        )
    return result


if __name__ == "__main__":
    app = argparse.ArgumentParser(description=__doc__)
    app.add_argument("--campaign", default="runs/research_campaign")
    app.add_argument("--phase", type=int, choices=(1, 2, 3), required=True)
    app.add_argument("--evidence", default="docs/verification/campaign")
    args = app.parse_args()
    summarize(args.campaign, args.phase, args.evidence)
