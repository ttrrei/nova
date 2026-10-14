# Nova — Quantitative Strategy Optimization Engine

> Ultra-lightweight, highly reusable, low-compute-cost Alpha strategy exploration and optimization engine.
> Focused solely on strategy optimization and Alpha algorithm validation; live order execution, stream processing, and operations are decoupled as independent follow-up engineering work.

---

## Project Overview

**Nova** is an automated quantitative strategy discovery system targeting mainstream trading instruments including forex, precious metals, crude oil, and stock indices. The system adopts **multi-timeframe state transition** as its core trading paradigm, leveraging an AI-driven strategy generation pipeline and a vectorized backtesting engine to achieve a fully automated closed loop from strategy conception, compilation, deduplication, to evaluation.

### Core Features

- **AI-Driven Strategy Generation**: Gemini + Gemma multi-model collaboration, implementing a three-stage pipeline: Concept → Compile → Audit
- **YAML Self-Describing Strategies**: Strategies expressed in self-contained YAML format, AI-readable and writable, with automatic evaluation result writes
- **Four-Level Progressive Deduplication Engine**: Syntax normalization → SHA-256 fingerprinting → AI self-reflection retry → Signal correlation deduplication, eliminating redundant compute waste
- **Vectorized Backtesting (DuckDB)**: R-Multiple normalized returns, pessimistic collision detection, single-position state machine
- **Strict Anti-Overfitting**: Time uniformity hard thresholds, win-rate volatility constraints, equity thickness integral evaluation
- **Medallion Data Architecture**: Bronze → Silver → Gold three-tier partitioning, DuckDB zero-copy queries

---

## Trading Paradigm

```
1h Candlestick ─── Trend Direction ──────┐
                                         ├──► State Transition Entry Signal
5m Candlestick ─── Entry Point ──────────┘
```

- **Trend Determination**: 1-hour timeframe establishes directional bias
- **Entry Execution**: 5-minute timeframe captures state transition entry timing
- **Look-ahead Bias Elimination**: During 5min signal calculation, 1h features are strictly locked to the previous fully closed candle

---

## Data Architecture

Adopts **Medallion Architecture** combined with DuckDB local vectorized queries:

| Tier | Description | Storage Format |
|------|-------------|----------------|
| **Bronze** | Raw 1-minute OHLCV from OANDA API (partitioned by year/month/instrument) | Parquet (OCI Object Storage) |
| **Silver** | Cleaned, aligned, and resampled (1min → 5min / 1h), session-isolated | Parquet (local) |
| **Gold** | Wide-table feature library (trend / volatility / momentum), sparse parameterization `[12,24,48,72]` | Parquet (local) |

- **Instrument Coverage**: 21 mainstream instruments (forex majors/crosses, precious metals, crude oil, equity indices)
- **Data Depth**: 1 year of historical 1-minute granularity
- **Zero-Copy Queries**: Seamless joins between base tables and wide tables via DuckDB `VIEW`

---

## AI Strategy Generation Pipeline

### Three-Tier Model Division

```
┌──────────────────────────────────────────────────────────────┐
│  Gemini 3.5 Flash Lite — Strategy Class/Template Architect   │
│  Responsibilities: Generate new YAML templates · Audit       │
│  Strategy Zoo · Review Backlog                               │
└──────────────────────┬───────────────────────────────────────┘
                       │ Template Dispatch
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  Gemma 4 26B — Intra-class Strategy Tuner (Two-Stage Call)   │
│  Call 1 (Idea): Parameter Map → Alpha Concept (≤250 Tokens)  │
│  Call 2 (Compiler): Idea + Schema → Executable YAML /        │
│  Overflow Archive                                            │
└──────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  Gemma 4 31B — Custom Feature Writer                         │
│  Responsibilities: Python / DuckDB SQL new indicators ·      │
│  AST Review · Tail Check Sandbox                             │
└──────────────────────────────────────────────────────────────┘
```

### Two-Stage Generation Flow

1. **Idea Stage**: Input compressed parameter space map (Top-2 benchmarks + dead zones + last 3 trajectories), output plain-text Alpha concept
2. **Compiler Stage**: Map concept to YAML Schema; non-expressible logic is stripped to `ideas_backlog/unsupported_ideas.json`

---

## Four-Level Progressive Deduplication Engine

Layers of duplicate interception before consuming vectorized backtesting compute:

```
Gemma Generated YAML
       │
       ▼
 Level 1 ── Syntax Normalization & Parameter Discretization (AST rearrangement + grid alignment)
       │
       ▼
 Level 2 ── SHA-256 Fingerprint Hash Library (millisecond-level comparison, intercept on hit)
       │                                    │
       │ (miss)                         (hit) → Level 3
       ▼                                    │
  Vectorized Backtest                      │
                                      AI Self-Reflection Retry Loop
                                   (3 consecutive duplicates → trigger Gemini template regeneration)
       ▼
 Level 4 ── Signal Correlation Deduplication (buy/sell vector correlation > 90% → eliminate lower performer)
       │
       ▼
  Store in Strategy Zoo
```

---

## Backtest Engine Design

### Core Mechanisms

