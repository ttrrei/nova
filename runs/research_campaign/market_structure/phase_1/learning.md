# Market structure phase one learning

All rounds use causal rolling range boundaries, all21 instruments and full hourly history, fixed execution and mandatory2% stop. No future pivots are inferred.

## Round 1

Hypothesis: A prior24-bar range break confirmed for two following outer-quarter closes may continue.

Change: Reproduce original two-close outer-quarter confirmation and midpoint exit.

Expected learning: Establish score versus monthly-frequency failures before altering confirmation.

Observed: 17,385 trades; 5/21 pass; 5/21 positive. Ranking [5, 0.02897969745148324, -0.035839204566767785]. Run `7ae01c4d167a24bad743`; audit passed.

Passing: DE30_EUR, SPX500_USD, US30_USD, USD_JPY, XAU_USD.

Post-result lesson and next decision after round 1: Baseline reproduces five passes and every complete month has openings on all21. Profitability is binding, not frequency. Test whether one less confirmation close improves entry timing before adding filters.

## Round 2

Hypothesis: A single outer-quarter confirmation close may enter structural continuation earlier.

Change: Reduce post-break confirmation from two following closes to one.

Expected learning: Distinguish confirmation latency from failed-break rejection quality.

Observed: 19,718 trades; 5/21 pass; 5/21 positive. Ranking [5, 0.014502849375802328, -0.04107362147577752]. Run `c71bf9bc4597f844d4eb`; audit passed.

Passing: DE30_EUR, US30_USD, USD_JPY, WTICO_USD, XAU_USD.

Post-result lesson and next decision after round 2: One-close confirmation keeps five passes but halves their median score and worsens median-all; it swaps SPX for WTICO. Baseline timing remains preferable. Test one additional confirmation close to see whether rejection quality improves with patience.

## Round 3

Hypothesis: Three outer-quarter closes may better distinguish structural acceptance from a brief range break.

Change: Increase confirmation from two following closes to three.

Expected learning: Compare both sides of the baseline delay before changing exit rules.

Observed: 15,411 trades; 4/21 pass; 4/21 positive. Ranking [4, 0.03450902691046576, -0.021564733834818866]. Run `fdb79786b7072bfae101`; audit passed.

Passing: DE30_EUR, US30_USD, USD_JPY, XAU_USD.

Post-result lesson and next decision after round 3: Three-close delay loses one passing instrument and starts a monthly gap in JP225, despite improving some losing scores. Two-close baseline is still the better breadth/score branch. Shift to whether the fixed target truncates successful structural breaks.

## Round 4

Hypothesis: Uncapped structural continuation may recover losses from prematurely truncated large winners.

Change: Remove4%takeprofit only; retain midpoint exit and36-bar cap.

Expected learning: Isolate profit-cap effects while preserving confirmation timing and losing exits.

Observed: 16,440 trades; 6/21 pass; 6/21 positive. Ranking [6, 0.025151210818835083, -0.0326345289297631]. Run `17fad5515028ae36d9b8`; audit passed.

Passing: BTC_USD, DE30_EUR, US30_USD, USD_JPY, WTICO_USD, XAU_USD.

Post-result lesson and next decision after round 4: Removing the target increases passes5to6 and reverses BTC from negative to14.24%/year; median-all improves only slightly and SPX loses its marginal positivity. Profit-cap truncation is plausible but not sufficient. Test whether range-break direction also needs established-trend agreement.

## Round 5

Hypothesis: A confirmed structural range break on the established-trend side of EMA60 may avoid countertrend failures.

Change: Add EMA60-side agreement to both uncapped structural entries.

Expected learning: Check whether a modest trend gate improves profitability without losing monthly coverage.

Observed: 16,009 trades; 5/21 pass; 5/21 positive. Ranking [5, 0.03704896398171509, -0.017456055436096258]. Run `034cf3df5ba82a736352`; audit passed.

Passing: BTC_USD, DE30_EUR, US30_USD, USD_JPY, XAU_USD.

Post-result lesson and next decision after round 5: EMA60 agreement improves the all-instrument median from-3.26%to-1.75%/year but reduces passes6to5 by making WTICO marginally negative. Retain as a diagnostic branch, not the winner. The uncapped branch still has a36bar hard horizon: test a slower cap before adding more entry filters.

## Round 6

Hypothesis: Allowing established range breaks more time may preserve longer structural continuation.

Change: Extend uncapped maximum holding36→72bars.

