# Nova Quantitative Strategy Optimization Engine — Business Requirements Document (BRD)

| Version | Date | Author | Status |
|---------|------|--------|--------|
| v1.0 | 2026 | Strategy Discovery Team | Finalized |

---

## 1. Project Overview

### 1.1 Project Background

As quantitative trading becomes increasingly competitive, the efficiency and quality of Alpha strategy discovery have become core competencies for institutional investors. However, traditional strategy development faces several challenges:

- **High manual dependency**: Strategy development relies on experienced traders, resulting in low efficiency and difficulty scaling
- **High overfitting risk**: Small-sample backtesting leads to poor live performance
- **High compute cost**: Exhaustive testing of massive strategy candidate spaces incurs enormous computational overhead
- **Strategy homogenization**: Lack of systematic deduplication results in redundant strategies wasting computing resources

**Nova** emerges to address these challenges, aiming to build an **ultra-lightweight, highly reusable, low-compute-cost** automated Alpha strategy discovery and optimization engine.

### 1.2 Project Positioning

| Dimension | Description |
|-----------|-------------|
| **Core Positioning** | Alpha strategy exploration and optimization engine |
| **Core Value** | Ultra-lightweight, highly reusable, low compute cost |
| **Delivery Form** | Lightweight Python codebase hosted on GitHub |
| **Design Principle** | Ship first, reject over-engineering |

### 1.3 Engineering Boundaries

> **Important Note**: This project strictly focuses on strategy optimization and Alpha algorithm validation. The following modules are decoupled as independent follow-up engineering and are out of scope:

- Live order execution system
- Streaming real-time computing engine
- Operations monitoring and alerting system
- Capital management and position control system

---

## 2. Business Objectives and Core Requirements

### 2.1 Core Business Objectives

| ID | Business Objective | Quantifiable Metric |
|----|-------------------|---------------------|
| **BG-01** | Establish automated strategy discovery pipeline | End-to-end automation from concept to evaluation, no manual intervention |
| **BG-02** | Implement AI-driven strategy generation | Gemini + Gemma multi-model collaboration to generate diverse Alpha strategies |
| **BG-03** | Build strict anti-overfitting system | Time uniformity + win-rate stability dual hard constraints |
| **BG-04** | Optimize compute cost | Four-level progressive deduplication engine to intercept redundant strategies |
| **BG-05** | Support self-evolution of strategies | Schema evolution pipeline to continuously absorb unsupported strategy logic |

### 2.2 Functional Requirements

#### 2.2.1 Data Management Module

| ID | Requirement | Priority |
|----|-------------|----------|
| **FR-DM-01** | Incrementally pull raw OHLCV Parquet files from OCI Object Storage (data collection handled by an external VM) | P0 |
| **FR-DM-02** | Organize local Bronze Layer Parquet files partitioned by year/month/instrument | P0 |
| **FR-DM-03** | Build Bronze → Silver → Gold three-tier data architecture | P0 |
| **FR-DM-04** | Support 1min/5min/1h multi-timeframe data resampling | P0 |
| **FR-DM-05** | Implement Session isolation to prevent cross-weekend/holiday data distortion | P0 |
| **FR-DM-06** | Build wide-table feature library (trend/volatility/momentum) with sparse parameters [12,24,48,72] | P1 |

#### 2.2.2 AI Strategy Generation Module

| ID | Requirement | Priority |
|----|-------------|----------|
| **FR-AI-01** | Gemini 3.5 Flash Lite generates strategy class YAML templates | P0 |
| **FR-AI-02** | Gemma 4 26B two-stage generation (Idea → Compiler) | P0 |
| **FR-AI-03** | Gemma 4 31B custom feature writing with AST review | P1 |
| **FR-AI-04** | Tail Check sandbox to verify no look-ahead bias in new features | P1 |
| **FR-AI-05** | Auto-precipitate unsupported strategy logic to Backlog | P0 |

#### 2.2.3 Backtest Engine Module

