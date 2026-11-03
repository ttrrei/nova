# docs/verification/

Machine-readable evidence that the release was built and audited as designed.
Top level covers the baseline release; `directions/` covers the
twelve-hypothesis review.

| File | Contents |
|---|---|
| `doctor.json`, `environment.json`, `baseline_environment.json` | `nova-doctor` status and locked dependency versions |
| `packaging.json`, `baseline_packaging.json` | Packaging checks |
| `data_audit.json`, `parquet_import_audit.json` | Data pipeline and native-Parquet import audits |
| `reference_regression.json`, `reference_tests.txt` | Regression against the reference implementation |
| `experiment_replay.json`, `rebuild_replay.json` | Replay-identity proofs (identical inputs → identical runs) |
| `results_index.json`, `baseline_results_index.json`, `instrument_results.csv` | Published result indexes and per-instrument results |
| `trade_audit.json`, `trade_samples.csv` | Independent trade-ledger audit and fill samples |
| `tests.xml` | Full test-suite report |
| `directions/` | Same artifact set for the twelve direction hypotheses (plus `review_findings.json`) |
