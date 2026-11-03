# src/nova/

The `nova` package — one module per responsibility (see `docs/DESIGN.md`):

| Module | Responsibility |
|---|---|
| `data.py` | Archive and hash CSVs/Parquet, validate source candles, deterministic dedup, UTC aggregation preserving quotes |
| `store.py` | DuckDB dataset/experiment catalog and Parquet-backed views |
| `catalog.py` | Registered feature contracts, parameters, version, research labels |
| `indicators.py` | Migrated, isolated Supertrend recursion |
| `features.py` | TA-Lib indicators, semantic transformations, core/trend/momentum snapshots |
| `config.py` / `compiler.py` | Strict safe YAML + reviewed expression vocabulary → past-only SQL |
| `trades.py` | Streaming single-trade lifecycle and execution/cost rules |
| `metrics.py` | Calendar-time denominators, explicit monthly zeros, per-instrument screening |
| `runner.py` | Windowed per-instrument evaluation, artifact publication, experiment registration |
| `audit.py` | Independent published-ledger arithmetic and signal/chronology checks |
| `cli.py` / `__main__.py` | `nova` command surface (ingest, aggregate, features, catalog, validate, run, batch, inspect, audit, rebuild) |
| `common.py` | Shared utilities |
| `doctor.py` | Environment/dependency self-check (`nova-doctor`) |

Files here are part of the frozen core (`FROZEN_CORE.sha256`).
