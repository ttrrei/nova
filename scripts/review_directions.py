"""Run one fixed hourly YAML per research family, then review published ledgers.

No candidate generation or parameter search. Experiments run sequentially because
the local catalog is writable; agents can prepare the YAML independently.
"""

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from review_trades import review

from nova.catalog import FAMILIES
from nova.common import write_json
from nova.compiler import compile_strategy
from nova.config import load_strategy
from nova.runner import run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", default="data")
    parser.add_argument("--strategies", default="strategies/directions")
    parser.add_argument("--output", default="runs/directions")
    parser.add_argument("--evidence", default="docs/verification/directions")
    args = parser.parse_args()
    candidates = []
    for path in sorted(Path(args.strategies).glob("*.yaml")):
        spec = load_strategy(path)
        compile_strategy(spec)
        if spec["timeframe_minutes"] != 60:
            raise ValueError("This comparison fixes every strategy to hourly bars")
        candidates.append((path, spec))
    if Counter(spec["family"] for _, spec in candidates) != Counter(FAMILIES):
        raise ValueError("Require exactly one strategy for each registered family")
    index = []
    instruments = []
    for path, spec in candidates:
        print(f"Running {spec['family']}: {path}", flush=True)
        destination, summary = run(path, root=args.store, output=args.output)
        stats = summary["per_instrument"]
        passes = [name for name, row in stats.items() if row["passes_initial_screen"]]
        positive = [
            name
            for name, row in stats.items()
            if row["annualized_trade_return_score"] is not None
            and row["annualized_trade_return_score"] > 0
        ]
        index.append(
            {
                "family": spec["family"],
                "strategy": str(path),
                "hypothesis": spec["hypothesis"],
                "run_id": destination.name,
                "directory": str(destination),
                "instruments": len(stats),
                "trades": summary["total_trades"],
                "positive_score_instruments": positive,
                "passing_instruments": passes,
                "no_trade_instruments": [
                    name for name, row in stats.items() if not row["trade_count"]
                ],
            }
        )
        for name, row in stats.items():
            full = [m for m in row["monthly_entries"] if m["complete_calendar_month"]]
            instruments.append(
                {
                    "family": spec["family"],
                    "instrument": name,
                    "run_id": destination.name,
                    "trades": row["trade_count"],
                    "annualized_trade_return_score": row[
                        "annualized_trade_return_score"
                    ],
                    "mean_net_trade_return": row["mean_net_trade_return"],
                    "win_rate": row["win_rate"],
                    "complete_months": len(full),
                    "zero_entry_complete_months": sum(
                        m["actual_entries"] == 0 for m in full
                    ),
                    "positive_years": sum(
                        v > 0 for v in row["yearly_net_trade_return_sum"].values()
                    ),
                    "reported_years": len(row["yearly_net_trade_return_sum"]),
                    "passes_initial_screen": row["passes_initial_screen"],
                }
            )
        print(
            f"Saved {summary['total_trades']:,} trades; "
            f"positive {len(positive)}/{len(stats)}, screen {len(passes)}/{len(stats)}",
            flush=True,
        )
    evidence = Path(args.evidence)
    review(args.store, args.output, evidence)
    audit = json.loads((evidence / "trade_audit.json").read_text())
    if {row["run_id"] for row in audit["results"]} != {row["run_id"] for row in index}:
        raise ValueError(
            "Review directory must contain exactly these twelve current runs"
        )
    write_json(
        evidence / "results_index.json",
        {
            "status": "passed",
            "selection": "One fixed hypothesis per family; no tuning after observing results",
            "timeframe_minutes": 60,
            "trades_checked": audit["trades_checked"],
            "quote_fill_samples_checked": audit["quote_fill_samples_checked"],
            "results": index,
        },
    )
    with (evidence / "instrument_results.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(instruments[0]))
        writer.writeheader()
        writer.writerows(instruments)
    print(f"Reviewed all twelve directions; evidence: {evidence}", flush=True)


if __name__ == "__main__":
    main()
