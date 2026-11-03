# Mean reversion phase 1 review

Completed20distinct, independently audited rounds on all21instruments and full available hourly history. Across experiments, 295,094 trades were audited. All costs, the2%stop, feature parameters and execution semantics remained fixed.

## Selected historical candidate

Round20, run `c140e7d6fc1884f4c3f6`; YAML `/home/ubuntu/work/nova/runs/research_campaign/mean_reversion/strategies/phase_1_round_20.yaml`. It passes on7/21instruments versus0/21for the baseline. Median passing-instrument annualized trade-return score is2.04%; median score across all21is-1.48%. These are per-instrument trade-return scores, not account returns or a portfolio.

Passing instruments: AUD_USD, CN50_USD, DE30_EUR, HK33_HKD, NAS100_USD, SPX500_USD, UK100_GBP.

The selected rules require a2.5ATR SMA24stretch in the preceding18observed bars; recovery inside1.5ATR while still on the stretched side of the mean; a signed six-bar price turn; efficiency24below0.35. Exit is a halfATR overshoot of the moving mean, a48bar holding cap, or the mandatory2%stop. There is no fixed profit target.

## Round evidence

| Round | Main change | Pass | Positive | Median passing score | Post-result lesson |
|---:|---|---:|---:|---:|---|
|1|Reproduce the original mean-reversion baseline.|0|0|0.00%|All21 instruments trade every full month but all lose. Profitability, rather than monthly frequency, is the binding failure. Test recovery before fading instead of entering directly into a large displacement.|
|2|Require a recent two-ATR extreme followed by recovery inside1.5ATR before fading, still before the mean.|1|1|0.65%|Recovery improves the all-instrument median from-8.78% to-4.43%/year and creates one passing SPX example. Most assets still lose; test whether fades need a low-efficiency context rather than stronger extremes.|
|3|Add efficiency24below0.25 to the recovery entry.|3|3|1.53%|Low efficiency expands passing breadth1to3 and improves median score, with almost no monthly gaps. The effect is selective to equity indices and still deeply negative in crypto/metals. Test shorter exits to limit failed recovery attempts.|
|4|Shorten maximum holding12to6bars only.|2|2|1.93%|The six-bar cap loses the UK100 pass and worsens several instruments; short holding is not a general cure. Restore12bar branch and test whether more time is needed to finish a valid reversion.|
|5|Extend holding12to24bars versus round3.|3|3|2.30%|A24bar cap wins the existing three-pass tie by median passing score, though the median across21barely worsens. Test deeper initial stretch to see whether the current threshold mostly captures ordinary trend drift.|
|6|Raise prior stretch magnitude2to3ATR, retain recovery1.5/efficiency/24barcap.|0|8|0.00%|Three-ATR dislocations create8positive instruments and sharply reduce losses, but all8fail monthly activity. This identifies a promising but sparse branch; extend recognition memory rather than immediately abandon the stretch mechanism.|
|7|Extend prior-extreme within6to18bars only.|4|5|1.69%|Longer memory recovers four monthly passes and adds NAS100, while CN50stillmissesone month. Costs remain negative across mostFX/crypto. Test an intermediate2.5ATR stretch to trade the depth/frequency compromise directly.|
|8|Reduce initial stretch3to2.5ATR on the18bar-memory branch.|4|4|2.59%|The intermediate stretch swaps NAS100 for CN50 and improves the selected passing median, but medianall worsens and crypto losses deepen. The four-pass branch is not universal profitability. Test whether local reversion should occur in agreement with the slowerEMA60 direction.|
|9|Add same-sideEMA60price-location gate to the local recovery fade.|0|6|0.00%|The slow-trend gate nearly eliminates activity: sixpositive assets but none meet monthly opening coverage. It is too restrictive for this dislocation definition. Return to the four-pass branch and isolate whether the1%profit cap harms successful reversions.|
|10|Remove1%takeprofit only, retain mean exit and24bar cap.|4|4|2.55%|Removing the target leaves four passes and a slightly lower passing median, but improves the all21median from-2.83%to-1.47%/year and greatly helps energy/crypto. Distance recovery can be caused by a moving mean without a true price turn; test directional return confirmation on this branch.|
|11|Add signed six-bar price-change confirmation to the uncapped recovery branch.|6|6|0.39%|Actual price-turn confirmation expands breadth4to6 but creates several marginal passes: CN50score0.02%/year and threeothersbelow0.5%. Test whether immediate mean-touch exits truncate the stronger reversal branch.|
|12|Move the indicator exit from mean-touch to half-ATR mean overshoot; retain24barcap/no target.|6|6|0.85%|Half-ATR mean overshoot keeps six passes and raises their median0.39%to0.85%/year, but swapsCN50forNAS100and does not improve the median across21. To understand index-driven breadth, isolate long and short contributions before adding more filters.|
|13|Long-only attribution control of round12, same exits/costs/instruments.|2|9|1.18%|Long-only has ninepositive assets but justtwo monthly passes; missing months remove mostindex opportunities. Directional drift matters, but two-sided participation currently supplies needed monthly openings. Test the complementary short side to see whether it is merely a frequency subsidy.|
|14|Short-only attribution control of round12.|0|7|0.00%|Short-only has sevenpositive instruments butnonepass monthly; UK/SPX/WTICOcontributions are positive, so shorts are not universally a subsidy. Keep two sides for the main hypothesis. The signed-return confirmation may make the low-efficiency gate redundant; ablate it.|
|15|Remove the low-efficiency gate from the signed-recovery/mean-overshoot branch.|4|4|3.25%|Removing efficiency worsens breadth6to4 and all21median; the low-efficiency regime contributes to this signed-recovery hypothesis. Test a stricter neighboring regime threshold to see whether the current gains are broad or confined to mixed directional paths.|
|16|Tighten efficiency ceiling0.25to0.15only.|1|8|1.34%|Stricter0.15efficiency creates eightpositive instruments butonlyone monthlypass; sparsity ratherthan edge becomes binding. Test the opposite0.35neighbor to check whether the sixpass0.25setting is a narrow local maximum.|
|17|Relax efficiency0.25to0.35as the opposite neighborcontrol.|6|6|1.91%|Looser0.35efficiency preserves sixpasses and improves passingmedian0.85%to1.91%/year, but swapsAUD/US30/WTICOforCN50/DE30/HK33 and worsens the medianall. Test a signal-bar shock ceiling to address energy/crypto losses without changing the assetpool.|
|18|Add current-bar rangeATRbelow1.5to round17.|5|5|1.93%|Signal-bar shock filtering reduces breadth6to5 and does not improve the all21median; discard it for the main branch. Test stronger recovery toward the mean to distinguish early turning points from late but clearer reversion.|
|19|Tighten recovery threshold1.5to0.5ATR; keep prior stretch, signedreturn,0.35efficiencyandovershoot exit.|6|6|1.45%|Later recovery keeps sixpasses but lowers passingmedian1.91%to1.45%/year and swapsCN50forUS30. It reduces somecrypto/metallosses yet is not the selected winner. The final test extends the selected branch horizon to check whether mean overshoot needs longer completion time.|
|20|Extend round17holdingcap24to48bars only.|7|7|2.04%|Extending to48bars increases breadth6to7, adds a marginalAUD pass, and raises medianpassing score to2.04%/year. The all21median remains-1.48%; crypto/energy/metals remain negative. Phase1has improved a zero-pass baseline but has not found a universally positive reversion rule. Nextstage should test the selected horizon/recovery neighborhood and challenge its marginal passes and year concentration rather than add many filters.|

