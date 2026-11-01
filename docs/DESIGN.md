# Nova design contract

The final decisions in `background/sol6.1design`, reflected in `background/moneta-next/START_HERE.md` and its working rules, are the requirements baseline. Earlier architecture proposals are historical context. In particular, the old assistant's claim that Hybrid selection approved High-Water Mark risk was incorrect and was explicitly withdrawn.

## Scope and acceptance

Deliver a complete, auditable local workflow: raw market data → cleaned Parquet → Hybrid features → YAML compiled to causal SQL → per-instrument trade state machine → detailed results. Integrate real data and inspect actual trades before expanding automated discovery.

The accepted objective is regular actual monthly opportunities and positive arithmetic annualized trade-return score, with higher scores useful for ordering. Same strategy and feature parameters apply across instruments. Per-instrument monthly screening is the initial default; it does not introduce an extra user-approved asset-pool promotion threshold. There is no cash/Buy & Hold gate.

The subsequent user-authorized research campaign permits bounded agent-authored YAML exploration: twelve direction agents, each conducting three stages of twenty distinct rounds, with coordinator review and guidance between stages. Each round uses the existing hourly feature vocabulary and all 21 instruments, keeps the mandatory execution contract, records its rationale/result/lesson, and receives an independent ledger audit. The finite campaign does not authorize an unbounded search service or a new strategy language. Catalogs are isolated by direction while immutable Parquet inputs are shared. Compressed experiment artifacts preserve full trades and signals within local disk capacity. Historical adaptive research is disclosed as such; no new OOS governance is introduced.

Account sizing, leverage, margin, equity curves, account drawdown, HWM, circuit breakers, combined portfolio returns, legacy OOS enforcement, autonomous AI candidate generation, hundreds of indicators, distributed systems, broker integrations and live trading are outside this release. The twelve research families are labels that can overlap, rather than twelve independent sources of edge.

## Components

| Module | Responsibility |
|---|---|
| `data.py` | Archive and hash CSVs, validate source candles, deterministic deduplication, UTC aggregation preserving quotes |
| `store.py` | DuckDB dataset/experiment catalog and Parquet-backed views |
| `catalog.py` | Registered feature contracts, parameters, version, research labels |
| `indicators.py` | Migrated, isolated Supertrend recursion |
| `features.py` | TA-Lib indicators, semantic feature transformations, core/domain snapshots |
| `config.py` / `compiler.py` | Strict safe YAML and reviewed expression vocabulary → past-only SQL |
| `trades.py` | Streaming single-trade lifecycle and execution/cost rules |
| `metrics.py` | Complete calendar-time denominators, explicit monthly zeros, per-instrument screening |
| `runner.py` | Windowed per-instrument evaluation, artifact publication and experiment registration |
| `audit.py` | Independent published-ledger arithmetic, chronology, signal and summary checks |
| `cli.py` | Import, aggregate, feature build, validate, run, finite reviewed batch, inspect, audit |

## Storage and identities

`data/raw_csv/` and `data/raw_parquet/` contain Nova-owned immutable inputs. Hard links avoid copying source bytes; file contents are hashed on import and must never be edited in place. Copying is the fallback across filesystems. Legacy removal does not remove hard-linked contents. A changed source at an already-owned path is rejected unless it is the same linked inode; changed linked content creates a new input identity when reimported. Published derived snapshots remain unchanged. Imports select raw OANDA, canonical or pre-aggregated OHLCV contracts explicitly and validate every source file. Pre-aggregated input requires a complete n_bars count; arbitrary cached indicator columns are ignored and reported. Data producer revisions are unknown unless established independently of the source-code revision.

`data/market/<minutes>m/<snapshot>/` contains one sorted Parquet per instrument and a manifest. Source identities include all file SHA256 hashes, source contract and data version. Raw normalization uses disk-backed DuckDB staging with two threads and a 1 GB memory limit; expensive sorts can spill to `data/tmp/`. Raw CSVs are scanned for schema/time validation and then normalized, not loaded into Python memory.

Complete source duplicates are ordered by quote availability, source filename, then payload SHA256. Conflicting duplicate keys and removed rows are counted. A duplicate payload disagreement is resolved deterministically, rather than silently dependent on thread order. Source filename changes can change the selected payload; names are therefore part of the snapshot identity.

Aggregation starts from cleaned one-minute data. UTC buckets are accepted only with every source minute present. Partial buckets are counted and excluded; no synthetic fill is used. All eight aggregated Bid/Ask fields are available only when every source minute carries quotes. This full-bucket policy is an explicit initial data-adapter choice; it can reduce sample sizes materially in low-activity/session-edge data. Calendar gaps remain gaps. No stored legacy derived features are imported.

