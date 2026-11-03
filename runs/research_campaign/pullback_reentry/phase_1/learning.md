
## Round 1

Hypothesis: RSI recovery following a recent pullback within an EMA trend can resume continuation.

Change: Reproduce original direction baseline as the first audited campaign control.

Expected lesson: Establish whether marginal scores or missing months are the binding constraints before changing entry timing.

Observed: 3/21 pass; 1 additional positive-score instruments fail monthly frequency; 17/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades: 14,329. Ranking: [3, 0.02635102415088236, -0.03119193317709156]. Passing instruments: DE30_EUR, NAS100_USD, USD_JPY. Run `e9b88c1f4498afd65aae`.

Post-result lesson and next decision after round 1: Baseline reproduces three passes but the median across instruments is negative; JP225 is positive with one empty complete month. First test whether the extra recovery confirmation bar delays entry and suppresses monthly opportunity.

## Round 2

Hypothesis: A single confirmed RSI recovery close may capture trend resumption sooner than two closes.

Change: Reduce RSI recovery held_for from two bars to one; keep all other baseline rules.

Expected lesson: If confirmation latency is costly, earlier entries should improve breadth without requiring looser pullback depth.

Observed: 4/21 pass; 1 additional positive-score instruments fail monthly frequency; 16/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades: 15,051. Ranking: [4, 0.026567108334317874, -0.024686944402437898]. Passing instruments: DE30_EUR, NAS100_USD, USD_JPY, WTICO_USD. Run `abc1eb9f4d0ba08b1035`.

Post-result lesson and next decision after round 2: One recovery close improves passes from3 to4, raises the median passing score slightly and improves the all-instrument median. Earlier timing is currently better. A deliberately slower control will test whether this is a monotonic timing effect rather than an accidental one-step gain.

## Round 3

Hypothesis: Three recovery closes may suppress false recoveries enough to offset delayed fills.

Change: Increase baseline recovery confirmation from two to three closes as a slower control.

Expected lesson: Compare early and late confirmation before selecting the entry branch to refine.

Observed: 4/21 pass; 0 additional positive-score instruments fail monthly frequency; 17/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades: 12,656. Ranking: [4, 0.008275080899027846, -0.03021388309615228]. Passing instruments: DE30_EUR, HK33_HKD, NAS100_USD, USD_JPY. Run `b86867380e2526cff331`.

Post-result lesson and next decision after round 3: Three-close control reaches four passes but materially weakens the median passing score; one-close round2 remains the better branch. JP225 monthly failure persisted in round2, so next broaden the pullback recognition window without changing depth or trend filters.

## Round 4

Hypothesis: A twelve-bar pullback memory may recover opportunities lost when RSI recovery takes longer than six bars.

Change: Extend the recent-pullback window6 to12 on the one-close recovery branch.

Expected lesson: Test whether monthly coverage improves before weakening the economic definition of a pullback.

Observed: 4/21 pass; 0 additional positive-score instruments fail monthly frequency; 17/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades: 23,690. Ranking: [4, 0.035675690075354385, -0.028113131735016228]. Passing instruments: HK33_HKD, NAS100_USD, USD_JPY, WTICO_USD. Run `92c275208795905ddcf8`.

Post-result lesson and next decision after round 4: Longer memory preserves four passes and raises median passing score to3.57%/year, but changes the passing set and leaves the typical instrument negative. Next test shallower pullbacks to distinguish an activity shortage from reversal-contamination in deep pullbacks.

## Round 5

Hypothesis: Shallow RSI excursions around neutral may be safer trend pullbacks than deeper countertrend moves.

Change: Change recent RSI pullback thresholds45/55 to48/52 on round4.

Expected lesson: Determine whether shallower pullbacks improve broad profitability rather than merely trading more often.

Observed: 6/21 pass; 0 additional positive-score instruments fail monthly frequency; 15/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades: 29,672. Ranking: [6, 0.03173384544110885, -0.03395555652343686]. Passing instruments: DE30_EUR, HK33_HKD, NAS100_USD, USD_JPY, WTICO_USD, XAU_USD. Run `2b6d0940808ffed68e90`.

Post-result lesson and next decision after round 5: Shallower pullbacks broaden passing coverage from4 to6, adding DE30/XAU, although the all-instrument median worsens. Test a deeper-pullback control before accepting the shallow-pullback interpretation; a few big markets still dominate the useful evidence.

## Round 6

Hypothesis: Deeper RSI pullbacks could improve entry price enough to compensate for more trend failures.

Change: Test RSI40/60 depth against round4, keeping twelve-bar memory and single-close recovery.

Expected lesson: Use an opposite-direction depth control to check whether the shallow-entry benefit is economically coherent.

