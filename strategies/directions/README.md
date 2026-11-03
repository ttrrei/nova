# strategies/directions/

The twelve fixed hourly research-family hypotheses, one YAML per family:
`failed_breakout`, `market_structure`, `mean_reversion`, `momentum_exhaustion`,
`pullback_reentry`, `range_trading`, `regime_transition`, `relative_strength`,
`session_temporal`, `trend_continuation`, `volatility_expansion`,
`volume_activity`.

Rules: identical rules and feature parameters across all 21 instruments; the
mandatory 2% adverse-price stop; close confirmation and next-open execution.
Each file is one reviewed hypothesis — not a parameter search. Run all twelve
with `scripts/review_directions.py` (results land in `runs/directions/`,
audited copies in `docs/verification/directions/`).