`data/features/<minutes>m/<snapshot>/` contains three wide domains per instrument: core (market data + ATR), trend (SMA/EMA/PSAR/Supertrend and semantic outputs), momentum (RSI). DuckDB exposes domain views and unified `features_<minutes>m`. Feature identity includes the market snapshot, timeframe, FEATURE_VERSION, complete parameter set and numerical-library versions. Changing computations requires a version bump. Files are hashed and validated before reuse. New source imports require rebuilding downstream aggregates and features before another experiment can run.

`data/nova.duckdb` holds only catalog records and views over Parquet. The latest snapshot is selected for each kind/timeframe; prior immutable snapshots and runs remain on disk. No old-project code, paths or OOS tokens are needed at runtime. In this local release manifest paths are absolute; relocate a store by rebuilding/registering it, rather than editing a live database's paths.

Experiments identify effective YAML, selected instruments/window, feature snapshot, application source hash and runtime dependency versions. Publication uses a temporary directory renamed after all artifacts and their hashes are written. Repeating identical inputs verifies and reuses the existing run. A failed run leaves a clearly marked temporary directory for diagnosis; it is never registered as complete.

## Feature and time semantics

Features are values observable at `bar_close_time`; “per-bar” does not prohibit historical input to EMA or PSAR. Warm-up NULLs are retained rather than removing an arbitrary block of rows. Recursive state starts at the data snapshot's head, preserving causality but not claiming independence from initialization. Rolling calculations use actual complete observed bars across gaps; no imputed bars are inserted.

The initial library preserves the starter's SMA 6/24 and simple-mean true-range ATR14, adding a separately named Wilder ATR14, EMA 6/24/60, RSI14, PSAR(0.02,0.2), and Supertrend(ATR14,3). ATR-normalized features declare the exact ATR denominator. A feature name always has fixed registered semantics. Parameter search and arbitrary runtime computation are not embedded in YAML.

The requested twelve-direction review extends this library in feature version v2 with fixed prior-24-bar range boundaries, range position/width, breakout and failed-breakout predicates, six-bar ATR-normalized movement, bar range/ATR, relative quote activity, UTC opening hour and 24-bar path efficiency. Boundaries and activity baselines exclude the current bar. Zero denominators remain NULL. These live in the existing core/trend/momentum domains. Each direction has one reviewed hourly YAML hypothesis, with identical rules across instruments and no parameter search. Relative strength uses within-instrument normalized movement; market structure uses rolling ranges rather than future-confirmed pivots.

Temporal conditions use `lag` and windows ending at the current row. Event after N bars means the event was N rows ago and each of the N following rows met the condition; its signal appears only at that confirmation close. Boolean warm-up NULLs never become positive confirmation through negation. Full N-row non-NULL windows are required for `within` and `held_for`, a conservative convention inherited from the starter. Gaps count as elapsed wall time for financing, while N-bar conditions count observed bars.

A requested run slice starts trade state flat but evaluates temporal warm-up using earlier snapshot history. Bounds filter complete bars after signal windows are evaluated. The calendar denominator is the requested interval clipped to each instrument's source coverage; no-trade time is included. Results disclose actual observed bars by month.

## Execution contract

At a bar opening: consume any pending entry; inspect known stop/target gaps; execute any prior close-confirmed exit; otherwise inspect this bar's liquidation-side range. If both stop and target occur with unknown order, choose the stop. Opening target fills are conservative at target, not improved to the gap price. Price exits on the opening of the entry bar are possible if spread/slippage already crosses a boundary. Every fill incurs configured adverse slippage; actual quotes avoid synthetic spread duplication.

At the bar close: if holding, schedule an indicator exit or time exit for next open. If flat and this bar did not exit a trade, an unambiguous entry may be scheduled. Conflicting long/short conditions skip both. An entry scheduled on the last bar expires. An existing trade at end of data exits at that last close.

Stops are `entry_fill × (1 − direction × 0.02)`. Returns are `direction × (exit_fill − entry_fill) / entry_fill`, less a flat round-trip commission fraction and elapsed daily financing fraction. Spread/slippage are already in fills. Intrabar times cannot be inferred from OHLC: `bar_interval` exits use the close timestamp as a reporting/financing approximation. The 2% stop is a trigger, not a guarantee of final net loss.

## Delivery and validation

Tests cover YAML escape rejection, feature typing and causality, nested temporal windows, confirmation timestamps, long/short price arithmetic and quotes, adverse gaps, known-open priority, costs, repeated entries, monthly zeros, partial months, duplicate provenance, source validation, source integrity, per-instrument views, window semantics, replay identities and an independent trade audit. CI installs the same locked environment and runs the data-free suite. Local acceptance additionally rebuilds the full available data and executes the example strategies across its 21 instruments.

