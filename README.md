# Nova

Nova discovers and inspects trades from **YAML strategies**, registered causal features, **DuckDB**, and **Parquet**. It is the next generation of Moneta, rebuilt in this directory around the final background requirements.

One universal strategy uses the same rules and parameters across instruments. Signals confirm at a completed bar's close and execute at the next observed open. Every actual entry has a mandatory **2% adverse-price stop**. Research is measured per trade and per instrument, with all calendar months shown.

## Get started

Python 3.12+ is required. The development environment in this workspace is `.venv`.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip install -e . --no-deps --no-build-isolation
.venv/bin/nova --help
.venv/bin/nova-doctor
.venv/bin/python -m pytest -q
```

Rebuild from the available legacy raw CSVs. This archives the raw files with hard links where possible, hashes them, rebuilds cleaned one-minute candles, aggregates complete 5m/1h buckets with Bid/Ask quotes, and computes feature snapshots. The legacy source is preserved. The application has no dependency on legacy code or its environment.

```bash
.venv/bin/nova rebuild --source legacy/moneta/data/raw_csv --timeframes 5 60
.venv/bin/nova inspect
.venv/bin/nova validate strategies/trend_hold.yaml
.venv/bin/nova run --strategy strategies/trend_hold.yaml
.venv/bin/nova run --strategy strategies/mean_reversion.yaml
```

Run a selected window or the small, reviewed set of example hypotheses:

```bash
.venv/bin/nova run --strategy strategies/ema_pullback.yaml \
  --instruments EUR_USD XAU_USD BTC_USD --since 2023-01-01 --until 2025-01-01
.venv/bin/nova batch --strategies strategies
.venv/bin/nova run --strategy strategies/5m/trend_hold.yaml
.venv/bin/nova audit runs/<run_id>
```

Date bounds are UTC. `--since` is inclusive; `--until` is exclusive. For example, `--until 2025-01-01` includes completed candles before that date, with close time at most midnight. Feature and temporal warm-up history remains available before the requested run window; trade state starts flat at the window boundary.

The stages are also available separately:

```bash
.venv/bin/nova ingest --source /path/to/csvs --kind oanda
.venv/bin/nova aggregate --minutes 60
.venv/bin/nova features --minutes 60
.venv/bin/nova catalog
```

Use `--store /path/to/data` for an independent data/catalog root and `--output /path/to/runs` for experiments. A custom canonical CSV can be imported with `nova ingest --source bars.csv --kind canonical --minutes 60`, followed by `nova features --minutes 60`.

Native Parquet imports use the same validation and snapshot pipeline:

```bash
# Raw Mid/Bid/Ask minute candles:
.venv/bin/nova ingest --source /path/to/all_data.parquet --kind oanda --minutes 1
# Pre-aggregated bars (time, OHLCV and n_bars), in a separate store:
.venv/bin/nova ingest --source /path/to/ohlcv_1h.parquet --kind ohlcv --minutes 60 --store data/imported
.venv/bin/nova features --minutes 60 --store data/imported
```

`oanda`, `canonical` and `ohlcv` each accept a homogeneous CSV or Parquet dataset. `ohlcv` requires `n_bars`; partial candles are excluded, and open times must align to the declared UTC timeframe. Old Gold files can supply market bars, but **all cached indicators are ignored and recorded in the manifest**, then Nova's own features are recomputed. A trimmed Gold history cannot recover its missing warm-up head; use raw data when available. Native Parquet files are archived under `data/raw_parquet`.

Once the raw files are archived, `nova rebuild --source data/raw_csv` rebuilds entirely from Nova's own inputs. The reviewed hourly batch uses the four YAML files directly inside `strategies/`; the five-minute example is invoked separately.

## Strategy language

```yaml
version: 1
id: example
family: trend_continuation
hypothesis: A confirmed SMA crossover can precede continuation.
timeframe_minutes: 60
entry:
  long:
    after_event:
      bars: 3
      event: {feature: sma_cross_up_6_24, op: eq, value: true}
      condition: {feature: sma_alignment_6_24, op: eq, value: 1}
exit:
  stop_loss_pct: 0.02
  take_profit_pct: 0.04
  max_holding_bars: 24
  long: {feature: sma_alignment_6_24, op: lt, value: 0}
execution:
  spread_bps: 2
  slippage_bps_per_side: 0.2
  commission_bps_round_trip: 0
  financing_bps_per_day: 0
