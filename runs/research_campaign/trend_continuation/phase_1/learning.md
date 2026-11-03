# Trend continuation phase 1 research log

This stage uses one universal hourly YAML per round on all 21 instruments and the full available history. Every round retains the actual-entry 2% stop and observed quote execution with 0.2 bps adverse slippage per side. Each successful run receives an independent ledger audit. Selection is descriptive: passing-instrument count, then median passing score, then median score across instruments; no returns are combined into a portfolio.

The starting hypothesis is a PSAR flip, confirmed for three following observed bars, with Supertrend agreement. Baseline evidence has 8/21 passing instruments. The initial questions are whether confirmation delay, exit responsiveness, and established-trend filters explain its losing instruments. Subsequent mutations will follow observed per-instrument monthly and return diagnoses, and near-neighbor/negative-control tests will be retained.

No candidate will run until the coordinator freezes the engine in READY.json.

## Round 01: A three-bar confirmed PSAR flip with Supertrend agreement can capture continued directional moves.

Change: Re-establish the reviewed original rules under the frozen compressed campaign engine.

Observed: 25,604 trades; 8/21 positive; 8/21 pass. Ranking key: [8, 0.026287682494103407, -0.04209056335085772]. Run `312ef0ac9d14eab91f5c`; audit passed.

Passing instruments: DE30_EUR, HK33_HKD, JP225_USD, NAS100_USD, SPX500_USD, US30_USD, USD_JPY, XAU_USD.

Post-result lesson: The frozen engine reproduces the original eight passing instruments exactly. Every instrument has openings in every complete month; negative trade returns, especially crypto and most FX, are the binding problem. Test quicker confirmation before adding filters.

## Round 02: Confirming a PSAR flip after one bar rather than three may reduce delayed entry while Supertrend agrees.

Change: Reduce PSAR post-flip confirmation from three bars to one only.

Observed: 21,348 trades; 3/21 positive; 3/21 pass. Ranking key: [3, 0.03310000423363452, -0.043692648024357794]. Run `084d90d1eaab926a2d56`; audit passed.

Passing instruments: DE30_EUR, NAS100_USD, XAU_USD.

Post-result lesson: One-bar confirmation cuts passing breadth from8 to3 and reduces trades because Supertrend agreement is often not yet established at the earlier confirmation. Earlier is not better; restore baseline and test longer persistence.

## Round 03: Five-bar PSAR persistence with Supertrend agreement may reject more failed flips than three-bar confirmation.

Change: Increase post-flip confirmation from three bars to five only.

Observed: 25,686 trades; 5/21 positive; 4/21 pass. Ranking key: [4, 0.02135038932068281, -0.053548809463764904]. Run `77f0009d0b6501929166`; audit passed.

Passing instruments: DE30_EUR, NAS100_USD, US30_USD, USD_JPY.

Post-result lesson: Five-bar persistence also weakens breadth4passes; JP225 adds a monthly gap and XAU loses positivity. Three-bar timing remains best locally. Shift attention from entry delay to whether PSAR exits are too reactive.

## Round 04: Holding confirmed PSAR entries until Supertrend reverses may preserve broader trend moves that PSAR exits truncate.

Change: Replace PSAR-flip indicator exits with opposite Supertrend state; keep entry,60-bar cap and4%target.

Observed: 15,211 trades; 7/21 positive; 7/21 pass. Ranking key: [7, 0.02488360996226437, -0.027229703244306413]. Run `fee9f840669b2c161410`; audit passed.

Passing instruments: DE30_EUR, HK33_HKD, NAS100_USD, SPX500_USD, US30_USD, USD_JPY, XAU_USD.

Post-result lesson: Slower Supertrend exits reduce trades40% and improve median all-instrument score from-4.21% to-2.72%/year, but breadth drops8to7 and commodity/crypto losses deepen. Keep this as a branch, not the winner; test an intermediate EMA exit.

## Round 05: An EMA6/24 reversal exit may retain trends longer than PSAR while exiting earlier than Supertrend.

Change: Replace baseline PSAR-flip exit with opposite EMA6/24 alignment only.

Observed: 17,509 trades; 4/21 positive; 4/21 pass. Ranking key: [4, 0.040360733522311065, -0.045151051421655486]. Run `01453288eca6b0b8e8e0`; audit passed.

