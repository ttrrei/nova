# Nova Quantitative Strategy Optimization Engine — System Architecture Design Document (SAD)

| Version | Date | Author | Status |
|---------|------|--------|--------|
| v1.0 | 2026 | Strategy Discovery Team | Finalized |

---

## 1. System Overview

### 1.1 System Positioning

Nova is an Alpha strategy automated discovery and optimization system for quantitative trading. Adopting multi-timeframe state transition strategy as the core trading paradigm, it achieves a fully automated closed loop from strategy concept, compilation, deduplication, to evaluation through an AI-driven strategy generation pipeline and vectorized backtest engine.

### 1.2 System Boundaries

| Included Scope | Excluded Scope |
|----------------|----------------|
| Strategy optimization and Alpha algorithm validation | Live order execution |
| AI strategy generation pipeline | Streaming real-time computing |
| Vectorized backtest engine | Operations monitoring and alerting |
| Four-level progressive deduplication engine | Capital management and position control |

---

## 2. Overall Architecture

### 2.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           Nova System Architecture                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐    │
│  │  OCI Object │────►│  Data       │────►│  DuckDB     │────►│  Gold Layer │    │
│  │  Storage    │     │  Pipeline   │     │  Bronze     │     │  (Features) │    │
│  └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘    │
│         │                                    │                      │          │
│         │                                    ▼                      │          │
│         │                            ┌─────────────┐                │          │
│         │                            │  Silver     │                │          │
│         │                            │  Layer      │                │          │
│         │                            └─────────────┘                │          │
│         │                                  │                          │          │
│         │                                  └──────────┬───────────────┘          │
│         │                                             │                          │
│         ▼                                             ▼                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                        AI Strategy Generation Pipeline                    │    │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                │    │
│  │  │   Gemini     │───►│   Gemma      │───►│   Gemma      │                │    │
│  │  │  3.5 Lite    │    │  4 26B       │    │  4 31B       │                │    │
│  │  │  (Architect) │    │  (Tuner)     │    │  (Feature)   │                │    │
│  │  └──────────────┘    └──────────────┘    └──────────────┘                │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                        │                                        │
│                                        ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                        Backtest & Evaluation Engine                      │    │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                │    │
│  │  │  YAML Parser │───►│  Vectorized  │───►│   Metrics    │                │    │
│  │  │              │    │  Tester      │    │  Evaluator   │                │    │
│  │  └──────────────┘    └──────────────┘    └──────────────┘                │    │
│  │         │                                                              │    │
│  │         ▼                                                              │    │
│  │  ┌──────────────────────────────────────────────────────────────────┐ │    │
│  │  │              Four-Level Progressive Deduplication Engine            │ │    │
│  │  │  Level 1: Syntax  │ Level 2: SHA-256  │ Level 3: AI Retry │ L4 │ │    │
│  │  └──────────────────────────────────────────────────────────────────┘ │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                        │                                        │
│                                        ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                        Strategy Archive Layer                            │    │
│  │  ┌─────────────────────┐        ┌─────────────────────┐               │    │
│  │  │   Strategy Zoo      │        │   Ideas Backlog     │               │    │
│  │  │   (Reviewed)        │        │   (Unsupported)     │               │    │
│  │  └─────────────────────┘        └─────────────────────┘               │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Architecture

### 3.1 Medallion Architecture

Adopts Medallion Architecture combined with DuckDB local vectorized queries to build a Bronze → Silver → Gold three-tier data architecture:

