# data/raw_parquet/

Nova-owned immutable raw Parquet inputs, archived by `nova ingest` for
native Parquet sources (`--kind oanda` minute candles with Mid/Bid/Ask, or
`--kind ohlcv` pre-aggregated bars that must carry `n_bars`).

Same ownership rules as `data/raw_csv/`: hashed on import, never edited in
place, part of downstream snapshot identities. Excluded from the repository
by the `*.parquet` rule; the folder stays visible.