| ID | Requirement | Priority |
|----|-------------|----------|
| **FR-BT-01** | DuckDB-based vectorized backtest engine | P0 |
| **FR-BT-02** | R-Multiple return normalization (normalized to 1R based on initial stop-loss distance) | P0 |
| **FR-BT-03** | TP/SL pessimistic collision detection (prioritize stop-loss when both hit same candle) | P0 |
| **FR-BT-04** | Single-position state machine (prohibit position stacking) | P0 |
| **FR-BT-05** | Zero debounce design (choppy wear as hard metric for Alpha coverage capability) | P0 |
| **FR-BT-06** | 21 instruments with dedicated pip sizes and spread attribute table | P0 |
| **FR-BT-07** | Multi-timeframe alignment (5m signals reference previous closed 1h candle) | P0 |

#### 2.2.4 Deduplication Engine Module

| ID | Requirement | Priority |
|----|-------------|----------|
| **FR-DD-01** | Level 1: Syntax normalization and parameter discretization (AST rearrangement + grid alignment) | P0 |
| **FR-DD-02** | Level 2: SHA-256 strategy fingerprint hash library (millisecond-level comparison) | P0 |
| **FR-DD-03** | Level 3: AI self-reflection retry loop (3 consecutive duplicates triggers new template generation) | P1 |
| **FR-DD-04** | Level 4: Signal correlation deduplication (correlation coefficient > 90% eliminates lower performer) | P0 |

#### 2.2.5 Evaluation Metrics Module

| ID | Requirement | Priority |
|----|-------------|----------|
| **FR-EV-01** | Basic performance metrics: Sharpe Ratio, Calmar Ratio, Profit Factor, Max Drawdown | P0 |
| **FR-EV-02** | Anti-overfitting constraint: Time uniformity (stable distribution of weekly/monthly trade counts) | P0 |
| **FR-EV-03** | Anti-overfitting constraint: Win-rate stability (σ_win_rate < 0.15) | P0 |
| **FR-EV-04** | Position posture ratio (positive/negative return holding time ratio) | P1 |
| **FR-EV-05** | Equity thickness (Area Ratio) integral evaluation | P1 |
| **FR-EV-06** | First-to-Hit target arrival rate | P1 |

---

## 3. Non-Functional Requirements

### 3.1 Performance Requirements

| Metric | Target | Description |
|--------|--------|-------------|
| **Single strategy backtest time** | < 5 seconds | 21 instruments × 1 year historical data |
| **Strategy generation throughput** | ≥ 100/hour | End-to-end AI pipeline |
| **Deduplication interception rate** | ≥ 60% | Intercept redundant strategies before backtesting |

### 3.2 Data Coverage Requirements

| Dimension | Requirement |
|-----------|-------------|
| **Number of instruments** | 21 mainstream instruments |
| **Instrument types** | Forex majors/crosses, precious metals, crude oil, equity indices |
| **Historical depth** | ≥ 1 year |
| **Data granularity** | 1-minute OHLCV |
| **Data source** | OCI Object Storage (upstream: OANDA API via external VM) |

### 3.3 Maintainability Requirements

| Requirement | Description |
|-------------|-------------|
| **Codebase** | Lightweight Python, hosted on GitHub |
| **Schema evolution** | Support YAML Schema version iteration |
| **Strategy archiving** | Strategy Zoo manages reviewed strategies |

---

## 4. Trading Paradigm Definition

### 4.1 Multi-Timeframe State Transition Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                  State Transition Entry Model                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│    1h Candle ─── Trend Direction ──────┐                     │
│                                         ├──► State Transition Entry Signal │
│    5m Candle ─── Entry Point ─────────┘                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Entry Logic Description

| Timeframe | Responsibility | Key Constraint |
|-----------|---------------|---------------|
| **1-hour cycle** | Establish directional bias | — |
| **5-minute cycle** | Capture state transition entry timing | When calling 1h features, strictly lock to previous fully closed candle |

---

## 5. Evaluation Metrics System

### 5.1 Basic Performance Metrics

