# Volatility expansion phase 1 learning log

Baseline round1:7/21 pass,15,020 actual trades, no additional positive-score instruments lost to monthly frequency. The initial decision was to isolate shock selectivity before combining filters. Each later entry contains its pre-run expected learning, observed result and subsequent interpretation.

Interpretation and next decision: Round1 establishes7 passing instruments, with nonpositive scores binding14. Most monthly coverage is sufficient. Raise the expansion threshold to2ATR to test whether shock selectivity improves failing instruments before relaxing anything.

## Round 2: Expansion threshold1.5→2.0ATR; other rules unchanged.

Hypothesis: Larger two-ATR breakout bars may separate sustained expansions from weaker range releases.

Expected learning: Does greater shock selectivity improve scores enough to offset reduced monthly opportunities?

Observed: 4/21 pass; 3 additional positive-score instruments fail monthly frequency; 14/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Ranking [4, 0.050688121918966975, -0.016824624237218328]; 9229 actual trades.

Interpretation and next decision: Round2 raises threshold to2 and reduces passes7→4 despite seven positive instruments: BCO/JP225/USDCHF lose monthly eligibility. All-instrument median improves to-1.68%/year, suggesting selectivity trades breadth for lower drag. Test the opposite, lowering to1ATR, to distinguish frequency gains from extra losing noise.

## Round 3: Expansion threshold1.5→1.0ATR frombaseline.

Hypothesis: A one-ATR closing breakout may capture more ordinary volatility expansion with better monthly reach.

Expected learning: Check whether broader opportunities add positive instruments or only increase trade cost/noise.

Observed: 7/21 pass; 0 additional positive-score instruments fail monthly frequency; 14/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Ranking [7, 0.019305350027447488, -0.04197196667633407]; 20069 actual trades.

Interpretation and next decision: Round3 keeps7 passes but median passing score falls3.72%→1.93% and all21median worsens. More frequent ordinary breakouts did not broaden the positive set enough. Keep1.5ATR and test one-bar continuation confirmation to reduce immediate breakout failure.

## Round 4: Delay entry one confirmation bar after baseline expansion; outer-quarter hold.

Hypothesis: One close holding the outer range quarter after a1.5ATR breakout may exclude immediate expansion failures.

Expected learning: Compare stronger confirmation against lost timing and monthly activity.

Observed: 4/21 pass; 1 additional positive-score instruments fail monthly frequency; 16/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Ranking [4, 0.045354870731169894, -0.03212998714337762]; 13600 actual trades.

Interpretation and next decision: Round4 delaysconfirmation and reduces breadth to4passes. USDCHF positive still missesmonths; NAS/BCO/BTC turnnonpositive, suggesting delayed expansion chases poorer fills rather than repairing failures. Return to immediate baseline and isolate midpoint-exit effect with an exit ablation.

## Round 5: Remove midpoint indicator exits; retain2%stop,4%target and24bar maximum.

Hypothesis: A volatility breakout may need room beyond a rolling midpoint rather than being liquidated by that moving reference.

Expected learning: Does the midpoint exit cut winners or protect against falsebreakouts?

Observed: 4/21 pass; 1 additional positive-score instruments fail monthly frequency; 16/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Ranking [4, 0.0475103022518863, -0.02275653392484377]; 13462 actual trades.

Interpretation and next decision: Round5 exit ablation also drops to4passes, so retaining an explicit failure exit matters for breadth. Test a tighter outer-quarter failure boundary to stop expansion fade sooner, while leavingthe mandatory hardstop unchanged.

## Round 6: Tighten rolling-range indicator exit frommidpoint toouter-quarter.

Hypothesis: A true expansion should hold the outer quarter; loss of that position may identify failure before midpoint loss.

Expected learning: Test whether faster failure exits improve failing score instruments without a frequency penalty.

Observed: 6/21 pass; 0 additional positive-score instruments fail monthly frequency; 15/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Ranking [6, 0.013152030670151936, -0.02459114232030425]; 17175 actual trades.

Interpretation and next decision: Round6 tighter failure exits reaches6passes, trading different index breadth but lower passing median1.32%. Neither exit ablation nor tighter exit improves baseline7; keepbaseline exits and test whether prior-path directional efficiency distinguishes continuation-worthy expansions.

## Round 7: Add efficiency_24>.25 filter tobaseline entries.

Hypothesis: Expansion beyond a24bar range is more likely to continue when the24bar path already has directional efficiency above.25.

Expected learning: Separate persistent expansion from noisy spikes while tracking monthly losses from filtering.

Observed: 3/21 pass; 3 additional positive-score instruments fail monthly frequency; 15/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Ranking [3, 0.039648307259645084, -0.02186649381744539]; 10487 actual trades.

Interpretation and next decision: Round7 efficiency>.25 gives6positive but only3passes; conditioning loses monthlycoverage inWTICO/UK/USDCHF and is not supported as general repair. Test above-average quoteactivity instead, a distinct participation hypothesis, with a lenient1.0 ratio to avoid the same severe sparsity.

