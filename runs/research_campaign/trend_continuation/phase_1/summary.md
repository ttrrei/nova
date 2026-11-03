# Trend continuation phase 1 findings

Completed 20 distinct hourly universal YAML experiments across all 21 instruments. Every round passed the independent ledger audit. All candidates retained the 2% adverse-price stop and baseline observed quotes plus 0.2 bps adverse slippage per side.

| Round | Passing instruments | Positive instruments | Trades | Median passing score | Median all-instrument score |
|---:|---:|---:|---:|---:|---:|
| 1 | 8/21 | 8/21 | 25,604 | 2.63% | -4.21% |
| 2 | 3/21 | 3/21 | 21,348 | 3.31% | -4.37% |
| 3 | 4/21 | 5/21 | 25,686 | 2.14% | -5.35% |
| 4 | 7/21 | 7/21 | 15,211 | 2.49% | -2.72% |
| 5 | 4/21 | 4/21 | 17,509 | 4.04% | -4.52% |
| 6 | 8/21 | 8/21 | 25,604 | 2.52% | -4.14% |
| 7 | 9/21 | 9/21 | 25,604 | 1.91% | -3.87% |
| 8 | 7/21 | 7/21 | 25,604 | 1.36% | -5.60% |
| 9 | 10/21 | 10/21 | 21,929 | 2.08% | -0.61% |
| 10 | 4/21 | 5/21 | 13,651 | 0.72% | -2.53% |
| 11 | 10/21 | 10/21 | 20,626 | 2.38% | -0.25% |
| 12 | 10/21 | 10/21 | 26,760 | 3.78% | -1.32% |
| 13 | 7/21 | 7/21 | 38,229 | 3.26% | -4.24% |
| 14 | 7/21 | 8/21 | 12,005 | 0.89% | -1.30% |
| 15 | 11/21 | 11/21 | 23,242 | 2.68% | 1.92% |
| 16 | 11/21 | 11/21 | 20,521 | 3.90% | 1.23% |
| 17 | 10/21 | 12/21 | 11,072 | 5.06% | 2.20% |
| 18 | 0/21 | 4/21 | 9,449 | 0.00% | -2.03% |
| 19 | 10/21 | 10/21 | 20,230 | 2.44% | -0.98% |
| 20 | 9/21 | 9/21 | 20,192 | 1.98% | -0.81% |

The selected candidate is round 16, run `ee98dd2b05da3dac5864`. It has 11/21 passing instruments versus 8/21 in the original baseline. Median passing score is 3.90%/year and median all-instrument score is 1.23%/year. These are distributions of individual trade-return scores, not portfolio returns.

The winner enters three bars after a PSAR flip while PSAR stays aligned, requires the close on the EMA60 side and directional side of the prior-24-bar range midpoint, excludes efficiency at or above 0.5 and signal bars at or above 1.5 ATR. It removes the fixed profit target and retains PSAR reversal exits plus the 60-bar holding cap. Supertrend agreement was removed after an explicit ablation.

Passing instruments: BTC_USD, DE30_EUR, HK33_HKD, JP225_USD, NAS100_USD, SPX500_USD, US30_USD, USD_JPY, WTICO_USD, XAG_USD, XAU_USD.

Removing the fixed target was useful for broad continuation tails; an efficiency lower bound and persistent state entries were harmful. Supertrend ablation and the shock filter rotate instrument winners, so their higher ranking does not mean each instrument improved. Long-only has 12 positive instruments but only 10 passes because HK33 and JP225 each miss one complete month; short-only has no passes.

4/11 passing instruments become nonpositive when their best reported calendar-year bucket is removed: BTC_USD, NAS100_USD, SPX500_USD, XAG_USD. This is descriptive concentration, not an extra acceptance gate. Year endpoints, including 2026, can be partial.

The two- and four-bar neighbors have 10 and 9 passes against 11 at three bars. The selected timing is locally sensitive. Ten instruments still have nonpositive scores under the winner. These results describe adaptive historical exploration and do not establish future profitability.

## Guidance for the coordinator

- Retain no fixed target and PSAR event framing; verify useful filters with nearby upper-efficiency and shock thresholds rather than stacking new filters.
- Keep all21 instruments and compare individual score/year/month changes. Strong FX and ETH losses persist.
- Revisit long-only frequency with broader entry opportunity timing as a diagnostic branch, while preserving unconditional2%stop and next-open execution.
- Study holding horizons and return-tail concentration; local confirmation2/3/4breadth10/11/9signals selection sensitivity.
- Cost stress should be reported separately from baseline candidate ranking; do not decrease execution costs.
