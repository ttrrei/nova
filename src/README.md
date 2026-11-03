# src/

Nova's application source (installed with `pip install -e .`).

| Folder | Contents |
|---|---|
| `nova/` | The `nova` CLI package. One module per responsibility per the design contract: `data.py` (CSV/Parquet archive, hash, validate, aggregate), `store.py` (DuckDB catalog + Parquet views), `catalog.py` (registered feature contracts), `indicators.py` (isolated Supertrend recursion), `features.py` (TA-Lib + semantic features, core/trend/momentum domains), `config.py` + `compiler.py` (safe YAML → past-only SQL), `trades.py` (single-trade state machine), `metrics.py` (calendar-time scores, monthly zeros), `runner.py` (windowed per-instrument runs, publication), `audit.py` (independent ledger audit), `cli.py`, `common.py`, `doctor.py`. |
| `nova_research.egg-info/` | Regenerable pip metadata (ignored). |

The frozen core set of files is recorded in `FROZEN_CORE.sha256`; any change
to them fails `scripts/check_frozen_core.py` and invalidates historical runs.
