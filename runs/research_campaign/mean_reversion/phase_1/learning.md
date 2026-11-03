
## Round 01

Hypothesis: A two-ATR displacement from SMA24 reverts toward its moving mean.

Change: Reproduce the original mean-reversion baseline.

Result: 0/21 pass, 0/21 positive, 34,182 trades; rank [0, 0.0, -0.0878477364926685]; run `fde2b6cf7de7e661b577`.

Post-result lesson: All21 instruments trade every full month but all lose. Profitability, rather than monthly frequency, is the binding failure. Test recovery before fading instead of entering directly into a large displacement.

## Round 02

Hypothesis: Recovery into the outer mean-deviation band after a recent two-ATR stretch may avoid ongoing directional shocks.

Change: Require a recent two-ATR extreme followed by recovery inside1.5ATR before fading, still before the mean.

Result: 1/21 pass, 1/21 positive, 25,814 trades; rank [1, 0.006508623933006305, -0.04429513629857666]; run `f712ae7a0898f83a88bd`.

Post-result lesson: Recovery improves the all-instrument median from-8.78% to-4.43%/year and creates one passing SPX example. Most assets still lose; test whether fades need a low-efficiency context rather than stronger extremes.

## Round 03

Hypothesis: Recovery fades are more plausible when the recent24bar path has low directional efficiency.

Change: Add efficiency24below0.25 to the recovery entry.

Result: 3/21 pass, 3/21 positive, 18,077 trades; rank [3, 0.01527403230718318, -0.035917581036043186]; run `454a25c02fd4a0035ea2`.

Post-result lesson: Low efficiency expands passing breadth1to3 and improves median score, with almost no monthly gaps. The effect is selective to equity indices and still deeply negative in crypto/metals. Test shorter exits to limit failed recovery attempts.

## Round 04

Hypothesis: A six-bar horizon may cut failed fades sooner while retaining quick recoveries toward the mean.

Change: Shorten maximum holding12to6bars only.

Result: 2/21 pass, 2/21 positive, 19,237 trades; rank [2, 0.019315314491680717, -0.03599863599127105]; run `8ea01ab589c2a6929c13`.

Post-result lesson: The six-bar cap loses the UK100 pass and worsens several instruments; short holding is not a general cure. Restore12bar branch and test whether more time is needed to finish a valid reversion.

## Round 05

Hypothesis: A24bar cap may let a confirmed low-efficiency recovery finish reverting before a forced exit.

Change: Extend holding12to24bars versus round3.

Result: 3/21 pass, 3/21 positive, 17,143 trades; rank [3, 0.022972698173416163, -0.036924293440895546]; run `02f59abe61e574336eba`.

Post-result lesson: A24bar cap wins the existing three-pass tie by median passing score, though the median across21barely worsens. Test deeper initial stretch to see whether the current threshold mostly captures ordinary trend drift.

## Round 06

Hypothesis: An initial three-ATR stretch followed by recovery may isolate more genuine dislocations than two-ATR drift.

Change: Raise prior stretch magnitude2to3ATR, retain recovery1.5/efficiency/24barcap.

Result: 0/21 pass, 8/21 positive, 4,455 trades; rank [0, 0.0, -0.004091274286569498]; run `e3823b352c37766c088a`.

Post-result lesson: Three-ATR dislocations create8positive instruments and sharply reduce losses, but all8fail monthly activity. This identifies a promising but sparse branch; extend recognition memory rather than immediately abandon the stretch mechanism.

## Round 07

Hypothesis: A longer18bar memory of a three-ATR stretch may retain more subsequent recovery opportunities.

Change: Extend prior-extreme within6to18bars only.

Result: 4/21 pass, 5/21 positive, 12,692 trades; rank [4, 0.01688452368221622, -0.020572453185758902]; run `559ebaec81095b48dfbd`.

Post-result lesson: Longer memory recovers four monthly passes and adds NAS100, while CN50stillmissesone month. Costs remain negative across mostFX/crypto. Test an intermediate2.5ATR stretch to trade the depth/frequency compromise directly.

## Round 08

