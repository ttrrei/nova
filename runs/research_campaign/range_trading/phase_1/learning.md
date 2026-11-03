
## Round 1

Hypothesis: Low-efficiency closes within the outer15 percent of the prior24bar range may fade toward the rolling midpoint.

Change: Reproduce original range-fade baseline under frozen campaign engine.

Expected learning: Establish whether monthly activity or negative scores are the main failure before changing entry.

Observed: 0/21 pass; 0 additional positive-score instruments fail monthly frequency; 21/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades23766; ranking[0, 0.0, -0.04518180589797531]. Run`5a4dd8aac1abc51692e6`, audit passed.

Passing: none.

Post-result lesson after round1: All21scores are negative while20/21 satisfy monthly activity; the failure is economics, especially fading volatile crypto/commodities. Test a return inside the range before risking a fade instead of broadening activity.

## Round 2

Hypothesis: A return from the outer range back into its inner band may confirm range rejection before fading to midpoint.

Change: Replace immediate outer-band fade with a within3bar outer touch followed by an inner-band close; retain lowefficiency and exits.

Expected learning: Does a causal reclaim remove falling-knife losses while retaining sufficient monthly openings?

Observed: 2/21 pass; 0 additional positive-score instruments fail monthly frequency; 19/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades23489; ranking[2, 0.0012252560483692761, -0.04495049281250136]. Run`e3991d5aa70ea9781dd5`, audit passed.

Passing: SPX500_USD, US30_USD.

Post-result lesson after round2: Reclaim confirmation creates2marginal equity-index passes and cuts some commodity losses, but median score stays near-4.5%. Time exits still affect7274trades, so test whether the12bar deadline cuts incomplete range recoveries.

## Round 3

Hypothesis: A reclaimed range edge may need a full24bar observation horizon to reach its rolling midpoint.

Change: Extend only maximum holding from12 to24bars on the reclaim branch.

Expected learning: Are unfinished reversions prematurely liquidated by the original12bar cap?

Observed: 2/21 pass; 0 additional positive-score instruments fail monthly frequency; 19/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades21681; ranking[2, 0.009930662555243925, -0.0317306363076564]. Run`08e59ab6eb094bd3ebf8`, audit passed.

Passing: UK100_GBP, US30_USD.

Post-result lesson after round3: Holding24 rather than12bars leaves2passes but improves their median score from0.12%to0.99%/year and all-instrument median from-4.50%to-3.17%. Test a48bar neighbor to see whether slower recovery is a real mechanism or a narrow horizon effect.

## Round 4

Hypothesis: Range recovery may require up to48observed bars when the midpoint exit remains active.

Change: Extend the reclaim branch cap24to48bars, keeping its midpoint and1%target exits.

Expected learning: Check whether the24bar improvement persists at a longer nearby holding horizon.

Observed: 4/21 pass; 0 additional positive-score instruments fail monthly frequency; 17/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades21018; ranking[4, 0.009958035469334721, -0.026187895786734805]. Run`87636400532d11b116cf`, audit passed.

Passing: NZD_USD, SPX500_USD, UK100_GBP, US30_USD.

Post-result lesson after round4: The48bar neighbor raises breadth2to4 and improves all-instrument median to-2.62%; allmonths remain active. Range recovery is slower than the baseline assumed, yet volatile instruments remain deeply negative. Before adding filters, isolate whether the1%profitcap cuts larger successful recoveries.

## Round 5

Hypothesis: Allowing recovered range trades to reach the rolling midpoint without a1%profitcap may retain their larger successful reversions.

Change: Remove take-profit only from the48bar reclaim branch; mandatory2%stop and midpoint exit remain.

Expected learning: Measure the contribution of profit truncation independently of entry changes.

Observed: 4/21 pass; 0 additional positive-score instruments fail monthly frequency; 17/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades20775; ranking[4, 0.01650821939020732, -0.02006210878284715]. Run`8ba43fe50c328a564b6b`, audit passed.

Passing: NZD_USD, SPX500_USD, UK100_GBP, US30_USD.

Post-result lesson after round5: Removing the1%target keeps4passes and raises their median to1.65%/year, substantially cutting BTC/ETH losses but not making them positive. Mean-of-range entry remains countertrend too often; test whether broader EMA60 direction distinguishes a tradable pullback inside a local range.

## Round 6

Hypothesis: Range-edge rejection aligned with the broader EMA60 side may avoid fading persistent directional moves.