Expected learning: Separate premature time exits from midpoint failures while entry remains unchanged.

Observed: 15,637 trades; 6/21 pass; 6/21 positive. Ranking [6, 0.01843976621043257, -0.03306941351400733]. Run `1d19b2ee86a95db0cbbb`; audit passed.

Passing: BTC_USD, DE30_EUR, US30_USD, USD_JPY, XAG_USD, XAU_USD.

Post-result lesson and next decision after round 6: The72bar cap retains six passes but lowers the passing median and swaps WTICO for XAG; slower is not broadly better. Test a shorter18bar cap on the same uncapped entry to complete the horizon-direction diagnosis.

## Round 7

Hypothesis: Shorter structural continuation horizons may capture range acceptance before later reversal.

Change: Shorten uncapped maximum holding36→18bars.

Expected learning: Check whether continuation value is concentrated soon after confirmation rather than at long horizons.

Observed: 19,013 trades; 8/21 pass; 8/21 positive. Ranking [8, 0.021768043688054795, -0.02077800092251395]. Run `7e0f2b1298512217a838`; audit passed.

Passing: BTC_USD, DE30_EUR, NAS100_USD, SPX500_USD, US30_USD, USD_JPY, WTICO_USD, XAU_USD.

Post-result lesson and next decision after round 7: The18bar uncapped horizon improves breadth6to8 and restores NAS/SPX while keeping every complete month populated. It reduces BTC upside but helps several losing instruments. Revisit the previously mixed EMA60 filter on this newly better horizon to test an interaction supported by earlier observations.

## Round 8

Hypothesis: Established-trend agreement may work better when structural trades use the shorter observed useful horizon.

Change: Add EMA60-side agreement to18bar uncapped branch.

Expected learning: Check whether the earlier mixed trend-filter effect depends on exit timing.

Observed: 18,552 trades; 9/21 pass; 9/21 positive. Ranking [9, 0.017383006881090023, -0.020886874354028015]. Run `9caffa95c460112f9290`; audit passed.

Passing: BCO_USD, BTC_USD, DE30_EUR, NAS100_USD, SPX500_USD, US30_USD, USD_JPY, WTICO_USD, XAU_USD.

Post-result lesson and next decision after round 8: EMA60 agreement now increases breadth8to9 by adding BCO, so its effect is horizon-dependent. Median-all remains negative and several FX/indices still lose. Test whether exceptionally efficient already-mature paths are poor places for a newly confirmed structure entry.

## Round 9

Hypothesis: Confirmed breaks outside already-mature efficient paths may avoid late structural entries.

Change: Exclude efficiency24>=0.5 at entry.

Expected learning: Distinguish mature-move exhaustion from simple range acceptance.

Observed: 17,531 trades; 7/21 pass; 7/21 positive. Ranking [7, 0.026510620941824287, -0.02797692105405425]. Run `abb179f4b75d98107410`; audit passed.

Passing: BTC_USD, DE30_EUR, NAS100_USD, SPX500_USD, US30_USD, USD_JPY, XAU_USD.

Post-result lesson and next decision after round 9: Excluding mature efficiency reduces breadth9to7 and worsens median-all; BCO/WTICO and ETH especially deteriorate. This continuation family benefits from some efficient moves, so reject that filter. Test activity participation at confirmation as a different structural-quality input.

## Round 10

Hypothesis: Structural acceptance with above-average quote participation may persist more often.

Change: Require current quote activity above prior24bar mean.

Expected learning: Test activity-quality conditioning independently of the rejected efficiency filter.

Observed: 12,409 trades; 10/21 pass; 10/21 positive. Ranking [10, 0.023174872124907594, -0.00462400270933781]. Run `7ad3802f0fa3791f2dae`; audit passed.

Passing: BCO_USD, BTC_USD, HK33_HKD, JP225_USD, NAS100_USD, USD_CHF, USD_JPY, WTICO_USD, XAG_USD, XAU_USD.

Post-result lesson and next decision after round 10: Above-mean activity increases breadth9to10, sharply improves median-all to-0.46%/year and replaces several index winners with Asian indices/CHF/metals. Frequency remains sufficient everywhere. Test a looser activity threshold to see whether participation quality or simple turnover reduction explains this change.

## Round 11

Hypothesis: Moderately active structural confirmations may retain useful opportunities excluded by above-mean activity.

Change: Loosen confirmation activity threshold1.0→0.75.

Expected learning: Check the local activity neighborhood instead of treating one threshold as established.

