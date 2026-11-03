# data/market/1m/

One-minute market snapshot(s). Each child directory is one immutable snapshot
(per-instrument Parquet — excluded by type — plus a tracked
`manifest.json`). Built by `nova aggregate`; the 1m base is the starting
point for 5m/60m aggregation. Selected via the catalog in
`data/nova.duckdb` (latest snapshot wins per kind/timeframe; older
snapshots remain on disk).