Observed: 5/21 pass; 3 additional positive-score instruments fail monthly frequency; 13/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades: 13,272. Ranking: [5, 0.01687077885021787, -0.011295253902180316]. Passing instruments: HK33_HKD, NAS100_USD, NZD_USD, US30_USD, USD_JPY. Run `2069d2c902cbd4fd0ce2`.

Post-result lesson and next decision after round 6: Deeper pullbacks reduce median losses acrossall21 to-1.13%/yr and produce8positive instruments, but monthly gaps leave5passes. Shallow round5 remains breadth winner. Next remove the slow EMA60 location filter to see whether it rejects legitimate early trend resumptions.

## Round 7

Hypothesis: Fast EMA trend plus shallow RSI recovery may be sufficient without requiring price already beyond EMA60.

Change: Remove only the EMA60-distance entry filter from round5.

Expected lesson: Test whether the slow trend-location gate improves entry quality or merely delays recoveries.

Observed: 4/21 pass; 0 additional positive-score instruments fail monthly frequency; 17/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades: 32,925. Ranking: [4, 0.04418895930682247, -0.05307034998599571]. Passing instruments: HK33_HKD, NAS100_USD, USD_JPY, XAU_USD. Run `d59efa5b7bad149b1d13`.

Post-result lesson and next decision after round 7: Removing EMA60 location reduces breadth from6 to4 and worsens the all-instrument median to-5.31%/yr; the slow trend gate appears useful on this branch. Retain it and test whether independent Supertrend agreement improves quality without sacrificing monthly coverage.

## Round 8

Hypothesis: Shallow RSI pullbacks may work better when both EMA trend and Supertrend direction agree.

Change: Add Supertrend-direction agreement to round5 without changing recovery or exits.

Expected lesson: Check whether an additional causal trend filter removes losing recoveries or creates sparse over-filtered opportunities.

Observed: 5/21 pass; 0 additional positive-score instruments fail monthly frequency; 16/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades: 24,672. Ranking: [5, 0.06403704569154563, -0.03731640948934897]. Passing instruments: DE30_EUR, HK33_HKD, NAS100_USD, USD_JPY, XAU_USD. Run `ece019261bf57a943b97`.

Post-result lesson and next decision after round 8: Supertrend agreement increases median passing score to6.40%/yr but drops breadth from6 to5, losing WTICO. Keep it as a quality branch while retaining round5 as breadth winner. Next isolate exit horizon: perhaps recoveries lose their edge before the24-bar timeout.

## Round 9

Hypothesis: Pullback recovery edge may be concentrated in the first twelve observed bars.

Change: Reduce maximum holding24 to12 on the broadest shallow-pullback branch.

Expected lesson: Separate entry-quality improvements from whether lingering trades give back the resumption move.

Observed: 2/21 pass; 0 additional positive-score instruments fail monthly frequency; 19/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades: 32,529. Ranking: [2, 0.07527331646693568, -0.060837095343805554]. Passing instruments: HK33_HKD, WTICO_USD. Run `2277789c357befd4452a`.

Post-result lesson and next decision after round 9: Twelve-bar exits sharply reduce passing breadth6to2 and worsen typical score; early timeout appears to truncate the resumption component rather than rescue noise. Test the opposite longer horizon while preserving EMA reversal exits.

## Round 10

Hypothesis: Giving established pullback resumptions up to48bars may retain more directional continuation.

Change: Increase round5 maximum hold24to48; keep EMA reversal exit and3% target.

Expected lesson: Check whether patience, rather than more entry filtering, improves broad outcomes.

Observed: 5/21 pass; 0 additional positive-score instruments fail monthly frequency; 16/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades: 27,836. Ranking: [5, 0.06110970813377229, -0.0356907652140061]. Passing instruments: HK33_HKD, NAS100_USD, USD_JPY, WTICO_USD, XAU_USD. Run `28c85b1febc40d1e10a2`.

Post-result lesson and next decision after round 10: Longer48-bar hold lifts payoff in several passing markets but loses DE30 and does not improve the typical instrument. Round5 remains breadth winner. Test whether its3% target clips winning tails while maintaining the24-bar limit and mandatory stop.

## Round 11

Hypothesis: Removing the fixed profit cap may preserve rare strong trend resumptions.

Change: Remove only the3% take-profit target from round5; keep24-bar and EMA reversal exits.

Expected lesson: Measure whether capped winners explain broad weakness without changing entry selection.