Passing instruments: HK33_HKD, NAS100_USD, USD_JPY, XAU_USD.

Post-result lesson: EMA exits reduce breadth to4 and fail to repair the median score. USDJPY improves to4.51%/year and6positiveyear buckets, but that isolated result does not support a universal change. Restore PSAR exit and test shorter maximum holding.

## Round 06: A24-bar holding cap may limit stale confirmed trends while retaining the original PSAR reversal exit.

Change: Shorten baseline maximum holding from60to24 observed hourly bars only.

Observed: 25,604 trades; 8/21 positive; 8/21 pass. Ranking key: [8, 0.025194232121792372, -0.04141722995180399]. Run `02ad9a00b806a7738da6`; audit passed.

Passing instruments: DE30_EUR, HK33_HKD, JP225_USD, NAS100_USD, SPX500_USD, US30_USD, USD_JPY, XAU_USD.

Post-result lesson: The24-bar cap leaves trade counts and passing set unchanged, with small score changes; long residual holding is not the main loss mechanism. Baseline60 remains slightly better on median passing score. Test whether the4%profit cap truncates the few profitable trends.

## Round 07: Removing the fixed profit target may let the original PSAR exit capture larger continuation tails.

Change: Remove baseline4%take-profit while retaining PSAR exit,60-bar cap and2%stop.

Observed: 25,604 trades; 9/21 positive; 9/21 pass. Ranking key: [9, 0.019109938291910065, -0.0387118383724122]. Run `292a6f618ef81a71afbd`; audit passed.

Passing instruments: BCO_USD, DE30_EUR, HK33_HKD, JP225_USD, NAS100_USD, SPX500_USD, US30_USD, USD_JPY, XAU_USD.

Post-result lesson: Removing target raises breadth8to9, turns BCO positive and materially reduces BTC/WTICO losses, despite lower median passing score. Winning-tail truncation matters. Keep no-target as new parent; test a tighter target as a falsification control before filtering entries.

## Round 08: A2%profit target is a tighter-tail control for the hypothesis that trend winners need room to extend.

Change: Set take-profit to2%instead of4%, retaining baseline entry and exits.

Observed: 25,604 trades; 7/21 positive; 7/21 pass. Ranking key: [7, 0.013628698075310131, -0.05596719059649778]. Run `bf422eaf8933e2cd3c67`; audit passed.

Passing instruments: DE30_EUR, HK33_HKD, JP225_USD, SPX500_USD, US30_USD, USD_JPY, XAU_USD.

Post-result lesson: Tightening target to2%reduces breadthto7 and worsens median-all score to-5.60%/year; BTC/ETH losses deepen. This supports preserving uncapped trend tails rather than a fixed small target. Test established-trend agreement on the no-target parent.

## Round 09: Requiring price on the EMA60 trend side may remove countertrend confirmed PSAR flips while leaving profitable tails uncapped.

Change: Add sign-consistent close-versus-EMA60 filter to no-target round7.

Observed: 21,929 trades; 10/21 positive; 10/21 pass. Ranking key: [10, 0.020789180550465813, -0.006052158218529413]. Run `bf613485e7df3215a52d`; audit passed.

Passing instruments: BCO_USD, BTC_USD, DE30_EUR, HK33_HKD, JP225_USD, NAS100_USD, SPX500_USD, US30_USD, USD_JPY, XAU_USD.

Post-result lesson: EMA60 agreement broadens passes9to10, turns BTC positive, and improves median-all score from-3.87%to-0.61%/year while retaining every-month activity. This is a useful causal filter. Test mild path-efficiency screening on this improved parent.

## Round 10: A mild24-bar path-efficiency floor may avoid choppy confirmed trends after EMA60 agreement.

Change: Add efficiency_24greaterthan0.15to both sides of round9.

Observed: 13,651 trades; 5/21 positive; 4/21 pass. Ranking key: [4, 0.007194821900519392, -0.02534069651394234]. Run `e0cdf8fbc007eba0bcbb`; audit passed.

Passing instruments: DE30_EUR, HK33_HKD, USD_JPY, XAU_USD.

Post-result lesson: A mild efficiency floor sharply reduces breadth10to4 and introduces monthly gaps. Higher path efficiency is not automatically better for this flip-entry timing. Test the opposite interpretation: exclude already highly efficient, potentially mature moves.

