# data/market/60m/

Hourly market snapshot(s). Each child directory is one immutable snapshot
(per-instrument Parquet — excluded by type — plus a tracked
`manifest.json`). Built by `nova aggregate --minutes 60`. This is the
timeframe the reviewed direction hypotheses run on. See
`data/market/README.md` for bucket and manifest rules.
