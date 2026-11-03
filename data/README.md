# data/

Nova's owned data root. Everything here is produced by the `nova` CLI from
validated sources; nothing in this tree is hand-edited.

**Repository policy:** large data files (`*.csv`, `*.parquet`, `*.duckdb`,
`*.npy`) are excluded by the root `.gitignore` file-type rules. The folder
structure and this README remain visible; the bytes live locally (or in
object storage per the `storage/` policy).

## Layout

| Folder | Contents |
|---|---|
| `raw_csv/` | Nova-archived immutable raw OANDA CSVs. Hard-linked (not copied) from the legacy source, hashed on import. Never edited in place; a changed source must be re-imported as a new input identity. |
| `raw_parquet/` | Same role for native Parquet imports (`nova ingest --kind oanda/canonical/ohlcv`). |
| `market/<minutes>m/<snapshot>/` | One sorted Parquet per instrument plus `manifest.json` and a manifest-level README. Snapshot identity includes source SHA256 set, source contract, timeframe and data version. Built by `nova aggregate`. |
| `features/<minutes>m/<snapshot>/` | Three wide domains per instrument — `*_core.parquet` (market + ATR), `*_trend.parquet` (SMA/EMA/PSAR/Supertrend), `*_momentary`/`*_momentum.parquet` (RSI) — plus `manifest.json`. Feature identity adds FEATURE_VERSION, the full parameter set and numerical-library versions. Built by `nova features`. |
| `import-check/` | A throwaway independent store used for the Parquet import acceptance check (`--store data/import-check`); mirrors `raw_parquet/`, `market/`, `features/`, `nova.duckdb` and `tmp/` inside that store. |
| `tmp/` | Scratch space for disk-backed DuckDB staging/spill during expensive sorts. Empty in the repository view; contents are ephemeral. |
| `nova.duckdb` | Local catalog database (excluded by type): dataset/experiment records and Parquet-backed views only. Latest snapshot per kind/timeframe is selected for queries; older immutable snapshots stay on disk. |

## Rules of thumb

- Rebuild chain: `nova ingest` → `nova aggregate` → `nova features` → `nova run`.
- Any new source import invalidates downstream snapshots: rebuild aggregates and features before another experiment.
- A feature computation change requires a FEATURE_VERSION bump; snapshot identity (inputs + timeframe + settings + library versions) must change with it.
- Use `--store <path>` to work in a different data root (e.g. `data/import-check`) so the primary store stays untouched.
