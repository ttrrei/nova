# Volume activity phase 1 learning

Twenty sequential adaptive hourly YAML tests on all21 instruments. Volume is source quote activity, not market-wide traded volume. Execution costs and mandatory2%stop remain fixed. Each round receives a full independent ledger audit.

## Round 1

Hypothesis: A closing prior-range breakout with above-average quote activity may continue.

Change: Reproduce original 1.5 activity-ratio breakout baseline.

Expected learning: Separate profitability failures from monthly-frequency failures before refining activity threshold.

Observed: 6/21 pass, 9/21 positive, 12,859 trades. Rank [6, 0.03430605961232276, -0.03031909719497407]. Run `bc0e2b590600184b9afd`; audit passed.

Post-result lesson for round 1: Baseline reproduces6passes and9positive scores. BTC,JP225 andUSDCHF are positive but miss months; most FX/index losses are score failures. First loosen activity to restore frequency while retaining breakout participation.

## Round 2

Hypothesis: A closing breakout with activity above its prior mean may retain useful participation while restoring monthly openings.

Change: Lower relative activity requirement1.5→1.0 only.

Expected learning: Measure whether activity selectivity rather than breakout direction causes missed months.

Observed: 6/21 pass, 6/21 positive, 18,776 trades. Rank [6, 0.028806673333290136, -0.03724826097220386]. Run `78ba17cb1240130b3c7b`; audit passed.

Post-result lesson for round 2: Activity1.0 restores monthly BTC/ETH coverage but their scores become negative; passcount stays6 and both medians weaken. Merely adding opportunities is not enough. Check stronger participation as the opposite control before altering exits.

## Round 3

Hypothesis: A stronger activity burst may select better closing breakouts despite fewer openings.

Change: Raise baseline relative activity1.5→2.0 only.

Expected learning: Test whether higher event quality offsets lost monthly eligibility, versus the lower-activity control.

Observed: 4/21 pass, 8/21 positive, 8,268 trades. Rank [4, 0.0234909582333687, -0.01234170986791943]. Run `128c2e2a91f53918b150`; audit passed.

Post-result lesson for round 3: Activity2.0 improves the all-instrument median loss but cuts passes6to4 because four positive assets miss months, notably BTC32 andETH31. Keep1.5 as the main branch and test whether its fixed3%target clips activity-led continuation.

## Round 4

Hypothesis: Activity-backed breakouts may benefit from uncapped continuation rather than a fixed3%profit target.

Change: Remove3%take-profit cap from baseline; keep midpoint exit and24bar holding.

Expected learning: Distinguish entry-quality problems from target truncation while retaining the mandatory2%stop.

Observed: 7/21 pass, 11/21 positive, 12,517 trades. Rank [7, 0.01880782822859878, 0.0048371099229552825]. Run `07c2538af230add1d652`; audit passed.

Post-result lesson for round 4: Removing target addsXAG and makesBTC/ETH strongly positive, raising breadth6to7 and all21median abovezero, but four positive assets still miss months. Retest activity1.0 on the uncapped branch: its prior frequency gain may now combine with untruncated winners.

## Round 5

Hypothesis: Broader above-average quote participation may restore monthly opportunities when activity-led winners are uncapped.

Change: Lower activity1.5→1.0 on the uncapped24bar branch.

Expected learning: Test the interaction between restored opportunity frequency and removal of winner truncation.

Observed: 8/21 pass, 8/21 positive, 18,027 trades. Rank [8, 0.04592680536938381, -0.02469304323779964]. Run `54dc9d3cea7058ab6710`; audit passed.

Post-result lesson for round 5: Lower activity on the uncapped branch restoresBTC monthly coverage and increases passes7to8, with higher passing median; ETH becomes negative again. Since tail capture helped, test whether extending the maximum holding horizon improves continuation before adding filters.

## Round 6

Hypothesis: Activity-backed closing breakouts may need up to48 observed bars to realize continuation.

Change: Extend uncapped branch maximum holding24→48bars only.

Expected learning: Determine whether the remaining24bar time exit truncates winners after removing the price target.

Observed: 9/21 pass, 9/21 positive, 16,521 trades. Rank [9, 0.05558486844875844, -0.03314318117181712]. Run `6d3d65b457305acfc085`; audit passed.

Post-result lesson for round 6: Extending the holding cap to48 addsETH and raises breadth8to9, but the all21median worsens. The added tail opportunity is selective. Test the opposite12bar horizon to determine whether the gain is due simply to longer exposure.

## Round 7

Hypothesis: Shorter12bar containment may avoid failed activity-led breakouts that reverse before midpoint exits.

Change: Shorten uncapped24bar branch maximum holding24→12bars as a horizon control.

Expected learning: Compare the shorter and longer duration branches before choosing a context refinement.

Observed: 6/21 pass, 6/21 positive, 21,456 trades. Rank [6, 0.03753083108365172, -0.03278135238293994]. Run `821f7407a3b9c079fc8b`; audit passed.