Change: Add directional EMA60 location to the no-target48bar range-reclaim branch.

Expected learning: Is wrong broader-trend direction responsible for the remaining range-fade losses?

Observed: 0/21 pass; 5 additional positive-score instruments fail monthly frequency; 16/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades5411; ranking[0, 0.0, -0.011064270103237754]. Run`2dc7009c1afd65ade672`, audit passed.

Passing: none.

Post-result lesson after round6: EMA60 alignment creates5positive instruments and reduces losses but eliminates allmonthlypasses because setups become too rare. Test a looser efficiency ceiling on this quality branch rather than abandon its directional context immediately.

## Round 7

Hypothesis: A moderately efficient local range can still reject its edge when aligned with EMA60.

Change: Relax path-efficiency ceiling0.25to0.4 only on the EMA60-aligned range-reclaim branch.

Expected learning: Can more inclusive local-range recognition recover missing months without destroying the trend-conditioned scores?

Observed: 0/21 pass; 6 additional positive-score instruments fail monthly frequency; 15/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades5703; ranking[0, 0.0, -0.009745512124975889]. Run`15ab0d5e112c6d709588`, audit passed.

Passing: none.

Post-result lesson after round7: Relaxing efficiency increases positive count5to6 but still zero monthlypasses; EMA60 sign rather than efficiency is the activity bottleneck. Allow a limited one-ATR excursion through EMA60 while retaining broad direction protection.

## Round 8

Hypothesis: A range-edge rejection can tolerate up to oneATR beyond EMA60 without becoming an unrestricted countertrend fade.

Change: Widen EMA60 location gate from strict side to long>-1ATR and short<+1ATR; retain efficiency0.4.

Expected learning: Test whether rigid moving-average location rather than the range hypothesis caused monthly gaps.

Observed: 1/21 pass; 2 additional positive-score instruments fail monthly frequency; 18/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades11921; ranking[1, 0.021656440784140602, -0.017336726480391012]. Run`9ecdcb575c08e6d3df91`, audit passed.

Passing: US30_USD.

Post-result lesson after round8: One-ATR EMA tolerance recovers only1pass and loses several previouslypositive assets. Broad EMA gating is not a clean improvement for range fading. Return to best unrestricted reclaim branch and isolate current-bar shock risk instead.

## Round 9

Hypothesis: An outer-edge reclaim on a non-shock bar may be more likely to remain a range than one with exceptionally large intrabar movement.

Change: Add current-bar range<1.5WilderATR only to the best no-target48bar reclaim branch.

Expected learning: Can excluding expansion/shock bars improve range reliability without the monthly starvation caused by EMA alignment?

Observed: 6/21 pass; 0 additional positive-score instruments fail monthly frequency; 15/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades19120; ranking[6, 0.012694994548839114, -0.015913802109705947]. Run`01daabc597e31fcd9923`, audit passed.

Passing: HK33_HKD, NAS100_USD, NZD_USD, SPX500_USD, UK100_GBP, US30_USD.

Post-result lesson after round9: Excluding signal bars above1.5ATR raises breadth4to6 while allsixpositives still meet monthly openings; it adds HK33/NAS100 and improves median-all to-1.59%. Test a stricter non-shock neighbor to distinguish useful shock avoidance from a narrow cutoff.

## Round 10

Hypothesis: Restricting a confirmed range reclaim to bars below1.2ATR may further separate range trading from expansion.

Change: Tighten range-atrsignalbar ceiling1.5to1.2 only.

Expected learning: Do additional calm-bar restrictions improve profitability or merely sacrifice opportunities?

Observed: 3/21 pass; 1 additional positive-score instruments fail monthly frequency; 17/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades17468; ranking[3, 0.02595239277868459, -0.016969485823493953]. Run`305f3d83d4d7d2e4a13b`, audit passed.

Passing: NZD_USD, SPX500_USD, US30_USD.

Post-result lesson after round10: The1.2ATRneighbor cuts breadth6to3 and creates a monthly failure in positiveJP225. Keep1.5ATR: useful calmness does not mean the smallest bars. On thatbranch, test whether efficiency0.25 excludes too many recoverable ranges.

## Round 11

Hypothesis: Moderately efficient paths may still support edge-to-midpoint recovery once signal-bar shocks are excluded.

Change: Relax efficiency ceiling0.25to0.4 on the best1.5ATRshock-filtered reclaim branch.