Observed: 7/21 pass; 0 additional positive-score instruments fail monthly frequency; 14/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades: 28,698. Ranking: [7, 0.032954250304551264, -0.04120289809535356]. Passing instruments: BCO_USD, DE30_EUR, HK33_HKD, NAS100_USD, USD_JPY, XAG_USD, XAU_USD. Run `b8f4ebb4c06f004aa033`.

Post-result lesson and next decision after round 11: Uncapping profits raises breadth6to7, adding BCO/XAG but losing WTICO; typical instrument loss worsens. Tail capture matters in selected markets. Before refining that branch, test a smaller target as an opposite payoff-shape control.

## Round 12

Hypothesis: A smaller1.5% target may monetize short pullback bursts before they reverse.

Change: Halve round5 take-profit3%to1.5%, keeping entry and24-bar hold fixed.

Expected lesson: Distinguish frequent small recovery capture from dependence on occasional large winners.

Observed: 3/21 pass; 0 additional positive-score instruments fail monthly frequency; 18/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades: 32,104. Ranking: [3, 0.020219774320336947, -0.05513831586517386]. Passing instruments: HK33_HKD, NAS100_USD, USD_JPY. Run `27e30e07b82aace7adec`.

Post-result lesson and next decision after round 12: Smaller target cuts passing breadth7-best to3 and worsens the median. The entry appears to need winning tails. Combine uncapped profits with the independently useful Supertrend quality filter from round8, without altering horizon.

## Round 13

Hypothesis: Supertrend agreement may improve the quality of uncapped pullback continuation winners.

Change: Combine no profit cap from round11 with Supertrend entry agreement tested in round8.

Expected lesson: Test whether the two separately helpful ideas complement rather than merely overlap.

Observed: 7/21 pass; 0 additional positive-score instruments fail monthly frequency; 14/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades: 23,938. Ranking: [7, 0.0625564691440896, -0.043045263408431705]. Passing instruments: BCO_USD, DE30_EUR, HK33_HKD, NAS100_USD, USD_JPY, XAG_USD, XAU_USD. Run `c06901923479cd0ed695`.

Post-result lesson and next decision after round 13: The combination retains all7passing instruments and raises their median score3.30%to6.26%/yr, making it current winner. Broad median remains-4.30%, so this is selective improvement. Longer holding previously improved payoff; test it now on this uncapped quality branch.

## Round 14

Hypothesis: Uncapped pullback continuations with independent trend agreement may benefit from48-bar patience.

Change: Extend round13 max holding24to48 without changing entries or exit indicator.

Expected lesson: Determine whether the earlier longer-hold payoff gain persists after eliminating the fixed profit cap.

Observed: 9/21 pass; 0 additional positive-score instruments fail monthly frequency; 12/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades: 22,320. Ranking: [9, 0.06312719677829437, -0.03921365448987831]. Passing instruments: BCO_USD, DE30_EUR, ETH_USD, HK33_HKD, NAS100_USD, USD_JPY, WTICO_USD, XAG_USD, XAU_USD. Run `b89349b6e0b8e7859dcd`.

Post-result lesson and next decision after round 14: Longer48-bar holding on the uncapped quality branch expands passing breadth7to9 and keeps median pass score6.31%/yr; ETH/WTICO join. Scores in BCO/WTICO are large, so dependence on rare commodity trends needs later review. Next test whether the EMA reversal exit is prematurely ending Supertrend-aligned positions.

## Round 15

Hypothesis: Using the same slower trend state for continuation exits may retain pullback winners that survive fast EMA reversals.

Change: Replace EMA624 reversal exit with opposite Supertrend direction on round14.

Expected lesson: Measure sensitivity to exit definition without changing48-bar horizon, entries or mandatory stop.

Observed: 10/21 pass; 0 additional positive-score instruments fail monthly frequency; 11/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades: 17,769. Ranking: [10, 0.05674891465130097, -0.00939566327949661]. Passing instruments: BCO_USD, DE30_EUR, HK33_HKD, NAS100_USD, SPX500_USD, USD_CHF, USD_JPY, WTICO_USD, XAG_USD, XAU_USD. Run `10165a4ebd45ad985355`.

Post-result lesson and next decision after round 15: Slower Supertrend exit improves breadth9to10 and typical score materially, approaching zero median acrossall21. ETH loses its pass but SPX/USDCHF become positive. Test one modest path-quality condition to see whether weak noisy trends explain the remaining losses.

## Round 16

Hypothesis: A modest24-bar directional-efficiency floor may remove noisy apparent-trend pullbacks.

Change: Add efficiency24>0.15 to round15 entries; preserve all exits and horizon.

Expected lesson: Check whether regime quality improves the typical instrument without causing empty months.