| Mechanism | Description |
|-----------|-------------|
| **R-Multiple Normalization** | Strip position sizing, normalize by initial stop-loss distance to 1R, evaluate pure Alpha |
| **Pessimistic Collision Detection** | When TP/SL are hit simultaneously on a single 5min candle, force判定为优先触及止损 |
| **Single-Position State Machine** | Ignore subsequent entry signals for the same instrument before position is closed; no stacking |
| **Zero Debounce Design** | No time cooldown; treat choppy market wear as a hard test of strategy Alpha coverage capability |
| **Instrument Attribute Table** | 21 instruments with dedicated pip sizes, dynamic/percentage spreads; no hardcoding |

### Evaluation Metrics System

**Basic Performance**
- Sharpe Ratio
- Calmar Ratio
- Profit Factor
- Max Drawdown

**Anti-Overfitting Hard Constraints**
- Time Uniformity: Stable distribution of weekly/monthly trade counts
- Win-Rate Stability: Weekly/monthly win-rate standard deviation $\sigma_{win\_rate} < 0.15$

**Advanced Evaluation**
- Position Posture Ratio: Positive/negative return holding time ratio $\frac{T_{profit}}{T_{loss}}$
- Equity Thickness (Area Ratio):

$$
\text{Area Ratio} = \frac{\int PnL_{+}(t) \, dt}{\int |PnL_{-}(t)| \, dt}
$$

- First-to-Hit Rate: Distribution probability of first reaching specified profit/loss ratio

---

## Schema Evolution Pipeline

```
unsupported_ideas.json  ──►  Gemini Periodic Review  ──►  yaml_parser.py Refactoring Plan
        ▲                                                    │
        │                                                    ▼
  Gemma Call 2 strips                                  DuckDB SQL Engine Extension
  unexpressible logic                                  System Expressiveness Version Iteration
```

Strategy logic not supported by the current YAML Schema automatically precipitates to Backlog; Gemini periodically reviews high-frequency/high-potential entries to drive the system's expressiveness evolution.

---

## Project Structure

```
nova/
├── data_pipeline/
│   ├── sync_oci.py              # OCI incremental sync
│   ├── build_silver.py          # 1min → 5min / 1h aggregation & session isolation
│   └── build_gold_features.py   # Sparse parameter wide-table generation (12, 24, 48, 72)
├── ai_engine/
│   ├── prompts/                 # Prompt template library (Idea & Compiler templates)
│   ├── gemma_yaml_gen.py        # Gemma 26B two-stage invocation & hash interception retry
│   ├── gemma_feature_writer.py  # Gemma 31B feature writing & Tail Check sandbox
│   └── gemini_auditor.py        # Gemini 3.5 template generation, Backlog review & global audit
├── backtest_engine/
│   ├── symbol_specs.py          # 21 instrument spread & pip attribute table
│   ├── yaml_parser.py           # YAML → DuckDB state transition SQL
│   ├── deduplicator.py          # SHA-256 fingerprint hashing & signal correlation deduplication
│   ├── vectorized_tester.py     # R-Multiple vectorized backtest engine
│   └── metrics_evaluator.py     # Evaluation metrics calculator
├── ideas_backlog/
│   └── unsupported_ideas.json   # Overflow ideas archive stripped by Gemma
├── strategies_zoo/              # YAML strategy archive that passed hard metric review
├── DESIGN.md                    # System design documentation
├── README.md
└── main.py                      # Main optimization flow orchestrator
```

---

## Tech Stack

| Category | Technology |
|----------|------------|
| Language | Python 3.12+ |
| Data Engine | DuckDB + Apache Parquet |
| Object Storage | OCI Object Storage |
| Data Source | OANDA API |
| AI Models | Gemini 3.5 Flash Lite · Gemma 4 26B · Gemma 4 31B |
| Strategy Description | YAML (self-contained spec + evaluation_results) |

---

## Quick Start

> 🚧 Project is in initialization phase; the following steps will be progressively completed with development progress.

```bash
# Clone repository
git clone https://github.com/<your-org>/nova.git
cd nova

# Install dependencies
pip install -r requirements.txt

# Run main flow
python main.py
```

---

## Project Roadmap

- [x] System design documentation finalized
- [ ] Data pipeline (Bronze → Silver → Gold)
- [ ] YAML strategy Schema definition
- [ ] Vectorized backtest engine
- [ ] Deduplication engine
- [ ] Evaluation metrics calculator
- [ ] AI strategy generation pipeline integration
- [ ] Schema evolution pipeline
- [ ] Strategy Zoo management

---

## Design Philosophy

1. **Ship First**: Reject over-engineering; lightweight Python codebase, hosted on GitHub
2. **Pure Alpha First**: Strip position management and execution layer; focus on evaluating signal quality of the strategy itself
3. **AI as Toolchain**: AI models are workers in the strategy factory, not black-box decision makers
4. **Anti-Overfitting as First Principle**: Time uniformity, win-rate stability, signal correlation deduplication — layer-by-layer filtering of pseudo-strategies
5. **Evolving Expressiveness**: Unsupported ideas are not discarded; precipitate → review → elevate dimension; system self-evolves

---

## License

[MIT License](LICENSE)

---

*Document Version: v1.0 | Maintainer: Strategy Discovery Team*
