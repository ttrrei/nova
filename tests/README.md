# tests/

Nova's test suite (data-free; CI runs it in the locked environment).

| Test | Covers |
|---|---|
| `test_core.py` | Core invariants: causality, temporal confirmation windows |
| `test_data.py` | CSV/Parquet source validation, dedup, provenance, aggregation contracts |
| `test_execution.py` | Long/short fills, 2% stop, gaps, costs, repeated-entry and last-bar rules |
| `test_features.py` | Feature typing, causality, snapshot identity, FEATURE_VERSION |
| `test_temporal.py` | `held_for` / `within` / `after_event` semantics, NULL warm-up handling |
| `test_parquet_import.py` | Native Parquet import pipeline (the `data/import-check` store) |
| `test_compressed_runs.py` | Compressed run artifacts (campaign stores) |
| `test_research_features.py` | Feature-version v2 research primitives (ranges, activity, path efficiency) |
| `test_provenance.py` | Activity-volume provenance and reuse provenance |
| `test_frozen_core.py` | `FROZEN_CORE.sha256` guard |

Run: `.venv/bin/python -m pytest -q`.