Expected learning: Does an overlystrict range-regime definition suppress valid reversions?

Observed: 3/21 pass; 1 additional positive-score instruments fail monthly frequency; 17/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades23902; ranking[3, 0.018635825662420856, -0.01927057860361916]. Run`2b4e919dfe456315b447`, audit passed.

Passing: NAS100_USD, SPX500_USD, UK100_GBP.

Post-result lesson after round11: Relaxing efficiency to0.4 reduces passing breadth6to3 and worsens commodity losses. Low-efficiency context is useful once the EMAgate is removed. Test stricter0.15 as a directional control before settling its0.25ceiling.

## Round 12

Hypothesis: Only strongly non-directional paths may support a clean range-reclaim fade.

Change: Tighten efficiency ceiling0.25to0.15 on the best calm-reclaim branch.

Expected learning: Check whether the efficiency benefit is monotone or whether overfiltering again loses monthly coverage.

Observed: 5/21 pass; 0 additional positive-score instruments fail monthly frequency; 16/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades13243; ranking[5, 0.009928715084830082, -0.019664510528192267]. Run`77500a1d73d499dca5f6`, audit passed.

Passing: CN50_USD, HK33_HKD, NAS100_USD, NZD_USD, US30_USD.

Post-result lesson after round12: Efficiency0.15 yields5passes versus6at0.25 and changes winners rather than cleanly improving them. Retain0.25forbreadth. Investigate whether too-narrow prior ranges leave insufficient travel to midpoint to cover fills and noise.

## Round 13

Hypothesis: A prior24bar range wider than fourATR may leave sufficient edge-to-midpoint distance for a practical recovery trade.

Change: Require prior-range width>4ATR on the best shock-filtered reclaim branch.

Expected learning: Does minimum available range amplitude improve net-trade economics without excessive activity loss?

Observed: 7/21 pass; 0 additional positive-score instruments fail monthly frequency; 14/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades15957; ranking[7, 0.0032238847154018356, -0.013697466621399514]. Run`f40f9f3ac9540f3d71c8`, audit passed.

Passing: GBP_USD, HK33_HKD, NAS100_USD, NZD_USD, SPX500_USD, UK100_GBP, US30_USD.

Post-result lesson after round13: Minimum width4ATR raises passes6to7 and recovers allcomplete-month coverage, but medianpassing score falls to0.32%/year: several new passes are tiny. Test width6ATR to see whether a larger required range strengthens economics or just changes the marginal winners.

## Round 14

Hypothesis: A wider sixATR prior range may offer more recoverable travel from its edge after a confirmed rejection.

Change: Increase minimum prior-range width4to6ATR only.

Expected learning: Check whether the width mechanism has consistent neighboring support and disclose marginal-score fragility.

Observed: 0/21 pass; 7 additional positive-score instruments fail monthly frequency; 14/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades3466; ranking[0, 0.0, -0.0027901884521323883]. Run`827997bb7816452b6683`, audit passed.

Passing: none.

Post-result lesson after round14: Width6ATRcreates7positive instruments but none passmonthly; missing months range2to20. The opportunity-frequency penalty overwhelms apparent quality. Keep width4 and test persistence of the actual reclaim instead of filtering the whole market state more tightly.

## Round 15

Hypothesis: Two consecutive inner-band closes after an outer-edge touch may confirm a durable range rejection.

Change: Replace single reclaim close with two-bar held_for confirmation while retaining the3bar touch memory.

Expected learning: Can persistence improve weak marginal scores without suppressing actual monthly openings?

Observed: 7/21 pass; 1 additional positive-score instruments fail monthly frequency; 13/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades11784; ranking[7, 0.007487713126799613, -0.007559767401794319]. Run`dafcceecef1d5b89f714`, audit passed.

Passing: DE30_EUR, GBP_USD, NAS100_USD, SPX500_USD, UK100_GBP, US30_USD, USD_CAD.

Post-result lesson after round15: Two-close confirmation keeps7passes while doubling their medianpassing score to0.75% and improving median-all to-0.76%; JP225isbarelypositive but lacksonefullmonth. Test whether the3bar edge memory is too short for persistent recovery.

## Round 16

Hypothesis: A confirmed two-close reclaim may remain linked to an outer-edge test up to sixbars earlier.

Change: Extend edge-touch recognition window3to6bars only on the two-close reclaim branch.

