# data/market/5m/

Five-minute market snapshot(s). Each child directory is one immutable snapshot
(per-instrument Parquet — excluded by type — plus a tracked
`manifest.json`). Built by `nova aggregate --minutes 5`. See
`data/market/README.md` for bucket and manifest rules.
