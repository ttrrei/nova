# Range trading phase 1 review

Completed20 distinct audited experiments across all21 instruments and full hourly histories. Total audited trade rows across experiments: 290,213. Baseline has0passing instruments. Selection uses passcount, then median passing score and median score across all21; returns are not combined into a portfolio.

The selected candidate is round19, run`cdac8eb24cc70865adc6`, YAML`/home/ubuntu/work/nova/runs/research_campaign/range_trading/strategies/p1_r19.yaml`. It has9/21passes, median passing annualized trade-return score2.66%, and median score across21 of-2.65%. It produced11,119actual openings. These are adaptive historical results.

## Research rounds

| Round | Change | Passing instruments | Post-result lesson |
|---:|---|---:|---|
| 1 | Reproduce original range-fade baseline under frozen campaign engine. | 0/21 | All21scores are negative while20/21 satisfy monthly activity; the failure is economics, especially fading volatile crypto/commodities. Test a return inside the range before risking a fade instead of broadening activity. |
| 2 | Replace immediate outer-band fade with a within3bar outer touch followed by an inner-band close; retain lowefficiency and exits. | 2/21 | Reclaim confirmation creates2marginal equity-index passes and cuts some commodity losses, but median score stays near-4.5%. Time exits still affect7274trades, so test whether the12bar deadline cuts incomplete range recoveries. |
| 3 | Extend only maximum holding from12 to24bars on the reclaim branch. | 2/21 | Holding24 rather than12bars leaves2passes but improves their median score from0.12%to0.99%/year and all-instrument median from-4.50%to-3.17%. Test a48bar neighbor to see whether slower recovery is a real mechanism or a narrow horizon effect. |
| 4 | Extend the reclaim branch cap24to48bars, keeping its midpoint and1%target exits. | 4/21 | The48bar neighbor raises breadth2to4 and improves all-instrument median to-2.62%; allmonths remain active. Range recovery is slower than the baseline assumed, yet volatile instruments remain deeply negative. Before adding filters, isolate whether the1%profitcap cuts larger successful recoveries. |
| 5 | Remove take-profit only from the48bar reclaim branch; mandatory2%stop and midpoint exit remain. | 4/21 | Removing the1%target keeps4passes and raises their median to1.65%/year, substantially cutting BTC/ETH losses but not making them positive. Mean-of-range entry remains countertrend too often; test whether broader EMA60 direction distinguishes a tradable pullback inside a local range. |
| 6 | Add directional EMA60 location to the no-target48bar range-reclaim branch. | 0/21 | EMA60 alignment creates5positive instruments and reduces losses but eliminates allmonthlypasses because setups become too rare. Test a looser efficiency ceiling on this quality branch rather than abandon its directional context immediately. |
| 7 | Relax path-efficiency ceiling0.25to0.4 only on the EMA60-aligned range-reclaim branch. | 0/21 | Relaxing efficiency increases positive count5to6 but still zero monthlypasses; EMA60 sign rather than efficiency is the activity bottleneck. Allow a limited one-ATR excursion through EMA60 while retaining broad direction protection. |
| 8 | Widen EMA60 location gate from strict side to long>-1ATR and short<+1ATR; retain efficiency0.4. | 1/21 | One-ATR EMA tolerance recovers only1pass and loses several previouslypositive assets. Broad EMA gating is not a clean improvement for range fading. Return to best unrestricted reclaim branch and isolate current-bar shock risk instead. |
| 9 | Add current-bar range<1.5WilderATR only to the best no-target48bar reclaim branch. | 6/21 | Excluding signal bars above1.5ATR raises breadth4to6 while allsixpositives still meet monthly openings; it adds HK33/NAS100 and improves median-all to-1.59%. Test a stricter non-shock neighbor to distinguish useful shock avoidance from a narrow cutoff. |
| 10 | Tighten range-atrsignalbar ceiling1.5to1.2 only. | 3/21 | The1.2ATRneighbor cuts breadth6to3 and creates a monthly failure in positiveJP225. Keep1.5ATR: useful calmness does not mean the smallest bars. On thatbranch, test whether efficiency0.25 excludes too many recoverable ranges. |
| 11 | Relax efficiency ceiling0.25to0.4 on the best1.5ATRshock-filtered reclaim branch. | 3/21 | Relaxing efficiency to0.4 reduces passing breadth6to3 and worsens commodity losses. Low-efficiency context is useful once the EMAgate is removed. Test stricter0.15 as a directional control before settling its0.25ceiling. |
| 12 | Tighten efficiency ceiling0.25to0.15 on the best calm-reclaim branch. | 5/21 | Efficiency0.15 yields5passes versus6at0.25 and changes winners rather than cleanly improving them. Retain0.25forbreadth. Investigate whether too-narrow prior ranges leave insufficient travel to midpoint to cover fills and noise. |
| 13 | Require prior-range width>4ATR on the best shock-filtered reclaim branch. | 7/21 | Minimum width4ATR raises passes6to7 and recovers allcomplete-month coverage, but medianpassing score falls to0.32%/year: several new passes are tiny. Test width6ATR to see whether a larger required range strengthens economics or just changes the marginal winners. |
| 14 | Increase minimum prior-range width4to6ATR only. | 0/21 | Width6ATRcreates7positive instruments but none passmonthly; missing months range2to20. The opportunity-frequency penalty overwhelms apparent quality. Keep width4 and test persistence of the actual reclaim instead of filtering the whole market state more tightly. |
| 15 | Replace single reclaim close with two-bar held_for confirmation while retaining the3bar touch memory. | 7/21 | Two-close confirmation keeps7passes while doubling their medianpassing score to0.75% and improving median-all to-0.76%; JP225isbarelypositive but lacksonefullmonth. Test whether the3bar edge memory is too short for persistent recovery. |
| 16 | Extend edge-touch recognition window3to6bars only on the two-close reclaim branch. | 5/21 | Sixbar touchmemory lowers breadth7to5 while increasing scoreconcentration in equityindices. The latest-touch link is useful; restore3bars. The remaining question is whether long and short range fades behave differently rather than assuming symmetry. |
| 17 | Run long-only ablation of the currentbest two-close/width4/calm-bar range-reclaim branch. | 1/21 | Long-only makes11instruments positive and turns median-allslightlypositive, but onlyGBPpassesmonthly(andscoreismarginal). Directional exposure matters, yet symmetry is essential for opportunity coverage in this range setup. Run the matched short control before finalizing attribution. |
| 18 | Run short-only matched ablation of the round15symmetric branch. | 3/21 | Short-only has5positive instruments and3monthlypasses; it contributes opportunities missed by long-only. Neither side alone matches7symmetricpasses. Keep symmetric execution and test whether exiting at the firstmidpoint truncates continued travel inside a genuine range. |
| 19 | Move long range exit0.5to0.75 and short0.5to0.25; keep entries,48barcap and mandatory stop. | 9/21 | Targeting the opposite innerquarter raises breadth7to9 and medianpassing score0.75%to2.66%/year, but worsens median-all from-0.76%to-2.65%. It helps a broader winning subset while hurting several FX/commodity cases. Test a longer cap on this exit branch to see whether the more ambitious target requires more completion time. |
| 20 | Extend only the opposite-quarter branch holding cap48to96bars. | 9/21 | The96bar neighbor retains the same9monthlypasses but lowers medianpassing score2.66%to1.64%/year and worsens median-all. More completion time is not a free improvement; round19with48barcap remains the phasewinner. Preserve both as a stability comparison. |

