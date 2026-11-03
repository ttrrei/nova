
## Round 01

Hypothesis: A prior-range wick sweep that closes back inside can revert toward its rolling midpoint.

Change: Reproduce the reviewed failed-breakout baseline under the frozen campaign engine.

Expected lesson: Determine whether profitability or monthly opportunity is the binding baseline problem.

Observed: 1/21 pass; 0 additional positive-score instruments fail monthly frequency; 20/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades 30,587; ranking [1, 0.018253578982978063, -0.06017050100832398]; run `5ffb8149d51234cf9142`; audit passed. Passing: UK100_GBP.

Post-result lesson after round 01: Baseline reproduces one passing instrument, UK100. Every instrument except JP225 has complete-month openings, so the dominant failure is negative trade returns rather than sparse signals. Test whether persistent directional paths invalidate a sweep-fade hypothesis.

## Round 02

Hypothesis: Failed range breaks may revert more reliably when the prior path is directionally inefficient.

Change: Add efficiency24<0.25 to both baseline entries.

Expected lesson: A low-efficiency context should reduce trend-fading losses; assess the loss in monthly coverage alongside profitability.

Observed: 3/21 pass; 1 additional positive-score instruments fail monthly frequency; 17/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades 18,544; ranking [3, 0.007692874755888468, -0.026394559180931653]; run `54f5e3d3c23497863bf8`; audit passed. Passing: CN50_USD, SPX500_USD, UK100_GBP.

Post-result lesson after round 02: Low efficiency improves breadth1to3 and the median all-instrument score from-6.02%to-2.64%/year, but remains mostly unprofitable. AUD becomes marginally positive with one missing month. Test whether a sweep against the short range but with the slower trend avoids structurally fading larger moves.

## Round 03

Hypothesis: Range sweeps in a low-efficiency pause may revert in the direction of the slower EMA60 trend.

Change: Add EMA60 directional alignment to the low-efficiency sweep branch.

Expected lesson: Distinguish countertrend-fade losses from failure of the sweep event itself; frequency may worsen.

Observed: 0/21 pass; 10 additional positive-score instruments fail monthly frequency; 11/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades 3,169; ranking [0, 0.0, -0.0010214270334568082]; run `d5b205aa87023878ea98`; audit passed. Passing: none.

Post-result lesson after round 03: EMA60 directional alignment makes ten instruments positive but creates4to26zero complete months per instrument; no passes. A prior24-range sweep naturally tends to be on the other side of its slow mean. So avoid treating strict directional alignment as a useful monthly strategy and test a loose distance guard instead.

## Round 04

Hypothesis: A range-sweep fade may work when it is not excessively displaced against the slow trend.

Change: Relax strict EMA60 side alignment to long distance>-2ATR and short distance<2ATR.

Expected lesson: Recover monthly frequency while retaining protection against deep continuing trends.

Observed: 1/21 pass; 2 additional positive-score instruments fail monthly frequency; 18/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades 12,682; ranking [1, 0.008398222055329972, -0.030018314746055843]; run `bd385e8b09518642b750`; audit passed. Passing: NAS100_USD.

Post-result lesson after round 04: Looser EMA guard restores many trades but only NAS passes, below the low-efficiency-only branch. Do not keep adding trend conditions to rescue the event. Return to round2 and test whether its12bar time cap cuts delayed mean reversion.

## Round 05

Hypothesis: Low-efficiency failed breaks may need a full observed day to complete reversion.

Change: Increase maximum holding12to24bars, preserving midpoint exit and2%target.

Expected lesson: Is poor performance partly caused by the initial time cap rather than entry selection?

Observed: 4/21 pass; 1 additional positive-score instruments fail monthly frequency; 16/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades 17,730; ranking [4, 0.014053221046650386, -0.045178283895699535]; run `9bb843a118ff0d792100`; audit passed. Passing: CN50_USD, NZD_USD, SPX500_USD, UK100_GBP.

Post-result lesson after round 05: Holding24bars adds NZD and raises passing breadth3to4, but worsens median all-instrument losses and several index/commodity scores. Keep this selective improvement as a branch; test whether the2%profit target truncates the rare larger reversals rather than assuming every longer hold helps.

## Round 06

Hypothesis: Failed breaks can occasionally lead to extended reversals, so an absolute profit cap may reduce their payoff.

Change: Remove2%profit target from the24bar low-efficiency sweep branch; retain midpoint exit.

Expected lesson: Determine whether winner truncation explains the payoff weakness while retaining the hard2%adverse stop.

