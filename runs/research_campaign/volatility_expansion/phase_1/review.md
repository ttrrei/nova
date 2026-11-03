# Volatility expansion phase 1 review

Completed exactly20 distinct full-history hourly experiments across all21 instruments. Every round passed the independent ledger audit; 279,993 trade records were checked across these experiments. All prior assumptions remain fixed, with no feature or data-window changes.

The selected round is **15**, run `093c44e6c8e458fc85dc`: **11/21** instruments pass, compared with7/21 at baseline. Its YAML is `strategies/p1_r15.yaml`; its complete records are in `phase_1/round_15.json` and the immutable experiment directory. Passing-instrument median annualized trade-return score is 2.49%; median over all21 instruments is 0.48%. These are individual-instrument distribution summaries, not combined portfolio returns.

The selected rule requires a closing prior24-bar breakout, current range above1.5 Wilder ATR14, and quote activity above its prior24-bar mean. It exits on rolling midpoint failure or after18 observed bars, with the mandatory2% stop and no takeprofit cap. Quote activity retains its source meaning; it is not actual market-wide traded volume.

| Round | Change | Passes | Actual lesson |
|---:|---|---:|---|
| 1 | Baseline fixed range_atr above1.5 with breakout,24bar holding and midpoint exit. | 7/21 | Baseline: score failures dominate; regular openings mostly sufficient. |
| 2 | Expansion threshold1.5→2.0ATR; other rules unchanged. | 4/21 | Stronger shocks improve some scores but lose monthly coverage. |
| 3 | Expansion threshold1.5→1.0ATR frombaseline. | 7/21 | More ordinary expansions add turnover without broader profitability. |
| 4 | Delay entry one confirmation bar after baseline expansion; outer-quarter hold. | 4/21 | One-bar delay loses continuation timing and breadth. |
| 5 | Remove midpoint indicator exits; retain2%stop,4%target and24bar maximum. | 4/21 | Midpoint failure exits support breadth versus exit ablation. |
| 6 | Tighten rolling-range indicator exit frommidpoint toouter-quarter. | 6/21 | Tighter outer-quarter exits alter winners but do not improve breadth. |
| 7 | Add efficiency_24>.25 filter tobaseline entries. | 3/21 | Efficiency conditioning becomes too sparse for monthly eligibility. |
| 8 | Add relative_volume_24>1.0 tobaseline entries. | 7/21 | Above-average quote activity retains breadth and modestly improves rank. |
| 9 | Raise activity filter from1.0to1.25; retain1.5ATR expansion. | 5/21 | Stronger activity selection loses BTC monthly coverage and breadth. |
| 10 | Shorten maximum holding24→12bars on activity-supported branch. | 8/21 | 12-bar cap adds DE30 and improves breadth. |
| 11 | Shorten holding12→6bars on activity-supported expansion. | 4/21 | Six bars is too short; turnover/early exits hurt. |
| 12 | Increase holding12→18bars as local horizon sensitivity. | 8/21 | 18 bars retains eight passes and improves score ordering. |
| 13 | Long-only arm ablation on18bar activity-supported expansion. | 3/21 | Long-only has nine positive scores but only three monthly passes. |
| 14 | Short-only arm ablation on18bar activity-supported expansion. | 1/21 | Short-only has four positive scores but only one monthly pass. |
| 15 | Remove4%takeprofit; retain midpoint,18bar cap and mandatory2%stop. | 11/21 | Removing target broadens to eleven; fixed target truncation matters. |
| 16 | Tighten profit target4%→2% on the18bar activity-supported branch. | 7/21 | Tighter target falls to seven, supporting the target-truncation diagnosis. |
| 17 | Increase uncapped maximumholding18→24bars. | 8/21 | 24 uncapped bars has eight passes; broader winner is horizon-sensitive. |
| 18 | Shorten uncapped holding18→12bars. | 7/21 | 12 uncapped bars has seven passes; no wide holding plateau shown. |
| 19 | Lower expansion threshold1.5→1.25ATR on uncapped18bar activity-supported winner. | 7/21 | Lower expansion threshold loses four passes; threshold sensitivity remains. |
| 20 | Remove activity>1.0filter from uncapped18bar winner. | 9/21 | Activity ablation has nine passes: participation contributes, with selected sensitivity. |

## Selected individual instrument results

| Instrument | Score per year | Trades | Zero complete months | Positive reported years | Positive after excluding best year |
|---|---:|---:|---:|---:|---|
| AUD_USD | -7.42% | 636 | 0 | 1/7 | False |
| BCO_USD | 13.65% | 609 | 0 | 5/7 | True |
| BTC_USD | 16.04% | 979 | 0 | 5/7 | True |
| CN50_USD | -5.82% | 534 | 0 | 3/7 | False |
| DE30_EUR | 1.28% | 570 | 0 | 5/7 | False |
| ETH_USD | 0.18% | 943 | 0 | 3/7 | False |
| EUR_USD | -4.97% | 873 | 0 | 0/7 | False |
| GBP_USD | -4.03% | 804 | 0 | 0/7 | False |
| HK33_HKD | -7.09% | 529 | 0 | 2/7 | False |
| JP225_USD | 3.01% | 463 | 2 | 5/7 | True |
| NAS100_USD | 5.00% | 844 | 0 | 5/7 | True |
| NZD_USD | -6.05% | 589 | 0 | 1/7 | False |
| SPX500_USD | -2.34% | 634 | 0 | 2/7 | False |
| UK100_GBP | 0.56% | 400 | 0 | 3/7 | False |
| US30_USD | 0.48% | 805 | 0 | 4/7 | False |
| USD_CAD | -2.79% | 740 | 0 | 1/7 | False |
| USD_CHF | -1.62% | 610 | 5 | 2/7 | False |
| USD_JPY | 2.49% | 832 | 0 | 4/7 | True |
| WTICO_USD | 14.78% | 676 | 0 | 5/7 | True |
| XAG_USD | 4.07% | 659 | 0 | 3/7 | False |
| XAU_USD | 1.83% | 882 | 0 | 5/7 | True |

## Interpretation and next-stage guidance

The11 passing instruments are BCO_USD, BTC_USD, DE30_EUR, ETH_USD, NAS100_USD, UK100_GBP, US30_USD, USD_JPY, WTICO_USD, XAG_USD, XAU_USD. JP225 has a positive score but fails monthly regularity. The selected rule is materially sensitive to its horizon:12 and24 uncapped bars produce7 and8 passes respectively, versus11 at18. Reducing expansion to1.25ATR yields7; removing activity yields9. Therefore the selected breadth is an adaptive historical maximum, with no stable neighborhood demonstrated yet.

Excluding each instrument’s best reported year leaves nonpositive total returns for 5/11 passing instruments: DE30_EUR, ETH_USD, UK100_GBP, US30_USD, XAG_USD. This is descriptive and is not an extra acceptance gate. Reported calendar-year buckets include partial endpoints, especially2026. Individual yearly results remain in each round record.

The next stage should investigate nearby holding horizons around18, nearby expansion/activity settings, and simpler controls before adding more filters. It should test whether the no-target improvement survives those neighbors rather than optimize only the largest winner. Keep both directions for the main rule: long-only and short-only controls lose regularity. Additional trend/previous-compression conditioning is still an open hypothesis, but existing efficiency filtering already showed a frequency penalty. Higher costs can later diagnose sensitivity without lowering baseline assumptions.

No successful-round execution or audit failures occurred. All losing hypotheses remain preserved. Phase2 has not started; it requires the coordinator’s review and guidance.
