# Moneta v1 → Nova

Source checkout: `legacy/moneta`, inspected at commit `67896d6` (2026-10-31). Background starter: `background/moneta-next`, v0.1. Nova runtime imports only its own package and installed dependencies.

| Asset | Decision and reason |
|---|---|
| Raw OANDA CSVs | Reuse as Nova-owned source files; rebuild clean data, aggregates and catalog from raw inputs |
| Legacy cleaned/aggregate Parquets | Optional native market-data import; default store remains rebuilt from raw. Imported bytes are archived under Nova, with no runtime dependence on legacy paths |
| Legacy 305/270-column feature files | Optional market-bars-only input; all cached indicators are ignored and recorded, and Nova recomputes its small registered library |
| `library/supertrend.py` | Migrate the causal NumPy recursion into `src/nova/indicators.py`; test prefixes, direction and flat-price behavior |
| `library/psar.py` | Retain its TA-Lib SAR calculation and direction convention in Nova's feature engine; explicit fixed parameters and NaN handling |
| TA-Lib SMA/EMA/ATR/RSI use | Reuse the computational approach; validate parity in Nova's tests |
| Starter compiler/config/metrics/trade tests | Adapt into Nova; preserve the final DSL and trade-score definitions, add real-data integration, streaming, snapshots and audits |
| Legacy ingestion/aggregation | Reuse UTC OHLC aggregation and explicit source completeness concepts; independently implement quote preservation, snapshot identities and data quality reporting |
| Legacy backtest engine | Reference only: reciprocal short returns, compounded account accounting, reversal rules and close-based exits differ from the final contract |
| Legacy Python strategy libraries | Historical research material; do not import strategy-specific code or introduce YAML escape hatches |
| Market-structure/catalogue feature code | Retain as future migration candidates; not required before the real-data core is validated |
| 50-feature and 200-strategy reports | Preserve the progress CSV and report bytes under docs/provenance/reference/research with pinned hashes; historical research material without current alpha/promotion claims |
| OOS ledger, tokens, finalist gates | Excluded as explicitly requested; results are labeled historical exploration |
| Account risk/30x/HWM proposals | Excluded by the final simplified requirements |

The source library uses Apache License 2.0; the original text is preserved in `LICENSE`. The initial Nova notes incorrectly called it MIT; the license file itself was correct. `NOTICE` and `docs/provenance/` record the source commit, hashes and changes to the adapted module.

The old feature pipeline and strategy reports are useful evidence, not a blanket correctness certificate. For example, source inspection shows potentially swapped TA-Lib output assignments in the old Aroon/Bollinger groups, and the old documentation records stored VWAP predating a session-grouping correction. Those groups are not migrated into this release. The new pipeline directly verifies the limited feature set it actually publishes.

The old data-profile document describes 6.6 million cleaned rows and a 2025–2026 range. Inspection of the supplied Parquet metadata instead found 48,588,451 minute rows and a January 2020–October 2026 range. Nova's new manifests are the authority for its own rebuilt data; they may differ because raw files, duplicate policy and complete-bucket rules are re-evaluated.

No legacy archive, original result or raw CSV is deleted or edited by the rebuild. Raw hard links share bytes, so neither linked path should be edited in place. Nova derives independent snapshots and records SHA256 identities rather than copying the old runtime database.