Observed: 4/21 pass; 0 additional positive-score instruments fail monthly frequency; 17/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades 17,665; ranking [4, 0.01435091728592211, -0.036100848241318796]; run `5a6465b4e3e77e76328a`; audit passed. Passing: CN50_USD, NZD_USD, SPX500_USD, UK100_GBP.

Post-result lesson after round 06: Removing the profit cap keeps4passes and modestly improves median passing and median-all scores, while losing AUD positivity. Payoff truncation is a secondary issue, not a broad rescue. The best branch still fades sweeps that close barely inside their broken boundary; next require a more convincing return inside before entry.

## Round 07

Hypothesis: A failed range break that closes decisively back inside may have stronger reversal information than a marginal rejection.

Change: Require long close above lower quarter and short close below upper quarter, still before midpoint exit.

Expected lesson: Test rejection-close quality while preserving the causal sweep event and avoiding entry/exit overlap.

Observed: 0/21 pass; 11 additional positive-score instruments fail monthly frequency; 10/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades 3,110; ranking [0, 0.0, 0.0006918480554120039]; run `6113524f63a64c32f03f`; audit passed. Passing: none.

Post-result lesson after round 07: Strong rejection closes make11instruments positive and median-all slightly positive, but the event is too rare: zero passes,4to40empty months. Close quality has information but a quarter-range penetration is incompatible with required monthly opportunities. Test a modest10%penetration rather than keeping this overfilter.

## Round 08

Hypothesis: A modest10%return inside the swept range may filter marginal failures without sacrificing every-month entries.

Change: Relax rejection penetration from25%to10%of the prior range.

Expected lesson: Find whether the close-quality gain can survive the monthly opening requirement.

Observed: 0/21 pass; 6 additional positive-score instruments fail monthly frequency; 15/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades 10,526; ranking [0, 0.0, -0.01583724391349547]; run `08100c883081bc463ea9`; audit passed. Passing: none.

Post-result lesson after round 08: Even10%penetration prevents every positive instrument from satisfying monthly activity, despite reducing many losses. The winner remains round6. Instead of further adding conditions, loosen its efficiency context to recover opportunity and test whether the original .25bound was needlessly restrictive.

## Round 09

Hypothesis: Failed breaks may revert within moderately inefficient paths as well as very flat ones.

Change: Relax efficiency ceiling0.25to0.4 on the no-target24bar branch, without rejection-penetration filter.

Expected lesson: Test whether broader monthly opportunity improves useful passing coverage or simply adds trend-fading losses.

Observed: 4/21 pass; 0 additional positive-score instruments fail monthly frequency; 17/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades 23,075; ranking [4, 0.019587545732859382, -0.03769765695924182]; run `ed8f5f5fb1ef4e497230`; audit passed. Passing: AUD_USD, NZD_USD, SPX500_USD, UK100_GBP.

Post-result lesson after round 09: Efficiency<.4 restores every-month opportunity for AUD and raises median passing score while retaining4passes, but loses CN50 and worsens crypto losses. The effect may be dominated by side asymmetry; next separate long and short sweep fades rather than attributing the combined result to a universal reversal edge.

## Round 10

Hypothesis: Long failed-downside breaks may carry a different payoff from failed-upside breaks over this historical instrument set.

Change: Long-only attribution of the best symmetric branch; all21instruments remain in evaluation.

Expected lesson: Determine whether short fades explain the broadly negative combined returns and whether long-only monthly frequency remains adequate.

Observed: 2/21 pass; 2 additional positive-score instruments fail monthly frequency; 17/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades 11,534; ranking [2, 0.04508013239307253, -0.01066753959143609]; run `a1d0b3eb4beaa450ed83`; audit passed. Passing: SPX500_USD, US30_USD.

Post-result lesson after round 10: Long-only improves median-all but reduces passing breadth4to2; JP225 and NAS are positive yet miss months. This direction does not simply inherit a broad long-side advantage. Complete the short attribution control to identify whether symmetric passes rely on distinct sides or on combined opening coverage.

## Round 11

Hypothesis: Short failed-upside breaks may explain the FX and UK-index passes in the combined branch.

Change: Short-only attribution of round9, preserving event/efficiency/exit rules.

Expected lesson: Separate side-specific profitability from coverage benefits of allowing both entry directions.

Observed: 2/21 pass; 2 additional positive-score instruments fail monthly frequency; 17/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades 12,196; ranking [2, 0.01578683136580258, -0.03936360972216012]; run `109e4cccf5afb2ce9121`; audit passed. Passing: CN50_USD, UK100_GBP.