Observed: 15,324 trades; 6/21 pass; 6/21 positive. Ranking [6, 0.044752730980897146, -0.009932294067470579]. Run `3e2b5fb46cd61f51ecd0`; audit passed.

Passing: BCO_USD, BTC_USD, NAS100_USD, USD_JPY, WTICO_USD, XAU_USD.

Post-result lesson and next decision after round 11: Loosening activity loses four passes despite higher median score among its six survivors. That weakens the case for a broad activity plateau. Test1.25as the stricter neighbor while preserving confirmation and exits, then leave threshold work for distinct structural questions.

## Round 12

Hypothesis: Stronger participation may improve structural-break follow-through but risks missing monthly openings.

Change: Tighten confirmation activity threshold1.0→1.25.

Expected learning: Assess the other local activity neighbor and quantify frequency sensitivity.

Observed: 9,140 trades; 8/21 pass; 12/21 positive. Ranking [8, 0.020095321134223354, 0.0037989426763771093]. Run `dd76e88a5c134580af87`; audit passed.

Passing: BCO_USD, HK33_HKD, JP225_USD, NAS100_USD, SPX500_USD, USD_JPY, WTICO_USD, XAU_USD.

Post-result lesson and next decision after round 12: Activity1.25improves median-all to+0.38%/year and12scorespositive, but four positive instruments miss full months, leaving eight passes. Activity1.0is current breadth winner; the local1.25neighbor exposes a score/frequency tradeoff. Test structural invalidation location next rather than refining the activity number further.

## Round 13

Hypothesis: A confirmed structural break may survive a midpoint retest before continuing within18bars.

Change: Loosen structural failure exit from midpoint to opposite outer-quarter boundary.

Expected learning: Distinguish midpoint exit noise from complete range failure.

Observed: 12,335 trades; 10/21 pass; 10/21 positive. Ranking [10, 0.01641869199482187, -0.006948940256699953]. Run `4f8a99dda66a3747cddd`; audit passed.

Passing: BCO_USD, BTC_USD, HK33_HKD, JP225_USD, NAS100_USD, USD_CHF, USD_JPY, WTICO_USD, XAG_USD, XAU_USD.

Post-result lesson and next decision after round 13: Allowing deeper retests preserves ten passes but lowers median passing and median-all scores. The midpoint still balances failure timing better than a permissive opposite-quarter boundary. Test a tighter exit that abandons loss of outer-quarter acceptance.

## Round 14

Hypothesis: A successful structural continuation may need to stay in the directional outer quarter rather than merely above midpoint.

Change: Tighten failure exit to loss of directional outer-quarter acceptance.

Expected learning: Compare both sides of structural invalidation without changing entries.

Observed: 13,193 trades; 7/21 pass; 7/21 positive. Ranking [7, 0.012230217653614489, -0.013159460722348597]. Run `7f8f6ec73131c96a8066`; audit passed.

Passing: BTC_USD, DE30_EUR, HK33_HKD, NAS100_USD, USD_JPY, WTICO_USD, XAU_USD.

Post-result lesson and next decision after round 14: Tighter acceptance-failure exits cut breadth10to7 and harm metal/energy results. Midpoint invalidation remains best among three tested levels, supporting a nontrivial retest allowance. Before further filters, attribute the current winner to long versus short structure breaks.

## Round 15

Hypothesis: Long structural acceptance may contribute most of the symmetric strategy returns.

Change: Retain only long structural-break entries as a directional control.

Expected learning: Measure directional attribution and monthly coverage; a control is not evidence of an independent mechanism.

Observed: 6,520 trades; 3/21 pass; 11/21 positive. Ranking [3, 0.009431586327066165, 0.0037725872480449006]. Run `2c6099c9b0a12a017dfb`; audit passed.

Passing: ETH_USD, NAS100_USD, USD_JPY.

Post-result lesson and next decision after round 15: Long-only improves median-all to+0.38%/year and11scorespositive, but eight positives miss full months, leaving three passes. Symmetric trading materially supports the monthly rule. Test short-only attribution before restoring both sides.

## Round 16

Hypothesis: Short structural acceptance may contribute distinct returns and monthly opportunities.

Change: Retain only short structural-break entries as the complementary control.

Expected learning: Separate short profitability from its role filling otherwise empty months.

Observed: 5,889 trades; 1/21 pass; 5/21 positive. Ranking [1, 0.013700863592547146, -0.013722793389124334]. Run `397e561146d0284ccd82`; audit passed.

Passing: HK33_HKD.