```
┌────────────────────────────────────────────────────────────────────┐
│                       Medallion Data Architecture                  │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   OCI Object Storage                                                    │
│   (External VM collects from OANDA API)                                 │
│        ▼                                                            │
│   ┌─────────┐     ┌─────────┐     ┌─────────┐                      │
│   │ Bronze  │────►│ Silver  │────►│  Gold   │                      │
│   │  (Raw)  │     │(Cleansed)│    │(Features)│                     │
│   └─────────┘     └─────────┘     └─────────┘                      │
│        │               │               │                            │
│        ▼               ▼               ▼                            │
│   Parquet           Parquet         Parquet                         │
│   (OCI Storage)    (Local)         (Local)                         │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### 3.2 Bronze Layer (Raw Layer)

| Item | Specification |
|------|--------------|
| **Data source** | OCI Object Storage (upstream: OANDA API collected by external VM) |
| **Data content** | 1-minute OHLCV raw data |
| **Storage format** | Parquet |
| **Storage location** | OCI Object Storage |
| **Partitioning strategy** | Partitioned by year / month / instrument |
| **Retention policy** | Complete raw data preservation, immutability |

### 3.3 Silver Layer (Cleansed Layer)

| Item | Specification |
|------|--------------|
| **Data content** | Cleansed and aligned base tables |
| **Resampling** | 1min → 5min / 1h |
| **Session isolation** | Mark trading sessions / overnight sessions |
| **Anti-distortion processing** | Cross-weekend / cross-holiday window rolling calculation isolation |
| **Storage format** | Parquet (Local) |

### 3.4 Gold Layer (Wide-Table Feature Library)

| Item | Specification |
|------|--------------|
| **Feature types** | feat_trend.parquet, feat_volatility.parquet, feat_momentum.parquet |
| **Sparse parameters** | Representative parameters such as [12, 24, 48, 72] |
| **Query method** | DuckDB VIEW zero-copy stitching |
| **Storage format** | Parquet (Local) |

### 3.5 Data Query Mechanism

```python
# DuckDB VIEW for seamless base table and wide-table stitching
CREATE VIEW strategy_signals AS
SELECT
    s.timestamp,
    s.close,
    t.ema_12, t.ema_24, t.ema_48, t.ema_72,
    v.atr_12, v.atr_24, v.atr_48, v.atr_72,
    m.rsi_12, m.rsi_24, m.rsi_48, m.rsi_72