## Selected behavior

The entry remains a range-rejection hypothesis: low24bar path efficiency below0.25; an inside-range outer15percent touch within3bars; two persistent inner-band reclaim closes; currentbar range below1.5WilderATR; prior24bar range wider than4ATR. The symmetric long/short entries exit at the opposite innerquarter(0.75long/0.25short), with48observed-bar cap, no profitcap and mandatory entry-fill2%stop. Execution costs and full-history denominators are unchanged. Boundaries continue rolling eachbar; no frozen entrytime range is claimed.

Passing instruments: AUD_USD, DE30_EUR, GBP_USD, NAS100_USD, NZD_USD, SPX500_USD, UK100_GBP, US30_USD, USD_CAD.

| Instrument | Annualized trade-return score | Trades | Zero full months | Losing reported years | Best-year-excluded trade-return sum |
|---|---:|---:|---:|---|---:|
| AUD_USD | 2.66% | 547 | 0 | 2023 | 10.11% |
| BCO_USD | -4.18% | 592 | 0 | 2022, 2023, 2024, 2026 | -49.33% |
| BTC_USD | -6.81% | 708 | 0 | 2022, 2023, 2024, 2026 | -67.29% |
| CN50_USD | -2.92% | 335 | 0 | 2020, 2021, 2023, 2024 | -28.69% |
| DE30_EUR | 3.20% | 462 | 0 | 2024, 2026 | 13.90% |
| ETH_USD | -16.92% | 749 | 0 | 2020, 2022, 2023, 2024, 2025, 2026 | -148.59% |
| EUR_USD | -3.72% | 563 | 0 | 2020, 2021, 2022, 2023, 2024, 2025, 2026 | -25.21% |
| GBP_USD | 0.48% | 569 | 0 | 2020, 2023, 2026 | -3.34% |
| HK33_HKD | -3.93% | 392 | 0 | 2021, 2022, 2024, 2025 | -49.51% |
| JP225_USD | -1.32% | 458 | 1 | 2021, 2023, 2024, 2026 | -27.44% |
| NAS100_USD | 2.88% | 537 | 0 | 2020, 2022 | 7.68% |
| NZD_USD | 0.45% | 559 | 0 | 2022, 2024, 2026 | -3.20% |
| SPX500_USD | 3.35% | 452 | 0 | 2021, 2022, 2025 | -7.23% |
| UK100_GBP | 1.05% | 412 | 0 | 2020 | 0.74% |
| US30_USD | 8.64% | 508 | 0 | 2024 | 22.66% |
| USD_CAD | 0.84% | 572 | 0 | 2020, 2021, 2023, 2024, 2026 | 0.27% |
| USD_CHF | -2.65% | 452 | 2 | 2020, 2021, 2022, 2023, 2025 | -21.65% |
| USD_JPY | -3.00% | 567 | 0 | 2020, 2021, 2022, 2023, 2024, 2026 | -21.55% |
| WTICO_USD | -11.47% | 601 | 0 | 2020, 2022, 2023, 2024, 2026 | -82.83% |
| XAG_USD | -17.76% | 526 | 0 | 2020, 2021, 2023, 2024, 2025 | -129.20% |
| XAU_USD | -4.72% | 558 | 0 | 2020, 2021, 2023, 2024, 2026 | -42.27% |

