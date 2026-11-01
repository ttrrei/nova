# Review of the updated Moneta Next v0.2 reference

The updated `background/moneta-next` was compared with Nova's implementation and the final user requirements. It is a reference, not a replacement design contract. Background and legacy files were left unchanged.

## Useful gaps closed in Nova 0.2.1

| Reference addition | Nova action |
|---|---|
| Exact source/license provenance | Corrected the mistaken MIT description to Apache 2.0, retained the already-correct LICENSE, added NOTICE and package license metadata, and recorded source commit/blob/SHA256 plus an adaptation diff |
| CSV/Parquet adapters for raw, aggregate and Gold inputs | Added native Parquet input and explicit `ohlcv` input mode, with per-file schema checks, timezone/duration/alignment validation and complete-bucket filtering |
| Cached-column exclusions | Nova imports market fields only and explicitly records all ignored columns, including Aroon/Bollinger/VWAP and higher-timeframe projections; it recomputes its own registered features |
| Dependency diagnostics | Added `nova-doctor`, `nova doctor` and `python -m nova.doctor`; standalone diagnostics report actual import/native-library failures |
| Integration tests previously skipped | Executed all 69 tests in the updated reference with the available legacy environment; all passed, none skipped |
| Source-identity testing | Added pinned-byte/license checks and numerical parity of Nova's adapted Supertrend with the original source |
| Historical research knowledge | Preserved the 50-idea progress CSV and original 50-feature/200-strategy reports with pinned hashes for future research/AI reference |

The original Apache license text in Nova's LICENSE was always correct. The incorrect label was in the migration prose and indicator header; these have been corrected. See [the source record](provenance/reuse.json), [adaptation diff](provenance/supertrend.patch) and [preserved reference](provenance/reference/supertrend.py).

Nova's own suite now includes Parquet/raw CSV equivalence, canonical Parquet end-to-end execution, partial aggregate filtering, preservation of short and canonical Bid/Ask names, invalid/naive input rejection, exclusion of cached Gold indicators, and dependency error diagnostics. The reference suite is a separate check and is not counted as Nova's own tests. The exact [reference test output](verification/reference_tests.txt) is retained.

The research references under `docs/provenance/reference/research/` preserve the original bytes and historical decisions. They were not rerun, relabeled as current alpha, or used to import the old OOS workflow. Their internal links refer to the original source tree; the source paths and hashes are in `reuse.json`.

## Already covered by Nova

The reference's quote-preserving aggregation, per-instrument computation, Hybrid Parquet/DuckDB store, next-open signals, 2% entry-fill stop, loss-first intrabar order, calendar-month opening counts, trade-level annualization and reproducible caching are already implemented and tested. Nova additionally rebuilt the full supplied raw data and audited five real-data runs.

The reference repairs Aroon/BBANDS output wiring and an uninitialized first gap flag. Nova does not implement or import those old outputs. Its small SMA/EMA/ATR/RSI/PSAR/Supertrend set is recomputed independently; no old cached VWAP or `h1_*` projections enter the runtime. Importing a Gold file does not certify the old indicators in that file.

## Useful future work retained explicitly

- The reference registers 293 names, including a broad legacy parameter grid. Nova retains 28 reviewed features in this release, following the agreed small-core scope. A larger library requires explicit feature contracts, numerical/causality tests and a feature-version update.
- The reference vendors market-structure and catalogue primitives. They remain migration candidates; Nova does not add unused modules or claim their outputs are registered.
- Its closed-bar alignment helper is useful research code, but the reference itself says complete multi-timeframe strategy execution is not connected. Nova continues to run one timeframe per experiment.
- The optional OANDA downloader and OCI acquisition are future data-access work. No broker credentials, download requests or orders were used in this review.
- The reference's warm-up policy masks 360 rows for its legacy profile. This is a different policy from Nova's per-feature NULL warm-up and is not silently applied to existing Nova results. Imported Gold market bars already start after the old head trimming, so rebuilding from raw remains preferable.

## Stale statements in the reference

The source Git repository did not ship large market data, but this workspace's legacy folder does contain it. Nova has already rebuilt it. The reference's missing-dependency/skipped-test notes describe its creation environment; all its 69 checks ran here using the existing legacy environment. These facts do not require replacing Nova's independently installed runtime dependencies.

Prior Nova run directories remain immutable. After these changes the example runs are executed under a new source identity, audited again, and compared with the original trade/signal/summary artifact hashes. Current acceptance reports select the current source identity; `scripts/review_trades.py --include-history` can include earlier runs that still match the selected data snapshots.