```

Conditions support numeric comparisons (`eq/ne/gt/gte/lt/lte`), boolean combinations (`all/any/not`), and causal temporal operators:

| Operator | Definition |
|---|---|
| `held_for` | Last N observed bars, including this bar, all satisfy a condition |
| `within` | At least one occurrence in the last N observed bars, including this bar |
| `after_event` | Event exactly N bars ago, followed by N bars satisfying the condition; confirm on the Nth following close |

`held_for` and `within` use `{bars: N, condition: ...}`. A complete non-NULL N-bar window is required. Unknown feature values remain unknown through `not`; unconfirmed results become false only at the final signal boundary. Missing calendar bars are never fabricated.

YAML cannot define a feature algorithm, arbitrary SQL, Python, or a callback. A new feature must be implemented, tested, registered, and versioned first. `nova catalog` lists exact identifiers, units, domains, and warm-up requirements. Initial parameter sets are deliberately small and fixed across instruments; they are an initial implementation, rather than a claim about optimal parameters.

## Results

The twelve-direction review supplies exactly one fixed hourly hypothesis per registered
research family under `strategies/directions/`. Run and independently review all twelve:

```bash
.venv/bin/nova features --minutes 60
.venv/bin/python scripts/review_directions.py
```

The review saves immutable experiments under `runs/directions/` and audited results,
quote-fill samples and per-instrument comparisons under `docs/verification/directions/`.
It performs no parameter search. A runnable strategy can fail the monthly/positive-score
screen. Relative strength here means normalized strength within each instrument;
structure uses causal rolling ranges; volume retains its quote-activity provenance.
The session rule filters signal bars by their opening UTC hour, with close confirmation
and execution at the next observed open. Local exchange sessions and daylight saving
are not inferred. Commission and financing are explicitly zero in these examples.

Feature version v2 adds fixed prior-range, path-efficiency, activity, movement and UTC
clock primitives. Older feature snapshots require rebuilding before new experiments;
their published historical runs remain immutable.

Each immutable `runs/<run_id>/` includes:

| Artifact | Contents |
|---|---|
| `report.md` | Human-readable per-instrument screening results |
| `trades.csv` | Actual opening/exit fills, timestamps, stop/target prices, reasons, holding bars, returns and costs |
| `signals.csv` | Candidate rows with at least one true entry/exit condition, including signals while holding |
| `summary.json` | Each UTC month, yearly return sums, per-instrument scores and pooled monthly opening counts |
| `manifest.json` | Effective strategy, dependencies, data/features/code identities, assumptions, artifact hashes |
| `strategy.yaml` | Original submitted YAML |
| `compiled.sql` | Generated past-only SQL |
| `feature_catalog.json` | Registered vocabulary used by the compiler |

`annualized_trade_return_score = sum(net per-trade fractional returns) / full calendar years`, where one year is 365.25 days. It is arithmetic: there is no reinvestment, sizing or account CAGR. Scores are not multiplied by 30. Instrument return sums are never combined into a portfolio return.

The initial per-instrument screen requires a positive score and at least one actual opening in **every complete UTC calendar month**. Partial first/last months are displayed separately. With no complete month, an instrument cannot pass. A month with zero openings remains visible, including its observed-bar count.

## Data and execution

Canonical CSV fields are `instrument,bar_open_time,bar_close_time,open,high,low,close,volume,is_complete`. Timestamps must be timezone-aware; prices must be positive finite OHLC ranges. Optional quotes require all eight `bid_open/high/low/close` and `ask_open/high/low/close` fields, or none. Quotes may be absent on a whole row; that row uses the configured mid-price spread. Incomplete source candles are excluded; invalid data is rejected. OANDA quote activity retains its source meaning in manifests while serving as a volume proxy.

Longs enter at Ask and liquidate at Bid; shorts do the reverse. Observed quotes replace configured spread. Each side receives adverse slippage. Round-trip commission and elapsed daily financing are deducted once. A stop or target is tested on the liquidation-side OHLC; the fixed stop is anchored to the actual entry fill. Unknown intrabar stop/target ordering selects the stop. Opening gaps and pending open exits are processed before later intrabar events. A favorable target gap fills conservatively at the target; an adverse stop gap fills at the opening quote.

One trade per instrument; no additions or reversals. Existing positions ignore new entries. An exit bar cannot generate a replacement entry. Fixed holding N bars includes the entry bar and exits at the following open after N bars complete. Last-bar entry signals cannot fill; remaining trades close at the last close. Intrabar exit time is reported as the bar close with `bar_interval` precision; financing shares this OHLC approximation.

See [the design contract](docs/DESIGN.md), [legacy reuse decisions](docs/MIGRATION.md), and [verification results](docs/VERIFICATION.md).

The [updated-reference review](docs/REFERENCE_REVIEW.md) records additions from the parallel Moneta Next v0.2 work and explicitly separates them from stale notes and future feature work.