FROM silver_5m s
JOIN gold_trend t ON s.timestamp = t.timestamp
JOIN gold_volatility v ON s.timestamp = v.timestamp
JOIN gold_momentum m ON s.timestamp = m.timestamp;
```

---

## 4. Multi-Timeframe Alignment Mechanism

### 4.1 Look-Ahead Bias Elimination

| Constraint | Implementation |
|------------|----------------|
| **5min signal calculation** | When calling 1h features, strictly lock to previous fully closed 1h candle |
| **Timestamp alignment** | Based on UTC timestamp exact matching |
| **Boundary handling** | Session boundaries do not cross-reference features across periods |

### 4.2 Timeframe Responsibility Division

| Timeframe | Responsibility | Data Source |
|-----------|---------------|-------------|
| **1 hour** | Trend direction determination | Gold Layer 1h base table |
| **5 minutes** | Entry point capture | Gold Layer 5m base table + 1h features |

---

## 5. AI Strategy Generation Pipeline

### 5.1 Three-Tier Model Division

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      AI Strategy Generation Pipeline                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                    Gemini 3.5 Flash Lite                                │    │
│  │                         — Strategy Class/Template Architect              │    │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │    │
│  │  │ • Generate new YAML templates (define state logic structure      │  │    │
│  │  │   and variable parameter ranges)                                 │  │    │
│  │  │ • Periodically audit Strategy Zoo                                 │  │    │
│  │  │ • Review high-frequency backlog entries                           │  │    │
│  │  └─────────────────────────────────────────────────────────────────┘  │    │
│  └────────────────────────────────────┬────────────────────────────────────┘    │
│                                        │ Template Dispatch                     │
│                                        ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                         Gemma 4 26B                                      │    │
│  │                   — Intra-class Strategy Tuner (Two-Stage Call)          │    │
│  │                                                                          │    │
│  │  ┌─────────────────────────────┐    ┌─────────────────────────────┐     │    │
│  │  │   Call 1: Idea Stage        │    │  Call 2: Compiler Stage      │     │    │
│  │  ├─────────────────────────────┤    ├─────────────────────────────┤     │    │
│  │  │ Inputs:                    │    │ Inputs:                       │     │    │
│  │  │  • Parameter space map     │    │  • Call 1 Idea output        │     │    │
│  │  │  • Top-2 benchmarks        │    │  • Current strategy class     │     │    │
│  │  │    + dead zones            │    │    YAML Schema               │     │    │
│  │  │  • Last 3 trajectories     │    │                               │     │    │
│  │  │ (≤ 250 Tokens)            │    │ Outputs:                      │     │    │
│  │  │                            │    │  • Executable YAML            │     │    │
│  │  │ Outputs:                  │    │  • unsupported_ideas.json     │     │    │
│  │  │  Plain-text Alpha concept  │    │   (unsupported logic stripped) │     │    │
│  │  └─────────────────────────────┘    └─────────────────────────────┘     │    │
│  └────────────────────────────────────┬────────────────────────────────────┘    │
│                                        │                                        │
│                                        ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                         Gemma 4 31B                                      │    │
│  │                    — Custom Feature Writer                               │    │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │    │
│  │  │ • Write Python / DuckDB SQL new indicator code                  │  │    │
│  │  │ • AST static code review (intercept look-ahead syntax)           │  │    │
│  │  │ • Tail Check sandbox (append new candles to verify no look-       │  │    │
│  │  │   ahead bias)                                                     │  │    │
│  │  └─────────────────────────────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Two-Stage Generation Flow

#### Stage 1: Idea Stage

```python
# Compressed parameter space map input
idea_prompt = """
Current strategy class: {strategy_class}
Parameter space:
  - Top-2 benchmarks: {top_benchmarks}
  - Dead zones: {dead_zones}
  - Last 3 trajectories: {recent_trajectories}
  
Output: Plain-text Alpha concept (≤250 Tokens, not restricted by YAML syntax)
"""
```

#### Stage 2: Compiler Stage

```python
# Map concept to YAML Schema
compiler_prompt = """
Idea: {idea_text}
Schema: {yaml_schema_definition}

Outputs:
  - Executable YAML (if Idea is mappable)
  - unsupported_ideas.json (if contains unexpressible mechanisms)
"""
```

---

## 6. Backtest Engine Design

### 6.1 Core Mechanisms

| Mechanism | Implementation | Purpose |
|-----------|----------------|---------|
| **R-Multiple normalization** | Normalize to 1R based on initial stop-loss distance | Strip position management, evaluate pure Alpha |
| **Pessimistic collision detection** | When TP/SL hit same 5min candle, prioritize stop-loss | Conservative evaluation, avoid over-optimism |
| **Single-position state machine** | Ignore subsequent signals before position is closed | Prevent position stacking |
| **Zero debounce design** | No time cooldown | Treat choppy wear as hard metric for Alpha coverage |

### 6.2 Backtest Engine Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Vectorized Backtest Flow                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   YAML Strategy File                                                │
│        │                                                            │
│        ▼                                                            │
│   ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐      │
│   │  YAML   │────►│ DuckDB  │────►│ Vector  │────►│ Signal  │      │
│   │ Parser  │     │  State  │     │ Tester  │     │  Gen    │      │
│   │         │     │  Trans  │     │         │     │         │      │
│   └─────────┘     │   SQL   │     └─────────┘     └─────────┘      │
│                   └─────────┘         │                               │
│                                        ▼                               │
│                               ┌─────────────────┐                     │
│                               │ Pessimistic TP  │                     │
│                               │ /SL Collision   │                     │
│                               └─────────────────┘                     │
│                                        │                               │
│                                        ▼                               │
│                               ┌─────────────────┐                     │
│                               │  Single Pos     │                     │
│                               │  State Machine   │                     │
│                               └─────────────────┘                     │
│                                        │                               │
│                                        ▼                               │
│                               ┌─────────────────┐                     │
│                               │   PnL Vector    │                    │
│                               │  (R-Multiple)   │                     │
│                               └─────────────────┘                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 6.3 Instrument Attribute Table

```python
# symbol_specs.py
SYMBOL_SPECS = {
    # Forex majors
    "EUR/USD": {"pip": 0.0001, "spread_type": "dynamic", "spread_default": 0.00015},
    "GBP/USD": {"pip": 0.0001, "spread_type": "dynamic", "spread_default": 0.00020},
    "USD/JPY": {"pip": 0.01, "spread_type": "dynamic", "spread_default": 0.015},
    # ... (21 instruments total)
    
    # Precious metals
    "XAU/USD": {"pip": 0.01, "spread_type": "percentage", "spread_default": 0.0003},
    
    # Equity indices
    "US30": {"pip": 1, "spread_type": "fixed", "spread_default": 2},
}
```

---

## 7. Four-Level Progressive Deduplication Engine

### 7.1 Deduplication Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                 Four-Level Progressive Deduplication Engine                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│   Gemma Generated YAML                                                          │
│          │                                                                       │
│          ▼                                                                       │
│   ┌─────────────────┐                                                          │
│   │  Level 1        │                                                          │
│   │  Syntax         │                                                          │
│   │  Normalization   │                                                          │
│   │  • AST reorder   │                                                          │
│   │  • Grid alignment│                                                          │
│   └────────┬────────┘                                                          │
│            │                                                                    │
│            ▼                                                                    │
│   ┌─────────────────┐                                                          │
│   │  Level 2        │──────────────┐                                           │
│   │  SHA-256        │              │                                           │
│   │  Fingerprint    │              │ (hit)                                     │
│   └────────┬────────┘              │                                           │
│            │                        ▼                                           │
│      (miss)              ┌─────────────────┐                                   │
│            │               │  Level 3        │                                   │
│            │               │  AI Self-Reflect│◄──────┐                          │
│            │               │  Retry          │       │                          │
│            │               └────────┬────────┘       │                          │
│            │                        │                │                          │
│            │                        │ 3 consecutive  │                          │
│            │                        │ duplicates      │                          │
│            │                        ▼                │                          │
│            │               ┌─────────────────┐       │                          │
│            │               │  Trigger Gemini │──────┘                           │
│            │               │  Template Regen │                                   │
│            │               └────────┬────────┘                                   │
│            │                        │                                            │
│            │                        ▼                                            │
│            │               ┌─────────────────┐                                   │
│            │               │  Run DuckDB     │                                   │
│            │               │  Vectorized     │                                   │
│            │               │  Backtest       │                                   │
│            │               └────────┬────────┘                                   │
│            │                        │                                            │
│            ▼                        ▼                                            │
│   ┌─────────────────────────────────────────────────────┐                        │
│   │  Level 4                                            │                        │
│   │  Signal Correlation Deduplication                   │                        │
│   │  • Extract buy/sell vectors for 21 instruments     │                        │
│   │  • Calculate correlation with Strategy Zoo          │                        │
│   │  • Correlation > 90% → eliminate lower performer  │                        │
│   └─────────────────────────────────────────────────────┘                        │
│                        │                                                        │
│                        ▼                                                        │
│              ┌─────────────────┐                                                │
│              │  Store in       │                                                │
│              │  Strategy Zoo   │                                                │
│              └─────────────────┘                                                │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Deduplication Level Details

| Level | Mechanism | Intercept Timing | Computational Complexity |
|-------|-----------|------------------|-------------------------|
| **Level 1** | AST reorder + parameter grid alignment | After YAML generation | O(n) |
| **Level 2** | SHA-256 fingerprint hash | After Level 1 passes | O(1) |
| **Level 3** | AI self-reflection retry loop | After hash hit | Calls Gemma |
| **Level 4** | Signal correlation deduplication | After backtest completes | O(m×k) |

---

## 8. Schema Evolution Pipeline

### 8.1 Evolution Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Schema Evolution Pipeline                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   unsupported_ideas.json                                            │
│          │                                                          │
│          ▼                                                          │
│   ┌─────────────────────────────────────────────────────────┐       │
│   │              Gemini 3.5 Periodic Review                  │       │
│   │  ┌───────────────────────────────────────────────────┐  │       │
│   │  │ • Evaluate high-frequency entries                 │  │       │
│   │  │ • Evaluate high-potential entries                 │  │       │
│   │  │ • Generate yaml_parser.py refactoring plan        │  │       │
│   │  └───────────────────────────────────────────────────┘  │       │
│   └────────────────────────┬────────────────────────────────────┘       │
│                             │                                             │
│                             ▼                                             │
│   ┌─────────────────────────────────────────────────────────┐             │
│   │              DuckDB SQL Engine Extension                 │             │
│   │  ┌───────────────────────────────────────────────────┐  │             │
│   │  │ • New state logic support                          │  │             │
│   │  │ • New indicator function additions                 │  │             │
│   │  │ • Schema version iteration                          │  │             │
│   │  └───────────────────────────────────────────────────┘  │             │
│   └─────────────────────────────────────────────────────────┘             │
│                             │                                             │
│                             ▼                                             │
│                      System Capability Upgrade                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 9. Codebase Architecture

### 9.1 Project Structure

```
nova/
├── data_pipeline/                    # Data pipeline module
│   ├── sync_oci.py                   # Incrementally pull Parquet data from OCI Object Storage
│   ├── build_silver.py               # 1min → 5min / 1h aggregation & session isolation
│   └── build_gold_features.py        # Sparse parameter wide-table generation (12, 24, 48, 72)
│
├── ai_engine/                         # AI strategy generation module
│   ├── prompts/                      # Prompt template library
│   │   ├── idea_template.md         # Idea stage template
│   │   └── compiler_template.md     # Compiler stage template
│   ├── gemma_yaml_gen.py             # Gemma 26B two-stage invocation & hash interception retry
│   ├── gemma_feature_writer.py       # Gemma 31B feature writing & Tail Check sandbox
│   └── gemini_auditor.py             # Gemini 3.5 template generation, Backlog review & global audit
│
├── backtest_engine/                  # Backtest engine module
│   ├── symbol_specs.py               # 21 instrument spread & pip attribute table
│   ├── yaml_parser.py                # YAML → DuckDB state transition SQL
│   ├── deduplicator.py               # SHA-256 fingerprint hashing & signal correlation deduplication
│   ├── vectorized_tester.py          # R-Multiple vectorized backtest (pessimistic stop-loss + single position)
│   └── metrics_evaluator.py          # Win-rate stability, time/area ratio (with integral algorithm), First-to-Hit
│
├── ideas_backlog/                     # Overflow ideas archive
│   └── unsupported_ideas.json         # Unsupported logic stripped by Gemma
│
├── strategies_zoo/                   # Strategy archive
│   └── *.yaml                        # YAML strategies that passed hard metric review
│
├── DESIGN.md                         # System design document
├── README.md                         # Project documentation
├── main.py                           # Main optimization flow orchestrator
└── requirements.txt                  # Python dependencies
```

### 9.2 Core Module Dependencies

```
main.py
    │
    ├──► ai_engine/gemini_auditor.py
    │        │
    │        └──► ai_engine/gemma_yaml_gen.py
    │                   │
    │                   └──► ai_engine/gemma_feature_writer.py
    │
    ├──► backtest_engine/deduplicator.py
    │        │
    │        ├──► backtest_engine/yaml_parser.py
    │        │
    │        ├──► backtest_engine/vectorized_tester.py
    │        │
    │        └──► backtest_engine/metrics_evaluator.py
    │
    └──► data_pipeline/* (data preprocessing)
```

---

## 10. Technology Stack

| Category | Technology | Version Requirement |
|----------|------------|---------------------|
| **Language** | Python | 3.12+ |
| **Data engine** | DuckDB | Latest |
| **Storage format** | Apache Parquet | — |
| **Object storage** | OCI Object Storage | — |
| **Data source** | OCI Object Storage (upstream: OANDA API) | v20 |
| **AI model** | Gemini 3.5 Flash Lite | — |
| **AI model** | Gemma 4 26B | — |
| **AI model** | Gemma 4 31B | — |
| **Strategy description** | YAML | 1.2+ |

---

## 11. Security and Fault Tolerance

### 11.1 Sandbox Defense Mechanisms

| Mechanism | Implementation |
|-----------|----------------|
| **AST static review** | Intercept Python code containing look-ahead syntax |
| **Tail Check** | Append new candles to verify historical feature values remain unchanged |
| **Look-ahead detection** | 5m signal calculation strictly references closed 1h candles |

### 11.2 Exception Handling

| Scenario | Handling |
|----------|----------|
| **API call failure** | Exponential backoff retry, alert on failure |
| **Backtest timeout** | Per-instrument timeout isolation, continue other instruments |
| **AI generation failure** | Fallback to template strategy, record to Backlog |

---

*Document Version: v1.0 | Maintainer: Strategy Discovery Team*