## Round 11: Excluding very efficient24-bar paths may avoid mature trends while preserving earlier confirmed continuation entries.

Change: Add efficiency_24lessthan0.5to round9 instead of the failed lower-bound filter.

Observed: 20,626 trades; 10/21 positive; 10/21 pass. Ranking key: [10, 0.023849445725317907, -0.002475378117685118]. Run `5f3edfe10b76fee78f75`; audit passed.

Passing instruments: BCO_USD, BTC_USD, DE30_EUR, HK33_HKD, JP225_USD, NAS100_USD, SPX500_USD, US30_USD, USD_JPY, XAU_USD.

Post-result lesson: Excluding efficiency>=0.5 retains10passing instruments and improves both medians, while USDJPY is positive in all7reported year buckets. It remains an adaptive historical result; mature-trend filtering is more useful here than minimum efficiency. Test whether Supertrend agreement adds value beyond EMA60 and this upper bound.

## Round 12: Supertrend agreement may be redundant once confirmed PSAR persistence,EMA60 direction and a mature-trend filter are required.

Change: Remove the Supertrend entry gate from round11only.

Observed: 26,760 trades; 10/21 positive; 10/21 pass. Ranking key: [10, 0.03775570202412227, -0.013158004148621614]. Run `0ee4f105fc99b04a7b2b`; audit passed.

Passing instruments: BCO_USD, DE30_EUR, HK33_HKD, JP225_USD, NAS100_USD, US30_USD, USD_JPY, WTICO_USD, XAG_USD, XAU_USD.

Post-result lesson: Removing Supertrend keeps10passes but rotates winners: WTICO/XAG become positive while BTC/SPX lose. Median passing score improves to3.78%/year, although median-all worsens. This is a breadth tie with instrument-dependent tradeoffs, not universal dominance. Test whether discrete flip timing adds value versus persistent PSAR alignment.

## Round 13: Three-bar persistent PSAR alignment with EMA60 agreement may support repeated continuation opportunities without requiring a specific flip age.

Change: Replace exact flip-after-three event with held-for-three PSAR direction on round12.

Observed: 38,229 trades; 7/21 positive; 7/21 pass. Ranking key: [7, 0.03257603783860947, -0.042432362188172985]. Run `730a33a2eb7a6794d9db`; audit passed.

Passing instruments: BCO_USD, DE30_EUR, HK33_HKD, NAS100_USD, USD_JPY, WTICO_USD, XAG_USD.

Post-result lesson: Persistent-state entries increase trades43%and lower breadth10to7, with worse median-all score. Entry age matters; repeated continuation participation after exits is not free edge. Restore the event template and test Supertrend as the originating event.

## Round 14: A Supertrend flip followed by three PSAR-aligned closes may identify continuation earlier in a stronger trend transition.

Change: Change the originating event from PSAR flip to Supertrend flip while retaining the three-bar PSAR condition and other round12 rules.

Observed: 12,005 trades; 8/21 positive; 7/21 pass. Ranking key: [7, 0.008905405619483971, -0.013030718977251029]. Run `5995570563378bfac9db`; audit passed.

Passing instruments: CN50_USD, HK33_HKD, NAS100_USD, UK100_GBP, USD_CHF, USD_JPY, WTICO_USD.

Post-result lesson: Supertrend-event entries halve trade count and broaden different assets such as CN50/USDCHF, but only7pass and JP225 fails a month. It is a distinct weaker branch. Return to the10-pass PSAR-event parent and test whether price is on the continuation side of its rolling range.

## Round 15: A confirmed PSAR continuation close on the directional side of the prior24-bar midpoint may reject weak follow-through.

Change: Add range-position midpoint agreement to round12.

Observed: 23,242 trades; 11/21 positive; 11/21 pass. Ranking key: [11, 0.026814799504903057, 0.019174767434834664]. Run `23a479dcf654cd6ad901`; audit passed.

Passing instruments: BCO_USD, BTC_USD, DE30_EUR, HK33_HKD, JP225_USD, NAS100_USD, US30_USD, USD_JPY, WTICO_USD, XAG_USD, XAU_USD.

