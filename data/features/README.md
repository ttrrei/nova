# data/features/

Registered causal per-bar features, computed per instrument per timeframe
and published as immutable snapshots. Built by `nova features --minutes <5|60>`.

Each `<minutes>m/<snapshot-id>/` directory contains, per instrument:

- `*_core.parquet` — market fields + ATR14 (simple-mean and Wilder)
- `*_trend.parquet` — SMA 6/24, EMA 6/24/60, PSAR, Supertrend and semantic outputs
- `*_momentum.parquet` — RSI14
- `manifest.json` — tracked; feature identity = market snapshot + timeframe +
  FEATURE_VERSION + complete parameter set + numerical-library versions

Feature values are observable at `bar_close_time`; warm-up NULLs are kept
(rows are not dropped). Any computation change requires a FEATURE_VERSION
bump. Parquet files are excluded from the repository by type; manifests and
this README stay visible.