Hypothesis: An intermediate2.5ATR stretch with long recovery memory may balance dislocation quality and monthly availability.

Change: Reduce initial stretch3to2.5ATR on the18bar-memory branch.

Result: 4/21 pass, 4/21 positive, 20,397 trades; rank [4, 0.02585769113649232, -0.02830712062624381]; run `85a9d4f8063560018a3b`.

Post-result lesson: The intermediate stretch swaps NAS100 for CN50 and improves the selected passing median, but medianall worsens and crypto losses deepen. The four-pass branch is not universal profitability. Test whether local reversion should occur in agreement with the slowerEMA60 direction.

## Round 09

Hypothesis: Reverting a local SMA24 displacement in the direction of broaderEMA60location may avoid fading structural trends.

Change: Add same-sideEMA60price-location gate to the local recovery fade.

Result: 0/21 pass, 6/21 positive, 2,785 trades; rank [0, 0.0, -0.005813110504781762]; run `9a87164e30a8cf2b7ee4`.

Post-result lesson: The slow-trend gate nearly eliminates activity: sixpositive assets but none meet monthly opening coverage. It is too restrictive for this dislocation definition. Return to the four-pass branch and isolate whether the1%profit cap harms successful reversions.

## Round 10

Hypothesis: Allowing a recovery fade to exit at the mean without a fixed profitcap may retain valuable reversions.

Change: Remove1%takeprofit only, retain mean exit and24bar cap.

Result: 4/21 pass, 4/21 positive, 20,043 trades; rank [4, 0.025515479739679478, -0.014653154556515561]; run `6c8084f0c6026bce02f4`.

Post-result lesson: Removing the target leaves four passes and a slightly lower passing median, but improves the all21median from-2.83%to-1.47%/year and greatly helps energy/crypto. Distance recovery can be caused by a moving mean without a true price turn; test directional return confirmation on this branch.

## Round 11

Hypothesis: A positive six-bar price change after downside stretch, or negative after upside stretch, may confirm actual recovery rather than a moving-mean artifact.

Change: Add signed six-bar price-change confirmation to the uncapped recovery branch.

Result: 6/21 pass, 6/21 positive, 13,980 trades; rank [6, 0.0038867939765858638, -0.013568778229063945]; run `e7298657c3fb2fe94c68`.

Post-result lesson: Actual price-turn confirmation expands breadth4to6 but creates several marginal passes: CN50score0.02%/year and threeothersbelow0.5%. Test whether immediate mean-touch exits truncate the stronger reversal branch.

## Round 12

Hypothesis: A confirmed price reversal may overshoot the moving mean by half anATR before decaying.

Change: Move the indicator exit from mean-touch to half-ATR mean overshoot; retain24barcap/no target.

Result: 6/21 pass, 6/21 positive, 12,476 trades; rank [6, 0.008547687455697447, -0.014303180495413362]; run `ddf42e5233827717f376`.

Post-result lesson: Half-ATR mean overshoot keeps six passes and raises their median0.39%to0.85%/year, but swapsCN50forNAS100and does not improve the median across21. To understand index-driven breadth, isolate long and short contributions before adding more filters.

## Round 13

Hypothesis: Long recovery fades may account for most positive index results under a broad rising-price history.

Change: Long-only attribution control of round12, same exits/costs/instruments.

Result: 2/21 pass, 9/21 positive, 6,054 trades; rank [2, 0.011776020223809578, -0.0032733359109189774]; run `e5b5ab963df9ea671f97`.

Post-result lesson: Long-only has ninepositive assets but justtwo monthly passes; missing months remove mostindex opportunities. Directional drift matters, but two-sided participation currently supplies needed monthly openings. Test the complementary short side to see whether it is merely a frequency subsidy.

## Round 14

Hypothesis: Short recovery fades may contribute distinct reversion returns rather than merely filling quiet months.

Change: Short-only attribution control of round12.

Result: 0/21 pass, 7/21 positive, 6,429 trades; rank [0, 0.0, -0.010804506262685462]; run `c58febe0d2ac4bb0fd1e`.