Post-result lesson: Directional rolling-range midpoint agreement increases breadth10to11 and produces the first positive median-all score(+1.92%/year). BTC turns positive while all21retain complete-month entries. Test whether unusually large signal bars are late-entry shocks rather than attractive continuation.

## Round 16: Avoiding signal bars wider than1.5WilderATR may reduce buying or selling after transient shocks in confirmed trends.

Change: Add range_atrlessthan1.5to both sides of round15.

Observed: 20,521 trades; 11/21 positive; 11/21 pass. Ranking key: [11, 0.0390031492016076, 0.012279812957367816]. Run `ee98dd2b05da3dac5864`; audit passed.

Passing instruments: BTC_USD, DE30_EUR, HK33_HKD, JP225_USD, NAS100_USD, SPX500_USD, US30_USD, USD_JPY, WTICO_USD, XAG_USD, XAU_USD.

Post-result lesson: Shock exclusion retains11passes and raises median passing score to3.90%/year, with SPX replacing BCO; median-all falls slightly to1.23%. This remains a tradeoff across instruments. Use side ablations to test whether gains come mainly from directional drift.

## Round 17: A long-only ablation can reveal whether the improved continuation template relies on upward directional drift.

Change: Remove short entries and their unused indicator exit from round16; keep all21instruments.

Observed: 11,072 trades; 12/21 positive; 10/21 pass. Ranking key: [10, 0.05059645498130524, 0.022004977150859428]. Run `91f67da64904c964502f`; audit passed.

Passing instruments: BCO_USD, BTC_USD, DE30_EUR, NAS100_USD, SPX500_USD, US30_USD, USD_JPY, WTICO_USD, XAG_USD, XAU_USD.

Post-result lesson: Long-only improves12positive instruments and median-all to2.20%/year, but HK33/JP225each miss a complete month, leaving10passes. This exposes substantial directional drift and a frequency cost, so it does not outrank the11-pass two-sided template. Test complementary short-only behavior.

## Round 18: A short-only ablation separates downside continuation value from the long drift visible in round17.

Change: Remove long entries and their unused indicator exit from round16; retain every instrument.

Observed: 9,449 trades; 4/21 positive; 0/21 pass. Ranking key: [0, 0.0, -0.02026077314092116]. Run `5424136794fe270eebb6`; audit passed.

Passing instruments: none.

Post-result lesson: Short-only has4positive instruments but none trade every complete month;17instruments have nonpositive scores. Long-side drift is material. Two-sided execution improves monthly coverage for otherwise positive HK33/JP225, so retain both sides and test local confirmation stability on the improved rules.

## Round 19: With redundant Supertrend gating removed and price-location filters added,two-bar PSAR confirmation may capture continuation earlier without the original one-bar timing failure.

Change: Reduce confirmation from three to two bars on round16only.

Observed: 20,230 trades; 10/21 positive; 10/21 pass. Ranking key: [10, 0.02440012068435625, -0.009814024155921156]. Run `313680f6f7ace5e9fad7`; audit passed.

Passing instruments: BCO_USD, DE30_EUR, HK33_HKD, NAS100_USD, SPX500_USD, US30_USD, USD_JPY, WTICO_USD, XAG_USD, XAU_USD.

Post-result lesson: Two-bar confirmation yields10passes versus11atthree bars, with JP225/BTC losing positivity but BCO improving. The chosen entry age is locally sensitive rather than monotonically better when earlier. Complete the first stage with the later adjacent confirmation.

## Round 20: Four-bar PSAR confirmation tests whether the selected three-bar continuation template survives a nearby delay.

Change: Increase confirmation from three to four bars on round16only.

Observed: 20,192 trades; 9/21 positive; 9/21 pass. Ranking key: [9, 0.019822903472586157, -0.008146003632423753]. Run `00bf47b4b053b6feb1e5`; audit passed.

Passing instruments: BCO_USD, DE30_EUR, HK33_HKD, JP225_USD, NAS100_USD, US30_USD, USD_JPY, XAG_USD, XAU_USD.

Post-result lesson: Four-bar confirmation reduces breadth to9 versus11 at3 and10 at2. The three-bar selection is locally sensitive; this is a reason for neighborhood and cost stress next stage, not evidence that3 is a universal optimum. All20unique rulesets were fully executed and independently audited.