| Metric | Calculation | Passing Threshold |
|--------|------------|------------------|
| **Sharpe Ratio** | Mean excess return / Return standard deviation | > 1.0 |
| **Calmar Ratio** | Annualized return / Max drawdown | > 1.5 |
| **Profit Factor** | Gross profit / Gross loss | > 1.2 |
| **Max Drawdown** | Maximum peak-to-trough decline | < 20% |

### 5.2 Anti-Overfitting Hard Constraints

| Constraint Type | Specific Requirement | Judgment Criteria |
|-----------------|---------------------|------------------|
| **Time uniformity** | Stable distribution of weekly/monthly trade counts | No significant clustering or sparse periods |
| **Win-rate stability** | Weekly/monthly win-rate standard deviation | σ_win_rate < 0.15 |

### 5.3 Advanced Evaluation Metrics

| Metric | Definition | Evaluation Purpose |
|--------|-----------|-------------------|
| **Position Posture Ratio** | T_profit / T_loss (positive/negative return holding time ratio) | Evaluate entry precision |
| **Equity Thickness (Area Ratio)** | ∫PnL_+(t)dt / ∫|PnL_-(t)|dt | Evaluate profit "thickness" vs. drawdown "depth" |
| **First-to-Hit Rate** | Distribution probability of first reaching specified profit/loss ratio | Evaluate target achievement efficiency |

---

## 6. Data Source and Instrument Specifications

### 6.1 Data Source Specifications

| Item | Specification |
|------|--------------|
| **Upstream data source** | OANDA API (collected by an independent Python script on an external VM) |
| **Nova data entry point** | OCI Object Storage (incrementally pull archived Parquet files) |
| **Raw granularity** | 1-minute OHLCV |
| **Historical depth** | 1 year |
| **Storage format** | Apache Parquet |

### 6.2 Instrument Coverage

| Category | Count | Instruments |
|----------|-------|-------------|
| **Forex majors** | 7 | EUR/USD, GBP/USD, USD/JPY, USD/CHF, AUD/USD, NZD/USD, USD/CAD |
| **Forex crosses** | 6 | EUR/GBP, EUR/JPY, GBP/JPY, EUR/CHF, EUR/AUD, GBP/AUD |
| **Precious metals** | 2 | XAU/USD (Gold), XAG/USD (Silver) |
| **Crude oil** | 2 | WTI, Brent |
| **Equity indices** | 4 | US30, US100, US500, US2000 |

### 6.3 Instrument Attribute Table Example

| Instrument | Pip Size | Spread Type | Notes |
|------------|----------|------------|-------|
| EUR/USD | 0.0001 | Dynamic | — |
| XAU/USD | 0.01 | Percentage | — |
| US30 | 1 | Fixed | — |

---

## 7. Project Milestones

| Phase | Deliverable | Status |
|-------|-------------|--------|
| **Phase 1** | System design document (DESIGN.md) finalized | ✅ Completed |
| **Phase 2** | Data pipeline (Bronze → Silver → Gold) | 🚧 In Progress |
| **Phase 3** | YAML strategy Schema definition | 📋 Pending |
| **Phase 4** | Vectorized backtest engine | 📋 Pending |
| **Phase 5** | Deduplication engine | 📋 Pending |
| **Phase 6** | Evaluation metrics calculator | 📋 Pending |
| **Phase 7** | AI strategy generation pipeline integration | 📋 Pending |
| **Phase 8** | Schema evolution pipeline | 📋 Pending |
| **Phase 9** | Strategy Zoo management | 📋 Pending |

---

## 8. Design Philosophy

| Principle | Description |
|-----------|-------------|
| **Ship First** | Reject over-engineering; lightweight Python codebase, hosted on GitHub |
| **Pure Alpha First** | Strip position management and execution layer; focus on evaluating signal quality of the strategy itself |
| **AI as Toolchain** | AI models are workers in the strategy factory, not black-box decision makers |
| **Anti-Overfitting as First Principle** | Time uniformity, win-rate stability, signal correlation deduplication — layer-by-layer filtering of pseudo-strategies |
| **Evolving Expressiveness** | Unsupported ideas are not discarded; precipitate → review → elevate dimension; system self-evolves |

---

*Document Version: v1.0 | Maintainer: Strategy Discovery Team*
