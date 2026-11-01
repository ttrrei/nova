"""Verify real rebuilt quotes/bars and produce a repeatable data-quality artifact.

Run from the project root: .venv/bin/python scripts/verify_rebuild.py
This is a read-only audit of the store, apart from its requested JSON output.
"""

import argparse
from pathlib import Path

from nova.common import write_json
from nova.data import PRICES, _verify_files
from nova.store import connect, dataset


def verify(root):
    checks = []
    with connect(root) as con:
        source = dataset(con, "market", 1)
        _verify_files(source)
        sources = {r["instrument"]: r for r in source["files"]}
        off_grid = 0
        for record in source["files"]:
            off_grid += con.execute(
                "SELECT count(*) FROM read_parquet(?) WHERE epoch(bar_open_time)%60 != 0",
                [record["path"]],
            ).fetchone()[0]
        if off_grid:
            raise ValueError("One-minute timestamps are not on the UTC grid")
        for minutes in (5, 60):
            market = dataset(con, "market", minutes)
            _verify_files(market)
            for record in market["files"]:
                frame = con.execute(
                    "SELECT * FROM read_parquet(?) ORDER BY bar_open_time",
                    [record["path"]],
                ).fetch_df()
                for index in sorted({0, len(frame) // 2, len(frame) - 1}):
                    bar = frame.iloc[index]
                    expressions = ["count(*)", "sum(volume)"]
                    for side in ("", "bid_", "ask_"):
                        expressions.extend(
                            [
                                f"arg_min({side}open,bar_open_time)",
                                f"max({side}high)",
                                f"min({side}low)",
                                f"arg_max({side}close,bar_open_time)",
                            ]
                        )
                    actual = con.execute(
                        f"SELECT {','.join(expressions)} FROM read_parquet(?) WHERE bar_open_time>=? AND bar_open_time<?",
                        [
                            sources[record["instrument"]]["path"],
                            bar.bar_open_time.to_pydatetime(),
                            bar.bar_close_time.to_pydatetime(),
                        ],
                    ).fetchone()
                    assert actual[0] == minutes
                    assert abs(actual[1] - bar.volume) < 1e-9
                    for name, reference in zip(PRICES, actual[2:]):
                        if reference is not None:
                            assert abs(float(bar[name]) - reference) <= 1e-10 * max(
                                1, abs(reference)
                            ), name
                    checks.append(
                        {
                            "instrument": record["instrument"],
                            "minutes": minutes,
                            "bar_open_time": str(bar.bar_open_time),
                        }
                    )
        return {
            "status": "passed",
            "source_files": len(source["raw_files"]),
            "one_minute_rows": sum(r["rows"] for r in source["files"]),
            "instruments": len(sources),
            "source_quality": source["quality"],
            "off_grid_minutes": off_grid,
            "aggregate_quote_samples_checked": len(checks),
            "samples": checks,
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--store", default="data")
    parser.add_argument("--output", default="docs/verification/data_audit.json")
    args = parser.parse_args()
    result = verify(Path(args.store))
    write_json(args.output, result)
    print(
        f"Verified {result['aggregate_quote_samples_checked']} aggregate quote samples across {result['instruments']} instruments"
    )