## Interpretation and fragility

The immediate-fade baseline is negative on every instrument despite complete monthly activity. Recovery confirmation and low-efficiency context reduce the failure, while deeper stretches alone generate positive but sparse observations. Extending the extreme-memory window helps opportunity coverage. Actual signed price recovery is useful because a moving SMA can create apparent distance recovery without a price reversal. Removing the fixed profit cap improves many losing assets; a modest mean overshoot and longer holding horizon improve selected breadth.

Six of the seven selected passing instruments are equity indices; AUD is a marginal exception. AUD's score is only0.05%/year and CN50's0.24%/year. Median score across all instruments remains negative, and BTC/ETH/energy/metals remain substantial losers. Full available calendar years and partial endpoint buckets remain visible;2026is partial.

Removing the best reported calendar-year contribution leaves nonpositive total trade-return sums for4/7passes: AUD_USD, CN50_USD, HK33_HKD, NAS100_USD. This is descriptive, not an additional acceptance gate.

| Passing instrument | Score | Losing reported years | Net sum excluding best year |
|---|---:|---|---:|
|AUD_USD|0.05%|2020, 2024, 2025, 2026|-8.25%|
|CN50_USD|0.24%|2020, 2021, 2024|-9.98%|
|DE30_EUR|4.88%|2023, 2026|14.76%|
|HK33_HKD|2.04%|2022, 2025, 2026|-5.66%|
|NAS100_USD|0.97%|2020, 2025, 2026|-6.97%|
|SPX500_USD|3.53%||19.49%|
|UK100_GBP|5.64%|2026|26.23%|

Long-only generated9positive instruments but only2monthly passes; short-only generated7positive instruments and no monthly passes. Positive short contributions exist, but monthly coverage depends on combining both sides. The0.15efficiency control had8positive instruments and only1monthly pass. The0.35neighbor retained6passes before the48barcap addedAUD; selected breadth therefore depends on context and a few marginal signs. No infrastructure failures occurred.

## Guidance proposed for phase 2

Challenge the selected48bar horizon with nearby durations and the recovery/mean-overshoot thresholds without using instrument-specific rules. Test whether delaying a true price turn, or making its minimum magnitude nonzero, improves weak passes without creating monthly gaps. Compare direction and context ablations on the selected branch rather than treating added filters as automatically useful. Keep the less restrictive round12as a branch because it passesAUD/US30/WTICOinstead of the newer CN50/DE30/HK33set. Inspect yearly concentration and higher-cost sensitivity as diagnostics; do not claim selected historical maxima are independent validation.

All round requests, candidate YAMLs, full compressed trade/signal artifacts, and post-run lessons are retained beneath this family directory. Stop after phase1; phase2requires coordinator guidance.
