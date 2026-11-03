# Pullback reentry phase1 review

Completed20 distinct, full-history,21-instrument rounds; each passed independent ledger audit. All hypotheses, effective YAML, compressed trades/signals and rejected branches are retained.

| Round | Passing instruments | Median passing score | Median all21 score | Trades |
|---:|---:|---:|---:|---:|
|1|3|2.64%|-3.12%|14,329|
|2|4|2.66%|-2.47%|15,051|
|3|4|0.83%|-3.02%|12,656|
|4|4|3.57%|-2.81%|23,690|
|5|6|3.17%|-3.40%|29,672|
|6|5|1.69%|-1.13%|13,272|
|7|4|4.42%|-5.31%|32,925|
|8|5|6.40%|-3.73%|24,672|
|9|2|7.53%|-6.08%|32,529|
|10|5|6.11%|-3.57%|27,836|
|11|7|3.30%|-4.12%|28,698|
|12|3|2.02%|-5.51%|32,104|
|13|7|6.26%|-4.30%|23,938|
|14|9|6.31%|-3.92%|22,320|
|15|10|5.67%|-0.94%|17,769|
|16|9|7.32%|-0.48%|14,589|
|17|10|5.43%|-0.96%|17,832|
|18|13|8.32%|2.31%|9,371|
|19|4|0.77%|-2.78%|9,196|
|20|12|8.89%|3.82%|9,939|

Selected round18, run`00d5575a38e5bda33229`, YAML`/home/ubuntu/work/nova/runs/research_campaign/pullback_reentry/strategies/phase_1_round_18.yaml`. Passing instruments: BCO_USD, BTC_USD, DE30_EUR, ETH_USD, HK33_HKD, NAS100_USD, SPX500_USD, UK100_GBP, US30_USD, USD_JPY, WTICO_USD, XAG_USD, XAU_USD.

The winning rule is long-only: fast EMA alignment and price above EMA60, a shallow RSI<48 pullback within12 bars, one recovery close above50, Supertrend agreement; no take-profit cap, opposite Supertrend exit and48-bar maximum hold. Mandatory2% entry-fill stop and baseline costs remain fixed.

Symmetric progression improved3passes to10 before the long-only control improved it to13. Short-only control achieved4passes. The historical benefit therefore includes directional exposure; it is not evidence that the symmetric entry is universally profitable. Most FX pairs remain weak.

Year buckets include partial endpoints. Descriptive exclusion of each instrument's best year leaves positive totals on BCO_USD, DE30_EUR, ETH_USD, NAS100_USD, SPX500_USD, UK100_GBP, US30_USD, USD_JPY, WTICO_USD, XAG_USD, XAU_USD. Passing totals depend on their best year for BTC_USD, HK33_HKD. This does not change the user's acceptance rule.

## Guidance for phase2

- Preserve long-only winner as primary branch but retain symmetric round15 as control; the directional choice explains much of improvement.
- Test a few close neighbors of pullback memory12, recovery50, hold48 and Supertrend exit before adding more filters.
- Do not infer broad FX edge: most FX pairs remain negative.
- JP225 positivity is blocked by monthly gaps; inspect dates and whether causal relaxation can improve coverage without asset-specific rules.
- Evaluate unchanged rules under higher adverse slippage in later stages; never lower baseline execution costs.
- Inspect yearly concentration and partial2026 separately; no new gate is introduced.
