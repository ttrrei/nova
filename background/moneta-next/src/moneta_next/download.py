"""Explicit-path wrapper around the unchanged legacy OANDA extractor."""
import argparse
import os
from pathlib import Path


def download(instrument, since, until, output, granularity="M1", practice=True, session=None, token=None):
    from .vendor.oanda import fetch_candles, candles_to_rows, write_csv
    token = token or os.environ.get("OANDA_API_TOKEN", "")
    if not token:
        raise ValueError("Set OANDA_API_TOKEN in your local environment")
    payload = fetch_candles(instrument, since, until, token=token,
        granularity=granularity, price="MBA", smooth=False, practice=practice, session=session)
    return write_csv(candles_to_rows(payload), Path(output))


def main():
    parser = argparse.ArgumentParser(description="Download raw candles using the pinned legacy extractor")
    parser.add_argument("--instrument", required=True)
    parser.add_argument("--since", required=True)
    parser.add_argument("--until", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--granularity", default="M1")
    parser.add_argument("--live", action="store_true", help="Use the live market-data host; no order endpoints are used")
    args = parser.parse_args()
    try:
        path = download(args.instrument, args.since, args.until, args.output, args.granularity, not args.live)
    except (ImportError, ValueError) as error:
        parser.exit(2, f"{error}; ingestion dependencies: pip install -e '.[ingestion]'\n")
    print(path)


if __name__ == "__main__":
    main()