Observed: 9/21 pass; 0 additional positive-score instruments fail monthly frequency; 12/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades: 14,589. Ranking: [9, 0.07322348030287451, -0.004832845928755391]. Passing instruments: BCO_USD, DE30_EUR, ETH_USD, HK33_HKD, NAS100_USD, USD_JPY, WTICO_USD, XAG_USD, XAU_USD. Run `ee85febbe5884f52af1b`.

Post-result lesson and next decision after round 16: Efficiency filtering improves the typical score slightly but cuts passing breadth10to9; SPX/USDCHF disappear while ETH gains a large score. Retain unfiltered round15 as breadth winner. Test whether slightly earlier RSI recovery retains the entry-timing benefit found in round2.

## Round 17

Hypothesis: Recovery just before RSI reaches neutral may capture resumption with less latency while still requiring a prior pullback.

Change: Change recovery threshold50/50 to49/51 on round15; keep pullback48/52.

Expected lesson: Check a close timing neighbor instead of adding another selective filter.

Observed: 10/21 pass; 0 additional positive-score instruments fail monthly frequency; 11/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades: 17,832. Ranking: [10, 0.054301481913568435, -0.009586246322060068]. Passing instruments: BCO_USD, DE30_EUR, HK33_HKD, NAS100_USD, SPX500_USD, USD_CHF, USD_JPY, WTICO_USD, XAG_USD, XAU_USD. Run `b728737a2239bd65db2d`.

Post-result lesson and next decision after round 17: Slightly earlier49/51 recovery leaves the same10passing instruments and slightly weaker median than50; the winner is locally stable to this timing neighbor. Next inspect directional asymmetry with a universal long-only control, not asset-specific selection.

## Round 18

Hypothesis: Long pullback resumptions may contribute differently from short resumptions across the shared history.

Change: Remove short entries globally from round15; every instrument still receives the same long-only rule.

Expected lesson: Attribute improvements to directional asymmetry and distinguish them from a genuinely symmetric pullback effect.

Observed: 13/21 pass; 1 additional positive-score instruments fail monthly frequency; 7/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades: 9,371. Ranking: [13, 0.08318175451706959, 0.02312749503264805]. Passing instruments: BCO_USD, BTC_USD, DE30_EUR, ETH_USD, HK33_HKD, NAS100_USD, SPX500_USD, UK100_GBP, US30_USD, USD_JPY, WTICO_USD, XAG_USD, XAU_USD. Run `00d5575a38e5bda33229`.

Post-result lesson and next decision after round 18: Long-only control expands breadth10to13 and turns the all-instrument median positive2.31%/yr; JP225 remains positive but fails monthly frequency. This is strong directional asymmetry and may reflect the historical upward bias of indices/commodities rather than a universal symmetric edge. Test short-only attribution before refining the long branch.

## Round 19

Hypothesis: Short pullback resumptions may be the principal source of losses in the symmetric strategy.

Change: Remove long entries globally from round15 as the paired directional attribution control.

Expected lesson: Compare both one-sided controls against the symmetric parent without pooling instrument returns.

Observed: 4/21 pass; 2 additional positive-score instruments fail monthly frequency; 15/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades: 9,196. Ranking: [4, 0.00773784130761713, -0.027820844190566085]. Passing instruments: BCO_USD, DE30_EUR, USD_CHF, USD_JPY. Run `951d8dc4f60c4d352da6`.

Post-result lesson and next decision after round 19: Short-only has only4passes and a negative2.78%/yr median, versus13passes and positive2.31%median long-only. The improvement is materially directional. Use the final phase1 round to check the strongest long branch with a broader pullback-memory neighbor, targeting residual missing opportunities rather than another side switch.

## Round 20

Hypothesis: A broader memory of shallow pullbacks may retain long resumption opportunities that develop more slowly.

Change: Extend only the long-only round18 pullback memory12to18 observed bars.

Expected lesson: Check whether breadth improvement is stable to entry-context duration and whether JP225 empty months can be reduced.

Observed: 12/21 pass; 1 additional positive-score instruments fail monthly frequency; 8/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Trades: 9,939. Ranking: [12, 0.08890545460991521, 0.038247025645769525]. Passing instruments: BCO_USD, BTC_USD, DE30_EUR, ETH_USD, NAS100_USD, SPX500_USD, UK100_GBP, US30_USD, USD_JPY, WTICO_USD, XAG_USD, XAU_USD. Run `d5e07900b6a00a3e9afc`.

Post-result lesson and next decision after round 20: Extending pullback memory12to18 loses the small HK33 pass, leaving12passes, while median score acrossall21 improves to3.82%/yr. Breadth-first rank still selects round18 with13passes. The strong branch is not a universal symmetric finding: long-only regime exposure is central, forex remains weak, and JP225 still has missing months.