## What was learned

The initial failure was profitability, not frequency. Causal reclaim rather than immediate fading helped; longer48bar recovery beat12/24bar caps. Removing1%profitcap helped but midpoint exits still limited the useful recovery. Calm signalbars and minimum range amplitude improved a weak winning subset. Extending the exit into the opposite rangequarter made the largest final breadth improvement,7to9passes.

Stricter market-quality filters repeatedly starved monthly opportunities: EMA60alignment produced5–6positive instruments but no passes, and width6ATR produced7positive instruments but no passes. The long-only control produced11positive instruments but only1monthlypass; short-only produced5positive and3monthlypasses. Both directions matter for activity in this setup.

The final branch remains uneven: only9of21 pass and the median score across all21 is negative. Its larger passing count comes with worse median-all than the midpoint-exit round15. 6of9passes remain positive after removing their best reported calendar-year bucket; dependent instruments: GBP_USD, NZD_USD, SPX500_USD. This concentration check is descriptive, not an extra promotion gate;2026ispartial.

## Guidance proposed for phase 2

Retain symmetric range-reclaim behavior rather than importing a long-only trend hypothesis. Prioritize neighboring exit locations around0.75/0.25 because that change caused the largest improvement; compare holding72/other close neighbors against48, noting96already keepsbreadth but weakensscores. Test whether two-close confirmation and3bar touch memory are stable; the6bar memory branch underperformed. Check minimum width4 and shock1.5 with nearby ablations while watching monthly zeros and marginal positive scores. Revisit the midpoint branch as a negative/control comparison because its median-all was better, even though breadth was lower. Investigate why crypto and silver remain deeplynegative before simply adding more conjunctive filters. Preserve the same user screening rule and existing feature parameters; do not claim independent validation.