Post-result lesson after round 11: Short-only also yields2passes, CN50 and UK100, while AUD/NZD are positive but miss months. The best symmetric branch combines distinct side-specific outcomes and monthly opportunities, not broad profitability. Return to it and test whether an extra close of rejection confirmation improves noise without the severe quarter-range filter.

## Round 12

Hypothesis: A failed break followed by one more close inside the same range half may confirm rejection before fading.

Change: Delay the full round9 event by one observed confirmation bar; maintain inside-range and efficiency context on confirmation.

Expected lesson: Test temporal confirmation rather than demanding a large same-bar recovery; moving boundaries remain a disclosed approximation.

Observed: 5/21 pass; 0 additional positive-score instruments fail monthly frequency; 16/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades 19,914; ranking [5, 0.019303377850866388, -0.03672770456063909]; run `9c87b47389285ae5a16e`; audit passed. Passing: AUD_USD, CN50_USD, NZD_USD, SPX500_USD, UK100_GBP.

Post-result lesson after round 12: One confirmation bar raises symmetric breadth4to5 and improves several passing scores without creating new monthly failures among them. Most instruments still lose. Test a second confirmation bar as a local timing control before treating one bar as an optimum.

## Round 13

Hypothesis: Two consecutive inside-range closes after a failed break may reject more false reversals than one.

Change: Increase post-sweep confirmation1to2bars, preserving event and context.

Expected lesson: Assess whether the improvement survives a neighboring timing setting or depends on a narrow confirmation delay.

Observed: 4/21 pass; 1 additional positive-score instruments fail monthly frequency; 16/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades 16,873; ranking [4, 0.02612999832929863, -0.014187843384739905]; run `339e13d07dd5e09309e4`; audit passed. Passing: NZD_USD, SPX500_USD, UK100_GBP, US30_USD.

Post-result lesson after round 13: Two-bar confirmation improves median-all but reduces passes5to4 and swaps AUD/CN50 for US30; JP225 remains positive but misses a month. Thus timing is not a monotonic improvement. Keep the one-bar winner and test whether quote activity at the rejection adds participation information.

## Round 14

Hypothesis: A failed range break with above-baseline quote activity may represent stronger rejection than a quiet sweep.

Change: Require activity ratio>1on the original failed-break event; keep one-bar confirmation.

Expected lesson: Measure participation information and its frequency cost without treating quote activity as true market-wide order flow.

Observed: 3/21 pass; 1 additional positive-score instruments fail monthly frequency; 17/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades 14,759; ranking [3, 0.03249377749267428, -0.021270438235371412]; run `f8915c7161c219e45242`; audit passed. Passing: NZD_USD, SPX500_USD, UK100_GBP.

Post-result lesson after round 14: Above-baseline activity reduces breadth5to3 and creates AUD monthly gaps, though it reduces losses on several instruments. Activity is not a sufficient rescue and does not add passing assets. Return to the winner and reject extreme RSI conditions at confirmation instead of filtering event participation.

## Round 15

Hypothesis: A confirmed failed break may be safer to fade after extreme RSI pressure has eased.

Change: At confirmation require long RSI>35 and short RSI<65.

Expected lesson: Test whether continuing extreme directional pressure explains remaining false reversals while preserving monthly opportunity.

Observed: 4/21 pass; 2 additional positive-score instruments fail monthly frequency; 15/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades 16,821; ranking [4, 0.020532729005192544, -0.027951434273815745]; run `199c981f0f75fff24033`; audit passed. Passing: NZD_USD, SPX500_USD, UK100_GBP, US30_USD.

Post-result lesson after round 15: The RSI pressure guard gives6positive instruments but only4passes; AUD/CN50 lose a monthly opening and the best5pass branch remains unchanged. Selection keeps reducing coverage. Now isolate the exit rule: perhaps a moving midpoint closes winners too early or creates arbitrary exits as the range rolls.

## Round 16

Hypothesis: A confirmed failed break may carry a longer reversal payoff than a moving-midpoint exit captures.

Change: Remove midpoint indicator exits; use fixed24bar maximum with the same mandatory2%stop and no profitcap.

Expected lesson: Separate entry-event value from moving-boundary exit behavior while retaining a bounded holding horizon.

