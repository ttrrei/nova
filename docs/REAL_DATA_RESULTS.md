# Real-data acceptance results

Nova 0.2.1, rebuilt locally from the supplied OANDA raw CSVs. These are historical research examples using the final trade-level requirements. An initial-screen pass is not independent validation or approval for live trading.

## Rebuilt data

| Dataset | Bars |
|---|---:|
| 1 minute | 48,588,451 |
| 5 minute | 9,299,520 |
| Excluded partial 5m buckets | 634,703 |
| 60 minute | 654,363 |
| Excluded partial 60m buckets | 179,550 |

Coverage: 2020-01-01T22:00:00+00:00 through 2026-10-23T21:00:00+00:00 (exclusive), across 21 instruments. Source completeness and session gaps vary by instrument.

The import examined 60,958,698 rows in 172 raw CSV files, excluded 2,576 incomplete rows, removed 12,367,671 complete duplicate rows, and found 0 conflicting duplicate keys. All cleaned minute candles carry observed Bid/Ask quotes.

Raw files are owned under `data/raw_csv` using hard links; original legacy files are preserved. The new DuckDB catalog is `data/nova.duckdb`. The 28 registered features are cached in core, trend and momentum Parquet domains for both 5m and 60m data.

## Reviewed examples

| Strategy | Minutes | Actual openings | Instruments passing initial screen | Run |
|---|---:|---:|---:|---|
| ema_pullback | 60 | 14,329 | 3/21 | [report](../runs/46777f5e674a09ea61a3/report.md) |
| mean_reversion_demo | 60 | 34,182 | 0/21 | [report](../runs/b0905f905411e8b7fe22/report.md) |
| psar_supertrend | 60 | 25,604 | 8/21 | [report](../runs/b5419de0b4c8b3f0c280/report.md) |
| trend_hold_demo | 60 | 30,131 | 6/21 | [report](../runs/60dfd5efa8f0b08157fb/report.md) |
| trend_hold_5m | 5 | 440,385 | 0/21 | [report](../runs/24b4d442e4f74830d805/report.md) |

The screen requires a positive arithmetic annualized trade-return score and at least one actual opening in every complete UTC calendar month. All first/last partial months and zero-entry months remain in each summary. Per-instrument results are available in [instrument_results.csv](verification/instrument_results.csv). No asset returns are combined into a portfolio return.

- **psar_supertrend (60m):** DE30_EUR, HK33_HKD, JP225_USD, NAS100_USD, SPX500_USD, US30_USD, USD_JPY, XAU_USD
- **trend_hold_5m (5m):** No instruments pass.
- **mean_reversion_demo (60m):** No instruments pass.
- **trend_hold_demo (60m):** BCO_USD, DE30_EUR, HK33_HKD, NAS100_USD, USD_JPY, XAU_USD
- **ema_pullback (60m):** DE30_EUR, NAS100_USD, USD_JPY

The five-minute example has a different elapsed holding horizon because its 24-bar hold is measured at five-minute cadence. It is retained as a scale/cadence check, rather than selected to improve the hourly results.

## Execution review

All 544,631 trades passed the independent arithmetic, chronology, signal backing, monthly count, stop-level and annualization audit. 57 representative fills cover available exit reasons and directions. The [samples](verification/trade_samples.csv) were independently checked against stored entry/exit-side quotes. 126 aggregate-bar samples across both timeframes and every instrument match their minute inputs, including volume and Bid/Ask OHLC.

Execution uses observed Bid/Ask plus 0.2 bps adverse slippage per side. These examples set commission and financing to zero; those configurable assumptions are recorded in every manifest. Intrabar order remains an OHLC approximation with losing-exit priority, and intrabar exit/financing time uses the bar-close reporting proxy.

## Reproduce

```bash
.venv/bin/nova inspect
.venv/bin/nova batch --strategies strategies
.venv/bin/nova run --strategy strategies/5m/trend_hold.yaml
.venv/bin/python scripts/review_trades.py
.venv/bin/python scripts/verify_rebuild.py
```

Each report links to the locally generated run directory. Large data and run files are intentionally excluded from Git; the compact acceptance evidence is retained here.

After the updated-reference reconciliation, all five runs were executed again under the Nova 0.2.1 source identity. Their trades, signals, summary, compiled SQL, catalog, YAML and report artifacts are byte-identical to the original five runs. See [regression evidence](verification/reference_regression.json).
