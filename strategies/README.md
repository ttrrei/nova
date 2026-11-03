# strategies/

YAML strategy definitions — the only strategy language Nova accepts.
YAML cannot define feature algorithms, SQL, Python or callbacks; it only
combines registered causal features with the fixed execution contract
(mandatory 2% stop, close-confirmed signals, next-open fills, one trade per
instrument).

| Path | Contents |
|---|---|
| `trend_hold.yaml`, `ema_pullback.yaml`, `mean_reversion.yaml`, `psar_supertrend.yaml` | The four reviewed hourly example strategies run by the small CI-adjacent batch (`nova batch --strategies strategies`). |
| `5m/trend_hold.yaml` | The five-minute example, invoked separately. |
| `directions/` | The twelve fixed hourly research-family hypotheses (one per family: failed_breakout, market_structure, mean_reversion, momentum_exhaustion, pullback_reentry, range_trading, regime_transition, relative_strength, session_temporal, trend_continuation, volatility_expansion, volume_activity). No parameter search — one reviewed hypothesis each. |

Validate with `nova validate <file>`; run with `nova run --strategy <file>`.