Expected learning: Check whether more patient range recognition recovers missed opportunities without degrading the rejection evidence.

Observed: 5/21 pass; 1 additional positive-score instruments fail monthly frequency; 15/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades17605; ranking[5, 0.025319868664935043, -0.013543765552186482]. Run`5c1039e9f938e6837b1d`, audit passed.

Passing: HK33_HKD, NAS100_USD, SPX500_USD, UK100_GBP, US30_USD.

Post-result lesson after round16: Sixbar touchmemory lowers breadth7to5 while increasing scoreconcentration in equityindices. The latest-touch link is useful; restore3bars. The remaining question is whether long and short range fades behave differently rather than assuming symmetry.

## Round 17

Hypothesis: Long-side range rejection may carry more of the historical range-fading edge than symmetric short entries.

Change: Run long-only ablation of the currentbest two-close/width4/calm-bar range-reclaim branch.

Expected learning: Attribute scores to direction and disclose whether apparent range improvement is dominated by bullish exposure.

Observed: 1/21 pass; 10 additional positive-score instruments fail monthly frequency; 10/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades5591; ranking[1, 0.00021432165395939015, 0.00021432165395939015]. Run`8d3810380382bf3a3d7e`, audit passed.

Passing: GBP_USD.

Post-result lesson after round17: Long-only makes11instruments positive and turns median-allslightlypositive, but onlyGBPpassesmonthly(andscoreismarginal). Directional exposure matters, yet symmetry is essential for opportunity coverage in this range setup. Run the matched short control before finalizing attribution.

## Round 18

Hypothesis: Short-side range rejection may contribute independent reversion opportunities even when its aggregate historical scores are weaker.

Change: Run short-only matched ablation of the round15symmetric branch.

Expected learning: Separate short-side economics from the shared monthly-frequency effect of removing one direction.

Observed: 3/21 pass; 2 additional positive-score instruments fail monthly frequency; 16/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades6193; ranking[3, 0.0064198375879017935, -0.010673775092022]. Run`e5c2aa70af1c5a5f1241`, audit passed.

Passing: GBP_USD, UK100_GBP, US30_USD.

Post-result lesson after round18: Short-only has5positive instruments and3monthlypasses; it contributes opportunities missed by long-only. Neither side alone matches7symmetricpasses. Keep symmetric execution and test whether exiting at the firstmidpoint truncates continued travel inside a genuine range.

## Round 19

Hypothesis: After a persistent edge rejection, price may travel beyond the midpoint toward the opposite inner range quarter.

Change: Move long range exit0.5to0.75 and short0.5to0.25; keep entries,48barcap and mandatory stop.

Expected learning: Does taking more of the same range recovery improve economics rather than merely increasing exposure time?

Observed: 9/21 pass; 0 additional positive-score instruments fail monthly frequency; 12/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades11119; ranking[9, 0.02662287967304626, -0.026502633617857426]. Run`cdac8eb24cc70865adc6`, audit passed.

Passing: AUD_USD, DE30_EUR, GBP_USD, NAS100_USD, NZD_USD, SPX500_USD, UK100_GBP, US30_USD, USD_CAD.

Post-result lesson after round19: Targeting the opposite innerquarter raises breadth7to9 and medianpassing score0.75%to2.66%/year, but worsens median-all from-0.76%to-2.65%. It helps a broader winning subset while hurting several FX/commodity cases. Test a longer cap on this exit branch to see whether the more ambitious target requires more completion time.

## Round 20

Hypothesis: An edge-to-opposite-quarter range recovery may need up to96observed bars once early profittruncation is removed.

Change: Extend only the opposite-quarter branch holding cap48to96bars.

Expected learning: Check whether recovery completion improves broadly or mainly increases long-duration loser exposure.

Observed: 9/21 pass; 0 additional positive-score instruments fail monthly frequency; 12/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades11001; ranking[9, 0.016428095360238523, -0.0289072602100517]. Run`8a9a4b53e1e7b392916c`, audit passed.

Passing: AUD_USD, DE30_EUR, GBP_USD, NAS100_USD, NZD_USD, SPX500_USD, UK100_GBP, US30_USD, USD_CAD.

Post-result lesson after round20: The96bar neighbor retains the same9monthlypasses but lowers medianpassing score2.66%to1.64%/year and worsens median-all. More completion time is not a free improvement; round19with48barcap remains the phasewinner. Preserve both as a stability comparison.
