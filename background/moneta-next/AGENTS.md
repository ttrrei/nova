# Moneta Next working rules

The user wants a small trade-discovery system. Preserve these decisions:

- DuckDB + Parquet; Hybrid means a core wide table and domain wide tables.
- Strategies are YAML only. No strategy-specific Python, arbitrary SQL, callbacks or eval.
- Features are registered causal per-bar outputs. Temporal strategy conditions compile to past-only SQL.
- A mandatory 2% adverse underlying-price move from each actual entry fill is an exit rule: long -2%, short +2%.
- The initial unit is a trade, not an account. Do not add sizing, leverage allocation, margin, equity drawdown, High-Water Mark, or account circuit breakers.
- Opportunity means an actual opening. Show every month, including months with no entries.
- Resolve unknown same-bar stop/target ordering in favour of the losing exit. Respect known open-time chronology and adverse gaps.
- Reuse old data as AI/research material without importing old-project OOS machinery.
- Keep volume's source meaning in metadata while allowing its use as a market-volume proxy.
- The annualized trade-return score is arithmetic trade-return sum divided by full calendar years. It is not account CAGR. A different score needs an explicit documented change.
- Use the same strategy and feature parameters across instruments. Report per instrument; do not add instrument returns into a fictitious portfolio return.
- Tests must cover causal timestamps, temporal confirmation, long/short stop levels, fills, gaps, costs and zero-trade months.
- Feature computation changes require a FEATURE_VERSION bump to invalidate the feature snapshot cache.
- First integrate actual data and review resulting trades before adding automated AI discovery, hundreds of indicators or distributed infrastructure.

Read README.md and START_HERE.md before changing scope. This project has no runtime dependency on the legacy repository.

## v0.2 migration rules

Read migration/MIGRATION_GUIDE.md and PROVENANCE.json. Preserve reference bytes and record changes to reused modules. The legacy checkout is not a runtime dependency; reused code is vendored under its recorded Apache 2.0 license. Keep cached AROON/BBANDS affected columns and VWAP blocked. Compute and evaluate per instrument. Preserve observed Bid/Ask. After dependencies are installed, run every previously skipped integration check.
