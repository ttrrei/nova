"""Synthetic prices for functionality checks; not evidence of alpha."""
import argparse
import csv
import math
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path


def generate(path, days=210):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    random_source = random.Random(20261031)
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    with Path(path).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["instrument", "bar_open_time", "bar_close_time", "open", "high", "low", "close", "volume", "is_complete"])
        writer.writeheader()
        for instrument, base, phase in [("SYNTH_A", 100, 0), ("SYNTH_B", 1.2, 1.4)]:
            previous = base
            for index in range(days*24):
                close = base * math.exp(0.000015*index + 0.018*math.sin(index/27+phase) + random_source.gauss(0, 0.001))
                amplitude = base*random_source.uniform(0.001, 0.003)
                opening = start+timedelta(hours=index)
                writer.writerow({"instrument": instrument, "bar_open_time": opening.isoformat(),
                    "bar_close_time": (opening+timedelta(hours=1)).isoformat(), "open": previous,
                    "high": max(previous, close)+amplitude, "low": min(previous, close)-amplitude,
                    "close": close, "volume": random_source.randint(50, 500), "is_complete": "true"})
                previous = close


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/demo.csv")
    parser.add_argument("--days", type=int, default=210)
    args = parser.parse_args()
    generate(args.output, args.days)
