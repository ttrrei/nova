# Verification

Nova 0.2.1 was implemented and verified locally in this workspace. Functional checks demonstrate specified behavior; historical scores describe the particular examples and data. An initial-screen pass is not a promoted/live strategy. The [updated reference review](REFERENCE_REVIEW.md) records the follow-up changes and preserved research evidence.

| Check | Actual result |
|---|---|
| Automated Nova suite | **73 passed**, no skipped DuckDB integration tests |
| Updated reference suite | **69 passed**, no skips, using the available legacy environment; separate from Nova's own suite |
| Static checks | Ruff E4/E7/E9/F checks, formatter check and Python compilation passed |
| Distribution | Wheel built, installed into an isolated target and imported; packaged Python sources match the workspace |
| Raw import | 172 CSVs; 60,958,698 input rows; 48,588,451 cleaned complete minute candles; 21 instruments |
| Duplicates | 12,367,671 complete duplicate rows removed; zero conflicting payload keys |
| Incomplete source rows | 2,576 excluded |
| Hourly store/features | 654,363 complete bars; 179,550 partial buckets excluded |
| Five-minute store/features | 9,299,520 complete bars; 634,703 partial buckets excluded |
| Real executions | Five universal YAML configurations, each evaluated on all 21 instruments |
| Independent ledger audit | **544,631 trades passed** arithmetic, chronology, candidate backing, stop levels, costs, monthly counts and annualization checks |
| Quote fill review | 57 samples across available exit reasons and directions matched stored quotes |
| Aggregate review | 126 first/middle/last samples across both timeframes and all instruments matched one-minute OHLC, Bid/Ask and volume |
| New native Parquet path | Imported the legacy hourly Parquet into an isolated store; all 654,363 complete market bars matched the raw rebuild across all 21 instruments |
| Source provenance | Apache-2.0 license/NOTICE, pinned source hashes and adaptation diff verified; Supertrend numerics match the original source |
| Original source preservation | All 172 Nova raw inputs are hard-linked to their unchanged source files; the legacy tracked checkout remains clean |
| Runtime independence | No imports from legacy/background; rebuild replay uses Nova's own `data/raw_csv` and new environment |
| CI | Workflow supplied for the locked dependencies, suite, static checks and example validation; no remote run claimed |

The first full-data attempt exposed a global deduplication allocation failure under the 1 GB DuckDB limit. The final implementation partitions expensive distinct/window operations by instrument, resumes validated staging after interruption, and successfully completes the same full import at the original memory limit. Successful export removes the generated staging database. A focused interruption/resume regression test is included.

Reproducibility identities include source content, feature/version/settings, selected instruments/window, application source and runtime versions. Existing outputs are verified before reuse. New imports cannot silently use stale downstream features. The full cached rebuild was rerun from Nova's owned inputs in **15.036 seconds**, preserving all five dataset identities. The existing hourly trend experiment was also replayed with its original run ID and artifact hashes. See [rebuild replay](verification/rebuild_replay.json) and [experiment replay](verification/experiment_replay.json).

Evidence:

- [Test report](verification/tests.xml), [environment and feature parameters](verification/environment.json), [packaging](verification/packaging.json).
- [Reference test output](verification/reference_tests.txt), [Parquet import audit](verification/parquet_import_audit.json), [dependency diagnostics](verification/doctor.json).
- [Data audit](verification/data_audit.json), [trade audit](verification/trade_audit.json), [sample trades](verification/trade_samples.csv).
- [Per-instrument results](verification/instrument_results.csv), [run index](verification/results_index.json), [real-data report](REAL_DATA_RESULTS.md).

Repeat the checks:

```bash
.venv/bin/python -m pytest -q
.venv/bin/ruff check src tests scripts --select E4,E7,E9,F
.venv/bin/ruff format --check src tests scripts
.venv/bin/python -m compileall -q src tests scripts
.venv/bin/nova rebuild --source data/raw_csv --timeframes 5 60
.venv/bin/nova batch --strategies strategies
.venv/bin/nova run --strategy strategies/5m/trend_hold.yaml
.venv/bin/python scripts/review_trades.py
.venv/bin/python scripts/verify_rebuild.py
```

Remaining modeling limits are intentional and disclosed: complete-bucket filtering, observed-bar temporal windows, conservative OHLC intrabar ordering, approximate intrabar exit times/financing, simple configurable costs, fixed initial indicator parameters and historical exploration. Example financing/commission are zero. The application does not model account leverage, margin or portfolio returns. Store manifests contain absolute local paths; moving a store requires rebuilding/registering it at its destination.