## Round 8: Add relative_volume_24>1.0 tobaseline entries.

Hypothesis: An expansion breakout supported by above-average quoteactivity may be less likely to be a low-participation spike.

Expected learning: Does activity support improve positive breadth without severe missing-month eligibility losses?

Observed: 7/21 pass; 1 additional positive-score instruments fail monthly frequency; 13/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Ranking [7, 0.03935943417649893, -0.023881286260133843]; 13991 actual trades.

Interpretation and next decision: Round8 is the first improvement over baseline:7passes retained, passing median3.94% versus3.72%, and all21median improves to-2.39%. JP225 becomespositive but remains sparse. Probe a nearby1.25activity threshold to assess whether participation benefit persists or is a narrow historical setting.

## Round 9: Raise activity filter from1.0to1.25; retain1.5ATR expansion.

Hypothesis: Moderately stronger quoteactivity support may improve the quality of already large expansion breakouts.

Expected learning: Check local stability of the participation improvement and record monthly eligibility costs.

Observed: 5/21 pass; 3 additional positive-score instruments fail monthly frequency; 13/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Ranking [5, 0.024787106347506638, -0.02350765363566682]; 12427 actual trades.

Interpretation and next decision: Round9 loses two passes at1.25activity, including BTC due to a missing month, while otherpositive names shift. Activity benefit is frequency-sensitive; retain the1.0branch and test whether expansion continuation is shorter than the current24bar cap.

## Round 10: Shorten maximum holding24→12bars on activity-supported branch.

Hypothesis: A volatility expansion may deliver most continuation during the first12observed hours rather than a full24bar hold.

Expected learning: Does a shorter continuation horizon improve score breadth and reduce prolonged failed expansion exposure?

Observed: 8/21 pass; 0 additional positive-score instruments fail monthly frequency; 13/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Ranking [8, 0.026017735555112817, -0.015048332958058432]; 15838 actual trades.

Interpretation and next decision: Round10 improves breadth7→8 with12bar cap, addsDE30, and improvesall21median to-1.50%; no positive instrument loses monthly eligibility. Shorter horizon appears more useful than tighter entry filters. Test6bars to locate whether continuation benefit is concentrated veryearly or needs the12bar span.

## Round 11: Shorten holding12→6bars on activity-supported expansion.

Hypothesis: The expansion continuation payoff may be concentrated in the first six observed bars.

Expected learning: Distinguish early impulse capture from over-fast exit and trading-cost drag.

Observed: 4/21 pass; 0 additional positive-score instruments fail monthly frequency; 17/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Ranking [4, 0.023760932976567173, -0.035715423866181]; 16953 actual trades.

Interpretation and next decision: Round11 six-bar cap collapses8→4passes and worsens median, so impulses need more than six bars and extra turnover is costly. Test18bars between the successful12 and broader24control to check whether12is a narrow setting or part of a useful holding region.

## Round 12: Increase holding12→18bars as local horizon sensitivity.

Hypothesis: Supported expansion continuation may persist across a12-to18bar horizon rather than depend on an exact12bar cutoff.

Expected learning: Check neighborhood stability of round10 improvement.

Observed: 8/21 pass; 1 additional positive-score instruments fail monthly frequency; 12/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Ranking [8, 0.04687025349604984, -0.011198107138698744]; 14775 actual trades.

Interpretation and next decision: Round12 retains8passes and raises passing median4.69%, withall21median-1.12%, improving selectedrank over12bars. JP225positivebutmissesmonthly. Before combining further filters, isolate directional contribution: long-only is a control for whether the apparent expansion edge is dominated by upward drift.

## Round 13: Long-only arm ablation on18bar activity-supported expansion.

Hypothesis: Upward volatility expansions may have different continuation behavior from downside expansions across this instrument set.

Expected learning: Diagnose direction asymmetry; any gain may reflect long drift and must retain same rule acrossall21.

Observed: 3/21 pass; 6 additional positive-score instruments fail monthly frequency; 12/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Ranking [3, 0.052915078943241184, -0.007848640647254096]; 7344 actual trades.

Interpretation and next decision: Round13 long-only has9positive scores but only3monthlypasses, so simply taking upward drift loses the regularity objective. A short-only counterpart will determine whether downward expansions offer genuine alternative coverage or mainly add monthly openings to a mixed strategy.

## Round 14: Short-only arm ablation on18bar activity-supported expansion.

Hypothesis: Downside volatility expansions may contribute differently to score and regularity than upside expansions.

Expected learning: Complete direction diagnostic without interpreting single-sided historical gains as an independent edge.

Observed: 1/21 pass; 3 additional positive-score instruments fail monthly frequency; 17/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Ranking [1, 0.005729277887283966, -0.01770575889902633]; 7637 actual trades.

