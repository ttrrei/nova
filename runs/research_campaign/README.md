# runs/research_campaign/

The finite twelve-direction research campaign (user-authorized, bounded).
Twelve family agents (one per research family), three stages, exactly 20
distinct audited rounds each; coordinator review and guidance between
stages. No unbounded search service, no new strategy language.

- `AGENT_PROTOCOL.md` — the per-agent working rules (read first)
- `campaign.json` — campaign configuration/ledger
- `READY.json` — frozen-engine readiness marker
- `runtime_validation.json`, `runtime_validation/` — runtime validation evidence
- `<family>/` (failed_breakout, market_structure, mean_reversion,
  momentum_exhaustion, pullback_reentry, range_trading, regime_transition,
  relative_strength, session_temporal, trend_continuation, volatility_expansion,
  volume_activity) — per family:
  - `strategies/` — the immutable candidate YAMLs, one per round
  - `phase_1/`, `phase_2/`, `phase_3/` — `round_XX.json` records (per-instrument
    results, ledger audit), `learning.md`, `review.md`
  - `experiments/` — compressed experiment artifacts (full trades/signals)
- `stores/<family>/` — per-direction isolated feature catalogs over the
  shared immutable Parquet inputs

Rules: all 21 instruments, full hourly history, identical thresholds across
instruments, the mandatory 2% adverse-price stop, next-observed-open fills,
one trade per instrument. Per-round CSVs are excluded by the root file-type
rules; JSON/MD/YAML artifacts stay tracked. Historical adaptive research —
disclosed as such, not independent validation.