Post-result lesson: Short-only has sevenpositive instruments butnonepass monthly; UK/SPX/WTICOcontributions are positive, so shorts are not universally a subsidy. Keep two sides for the main hypothesis. The signed-return confirmation may make the low-efficiency gate redundant; ablate it.

## Round 15

Hypothesis: Actual recovery-direction confirmation may be sufficient without requiring low24bar efficiency.

Change: Remove the low-efficiency gate from the signed-recovery/mean-overshoot branch.

Result: 4/21 pass, 4/21 positive, 17,384 trades; rank [4, 0.03246428362040364, -0.026877989340628107]; run `b5be90aaf134fa3b959a`.

Post-result lesson: Removing efficiency worsens breadth6to4 and all21median; the low-efficiency regime contributes to this signed-recovery hypothesis. Test a stricter neighboring regime threshold to see whether the current gains are broad or confined to mixed directional paths.

## Round 16

Hypothesis: A stricter low-efficiency regime may isolate cleaner reversion conditions.

Change: Tighten efficiency ceiling0.25to0.15only.

Result: 1/21 pass, 8/21 positive, 6,769 trades; rank [1, 0.01339243777103169, -0.003184460167219196]; run `472bab47c44e10dc7c88`.

Post-result lesson: Stricter0.15efficiency creates eightpositive instruments butonlyone monthlypass; sparsity ratherthan edge becomes binding. Test the opposite0.35neighbor to check whether the sixpass0.25setting is a narrow local maximum.

## Round 17

Hypothesis: A moderately looser efficiency ceiling may preserve reversion quality while restoring edge cases in monthly coverage.

Change: Relax efficiency0.25to0.35as the opposite neighborcontrol.

Result: 6/21 pass, 6/21 positive, 15,761 trades; rank [6, 0.019068656798620652, -0.019096760375032374]; run `c22a00584a0e0f5f40a9`.

Post-result lesson: Looser0.35efficiency preserves sixpasses and improves passingmedian0.85%to1.91%/year, but swapsAUD/US30/WTICOforCN50/DE30/HK33 and worsens the medianall. Test a signal-bar shock ceiling to address energy/crypto losses without changing the assetpool.

## Round 18

Hypothesis: Avoiding signal bars wider than1.5ATR may reduce entries immediately after volatile recovery shocks.

Change: Add current-bar rangeATRbelow1.5to round17.

Result: 5/21 pass, 5/21 positive, 14,824 trades; rank [5, 0.019346961761264405, -0.021125256539308464]; run `3371f9df791247d2881e`.

Post-result lesson: Signal-bar shock filtering reduces breadth6to5 and does not improve the all21median; discard it for the main branch. Test stronger recovery toward the mean to distinguish early turning points from late but clearer reversion.

## Round 19

Hypothesis: Waiting until price recovers within half anATR of its mean may offer clearer reversion despite later fills.

Change: Tighten recovery threshold1.5to0.5ATR; keep prior stretch, signedreturn,0.35efficiencyandovershoot exit.

Result: 6/21 pass, 6/21 positive, 11,401 trades; rank [6, 0.014518309343609077, -0.018250594064256657]; run `66e96fe2e70dcaf4def4`.

Post-result lesson: Later recovery keeps sixpasses but lowers passingmedian1.91%to1.45%/year and swapsCN50forUS30. It reduces somecrypto/metallosses yet is not the selected winner. The final test extends the selected branch horizon to check whether mean overshoot needs longer completion time.

## Round 20

Hypothesis: A48bar horizon may allow confirmed reversions to finish a halfATR overshoot before forced liquidation.

Change: Extend round17holdingcap24to48bars only.

Result: 7/21 pass, 7/21 positive, 15,191 trades; rank [7, 0.02036177932872409, -0.014787262220685793]; run `c140e7d6fc1884f4c3f6`.

Post-result lesson: Extending to48bars increases breadth6to7, adds a marginalAUD pass, and raises medianpassing score to2.04%/year. The all21median remains-1.48%; crypto/energy/metals remain negative. Phase1has improved a zero-pass baseline but has not found a universally positive reversion rule. Nextstage should test the selected horizon/recovery neighborhood and challenge its marginal passes and year concentration rather than add many filters.