Interpretation and next decision: Round14 short-only has4positive and only1monthlypass. Neither arm alone maintains breadth; the two-sided rule combines actual opportunity timing as well as returns. Keepboth and test whether the4%target usefully harvests expansion or caps rare large continuations.

## Round 15: Remove4%takeprofit; retain midpoint,18bar cap and mandatory2%stop.

Hypothesis: The best continuation expansions may benefit from an uncapped target while the midpoint and18bar exits still bound holding.

Expected learning: Test target truncation independently of entry selectivity and maximumhorizon.

Observed: 11/21 pass; 1 additional positive-score instruments fail monthly frequency; 9/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Ranking [11, 0.02491304994926459, 0.004766633874635843]; 14611 actual trades.

Interpretation and next decision: Round15 uncapped takeprofit improves8→11passes and makesall21medianpositive0.48%/year. ETH/UK/DE30 broaden profitability; JP225ispositivebutmissesmonthly. This suggests truncating rare expansion winners was harmful. Test a tighter2%target as a predeclared countercheck of that mechanism before refining uncappedholds.

## Round 16: Tighten profit target4%→2% on the18bar activity-supported branch.

Hypothesis: If rare long continuations drive expansion returns, a tighter2%profit cap should worsen breadth rather than improve it.

Expected learning: Countercheck target-truncation explanation; do not select merely from one favorable uncapped result.

Observed: 7/21 pass; 0 additional positive-score instruments fail monthly frequency; 14/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Ranking [7, 0.030323013277962045, -0.015773046634894074]; 15192 actual trades.

Interpretation and next decision: Round16 tight2%cap falls to7passes versus11uncapped, supporting the truncation hypothesis descriptively. Next test whether uncapped gains require the specific18bar horizon or survive the prior24bar horizon, separating the target change from hold tuning.

## Round 17: Increase uncapped maximumholding18→24bars.

Hypothesis: Uncapped expansion continuations may remain useful at a24bar maximum rather than depend on exactly18bars.

Expected learning: Check horizon stability around the newly useful uncapped branch.

Observed: 8/21 pass; 0 additional positive-score instruments fail monthly frequency; 13/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Ranking [8, 0.07301861022799225, -0.011845808735517027]; 13742 actual trades.

Interpretation and next decision: Round17 extendsuncappedhold24bars and drops11→8passes despitehighermedianamongpasses7.30%. Extra exposure improves strongsurvivors but loses broadmarginalinstrument profitability. Test12bars to distinguish a useful intermediatehorizon from a monotonic preference for shorter exposure.

## Round 18: Shorten uncapped holding18→12bars.

Hypothesis: An uncapped12bar expansion hold may preserve strong moves while reducing marginal losing exposure.

Expected learning: Comparebothneighbors12and24against18without changing entries or stop.

Observed: 7/21 pass; 0 additional positive-score instruments fail monthly frequency; 14/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Ranking [7, 0.09838051951952573, -0.01693217489950669]; 15741 actual trades.

Interpretation and next decision: Round18 uncapped12bars has7passes; the18bar winner is not broad across12/24horizonneighbors. Treat11passes as selected and horizon-sensitive, not stable evidence. Use the remaining entry ablations to see whether lower shock threshold or removal of activity support explains the breadth rather than an exact horizon fit.

## Round 19: Lower expansion threshold1.5→1.25ATR on uncapped18bar activity-supported winner.

Hypothesis: A moderately smaller1.25ATR expansion may broaden the uncapped18bar continuation rule without admitting ordinary nonexpansion bars.

Expected learning: Check threshold sensitivity of the winner after observed horizon fragility.

Observed: 7/21 pass; 1 additional positive-score instruments fail monthly frequency; 13/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Ranking [7, 0.04323208334603364, -0.011423846282436504]; 17011 actual trades.

Interpretation and next decision: Round19 lowering expansion to1.25ATR returns only7passes, so selected1.5ATR/18bar breadth is not robust to this thresholdneighbor. Finalround removes activity from the exact winner, isolating whether participation support contributes beyond the uncapped18bar exit combination.

## Round 20: Remove activity>1.0filter from uncapped18bar winner.

Hypothesis: The uncapped18bar expansion rule may work without its above-average activity filter, making the simpler price rule preferable if breadth remains.

Expected learning: Attribute the combined improvement to activity support versus exit/horizon changes and record simpler control.

Observed: 9/21 pass; 0 additional positive-score instruments fail monthly frequency; 12/21 have nonpositive scores; 0 instruments have no trades. Yearly concentration is descriptive, not another acceptance gate. Ranking [9, 0.020278586551152934, -0.00988753872637669]; 15689 actual trades.

Interpretation and next decision: Round20 removing activity gives9passes versus11withactivity, so participation adds descriptivebreadth. All20rounds are complete and independently audited. Round15 remains best, but nearbyhorizons and lower shock threshold lose breadth. Stopbeforephase2; coordinator guidance must determine the next tests.
