# data/raw_csv/

Nova-owned immutable raw OANDA CSV inputs, one file per instrument
(`EUR_USD.csv`, `BTC_USD.csv`, ...), plus `prices_*.csv` source batches and
`OUTPUT_BASE.csv`.

- Archived by `nova ingest --source ... --kind oanda`, hard-linked to the
  source bytes where possible (copying is the cross-filesystem fallback).
- Every file is hashed at import; the SHA256 set is part of every market
  snapshot's identity. Files must never be edited in place.
- A changed source at an already-owned path is rejected unless it is the
  same linked inode; a re-import of changed content creates a new input
  identity.
- Excluded from the repository by the `*.csv` rule; the folder and this
  README stay visible.