Observed: 9/21 pass; 1 additional positive-score instruments fail monthly frequency; 11/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades 14,757; ranking [9, 0.02161879804892544, -0.0055098245728274365]; run `9b051d128b92b9aab12e`; audit passed. Passing: AUD_USD, BCO_USD, BTC_USD, ETH_USD, SPX500_USD, UK100_GBP, US30_USD, WTICO_USD, XAU_USD.

Post-result lesson after round 16: Removing moving-midpoint exits creates the largest gain:5to9passes, flipping BCO/BTC/ETH/WTICO/XAU positive and reducing the median-all loss to0.55%/year. This is evidence against the original exit rather than proof of broad entry edge. Test shorter and longer neighboring fixed horizons before selecting it.

## Round 17

Hypothesis: A shorter fixed horizon may retain reversal gains without exposing failed breaks to later renewed trends.

Change: Shorten no-indicator-exit horizon24to12bars.

Expected lesson: Check whether the fixed-horizon improvement survives a shorter hold and measure its trade frequency/payoff effect.

Observed: 3/21 pass; 1 additional positive-score instruments fail monthly frequency; 17/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades 19,368; ranking [3, 0.00926877240534356, -0.03420347353617411]; run `b6b0bd0f9be6e6b0228c`; audit passed. Passing: AUD_USD, SPX500_USD, UK100_GBP.

Post-result lesson after round 17: The12bar fixed hold collapses9passes to3 and turns commodities/crypto negative again, so the improvement is horizon-sensitive. This control argues against calling the sweep event uniformly useful at all short horizons. Test48bars to see whether a slower reversal rather than arbitrary24bar tuning explains the gain.

## Round 18

Hypothesis: Failed breaks may resolve over two observed days when midpoint exits are avoided.

Change: Lengthen fixed horizon24to48bars with unchanged entry and stop.

Expected lesson: Distinguish a slower reversal payoff from a narrow24bar result; inspect monthly coverage and losses on all21.

Observed: 9/21 pass; 0 additional positive-score instruments fail monthly frequency; 12/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades 10,565; ranking [9, 0.047041666365020614, -0.007023438890463908]; run `684c24a30a2b69da3a08`; audit passed. Passing: AUD_USD, CN50_USD, GBP_USD, NZD_USD, SPX500_USD, UK100_GBP, US30_USD, USD_CAD, WTICO_USD.

Post-result lesson after round 18: The48bar hold retains9passes and raises median passing score from2.16%to4.70%/year, but the passing set changes substantially: commodities/crypto lose places to FX/CN50. This is broader horizon evidence but not stable asset-level behavior. Use the final two rounds to attribute sides on this new winning exit branch.

## Round 19

Hypothesis: Long-side confirmed failed breaks may account for most gains under the48bar fixed exit.

Change: Long-only attribution of the no-midpoint48bar winner.

Expected lesson: Check whether the improved branch is mainly long exposure and whether losing short entries were masking its coverage.

Observed: 9/21 pass; 6 additional positive-score instruments fail monthly frequency; 6/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades 7,313; ranking [9, 0.030745717434200494, 0.029587231567135563]; run `dea823d228e4830946bb`; audit passed. Passing: BCO_USD, BTC_USD, DE30_EUR, ETH_USD, USD_CAD, USD_JPY, WTICO_USD, XAG_USD, XAU_USD.

Post-result lesson after round 19: Long-only yields15positive instruments and a positive median-all2.96%/year, but6positive instruments miss complete months, leaving9passes. Its passing set differs sharply from the symmetric winner. The monthly condition is now the main limiter for this more promising long-only branch; finish short attribution to quantify the opposing contribution.

## Round 20

Hypothesis: Short-side failed-upside breaks may contribute selective FX reversion but impair the long reversal payoff.

Change: Short-only attribution of the48bar no-midpoint branch.

Expected lesson: Complete directional attribution, retain the best symmetric and long-only alternatives, and guide nextstage toward genuine frequency/payoff tradeoffs.

Observed: 1/21 pass; 3 additional positive-score instruments fail monthly frequency; 17/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades 7,621; ranking [1, 0.006086837499753806, -0.03983817985593127]; run `8229a6bc69b2753e2b5f`; audit passed. Passing: USD_CAD.

Post-result lesson after round 20: Short-only gives just1pass and a negative median-all, while long-only produces15positive instruments but6monthly failures. Phase1winner by the declared ranking is symmetric48bar round18(9passes,medianpassing4.70%/year); long-only round19 is the stronger broad-score alternative but lacks monthly coverage. Nextstage should address its frequency without restoring the damaging moving-midpoint exit, and examine neighboring48bar horizons rather than assuming a narrow optimum.
