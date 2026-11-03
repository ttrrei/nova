# Nova — Architecture Decision Record (thread of 2026-11-03)

Archive of the design conversation held on 2026-11-03. This records the
decisions, the reasoning behind them, and the agreed target architecture.
It supersedes the earlier "over-engineered" layout (SHA256 snapshot
directories, FROZEN_CORE, artifact-hash manifests) for the rebuild that
follows.

The single guiding principle from the user:

> This project exists so I can, in my spare time, with a small AI budget,
> keep trying and analyzing strategies. It must stay stable and light. It
> must NOT become a "perfectly engineered but useless" artifact.

---

## 1. The core purpose (why we are rebuilding)

- Nova is a personal alpha-discovery tool, **not** a product and **not** a
  compliance/audit system.
- The previous design optimized for cryptographic reproducibility
  (SHA256 directory names, per-run artifact hashes, a frozen-core guard
  that invalidated every historical run on any change). That is over-
  engineering for a tool the owner uses in spare time.
- The alpha itself (custom features, strategy definitions, run results) is
  the source of passive income and **must not be open-sourced**. If the
  alpha formula is shared with enough people, it gets arbitraged away
  ("被均摊").

---

## 2. The git / OCI split (the backbone of the new design)

Two stores, continuously kept in sync:

| Store | Nature | Contents |
|---|---|---|
| **git** | **Open source** (program only) | Base engine code, standard (non-alpha) features, one example strategy (for CI), tests, docs, `config_example.yml` |
| **OCI** (Object Storage) | **Closed** (private data + alpha) | Raw market data, feature snapshots, **custom/alpha feature Python + its tests**, **all strategy YAMLs**, all runs and analysis |

Rules of the split:

- **Base data is NOT copied into the new repo.** It is **downloaded from
  OCI** on demand. (The user explicitly retracted the earlier "move the base
  data in" plan.)
- **All strategies live in OCI**, including analysis output. They are kept
  under continuous sync.
- **Custom (alpha) features are closed-source Python.** They are loaded at
  runtime from an OCI-mounted path and must never be committed to git.
- **`config.yml` is not in git** (may hold OCI credentials / local paths).
  **`config_example.yml` is in git** (documented template, no secrets).
- The user wants the OCI Parquet layer to feel "as continuously managed as
  git" — i.e. treated as a persistent, versioned store even though it is not
  a git repo. (Design goal for a later sync step; not yet built.)
- The new repo's **primary function is to stay in sync with OCI**.

---

## 3. What "from scratch" means (agreed: A, not B)

- **A (chosen):** A fresh, clean repo. We **port** the already-validated
  inner core (trade engine, compiler, metrics, data pipeline) into it, and
  go through each component **together, transparently** — small steps,
  each tested, each committed, each explained. We **drop** the over-
  engineered layers.
- **B (rejected):** Re-deriving the validated trade semantics from nothing.
  Rejected because the causality / 2% stop / gap handling / next-open fill /
  warmup-NULL semantics took real time to pin correctly, and re-deriving
  risks drifting on exactly the details that determine backtest correctness.

Porting preserves the semantics; transparency comes from building it in
reviewable commits, not from throwing the logic away.

---

## 4. The base ("基座") — four small, data-independent components

These are data-independent and may be open-sourced. "Base" is really four
components, not one monolithic SQL parser:

| Component | Responsibility |
|---|---|
| **Feature builder** | From OHLCV, compute feature columns (SMA/EMA/RSI/ATR/PSAR/Supertrend/range/efficiency …) and publish Parquet |
| **YAML → SQL compiler** | Compile entry/exit boolean conditions into past-only SQL over the `features` table |
| **Trade state machine** | Per-bar: confirm signal → fill at next open → 2% stop → take-profit / time exit |
| **Metrics / reporting** | Per-instrument, per-month accumulation into the report |

Only the compiler is "SQL"; holding-period accumulation and reporting live in
Python. The boundary is clean, and none of it depends on the specific data.

---

## 5. Feature model — settled as: Python code, two kinds

### 5.1 Standard (open-source) features
Fixed registered vocabulary: SMA 6/24, EMA 6/24/60, ATR (SMA + Wilder),
RSI 14, PSAR, Supertrend, plus research primitives (prior range, range
position/width, breakout/failed-breakout, 6-bar ATR movement, bar
range/ATR, relative activity, UTC hour, path efficiency). Small, fixed,
shared across instruments. These may be open-sourced.

### 5.2 Custom / alpha features — Python is the floor (agreed)
The user considered an operator-algebra / "strict pseudocode" approach so as
not to be language-locked. Conclusion reached together:

- **Stateless series transforms** (SMA/EMA/RSI/rolling/distance/cross) can
  be described by a fixed operator table with exact specs.
- **Stateful recursive** features (PSAR, Supertrend, and any custom state
  machine: "current value depends on previous value, with branching and
  variable state") **cannot** be expressed as a composition of window
  operators. They are data-driven finite state machines.
- Expressing the stateful class declaratively would require building an
  interpreter/DSL — which the user explicitly rejects as over-engineering.
- **Decision:** all custom features are written as **Python code**, with a
  **contract card** (state variables, transition rule, seed, gap/flip
  boundary) and a **golden test** that pins the output. Code is "a reference
  implementation of the definition"; the contract + test lock the semantics.
  This is exactly how TA-Lib documents PSAR/Supertrend, so it is standard,
  not exotic.
- The custom feature **code + contract + test is alpha and stays in OCI**,
  never in git. Git only keeps a clean extension point: "load feature
  modules from a directory" (generic ones ship with git; the alpha ones load
  from OCI at runtime).

### 5.3 Feature parameters stay FIXED (agreed)
Changing parameters (e.g. SMA 10 vs 11) is treated as overfitting. Parameters
are fixed per registered feature; new features are added, not re-parameterized.

---

## 6. Strategy language — settled rules

- **YAML is the only strategy language.** No SQL, Python, eval, or callbacks
  in strategy files.
- **Feature-vs-feature comparison: ALLOWED (relaxed from before).** The
  compiler previously only allowed `feature op constant`. The restriction is
  a conservative choice, not a technical one — DuckDB handles `col_a > col_b`
  natively. New rule: the right-hand side may be a constant **or** another
  registered feature column. Backward compatible with all 332 existing
  strategies. Example now legal:
  `ema_24 > close AND rsi_14 < 30 AND return_6_atr > 2`.
- **Feature-vs-constant: still allowed** (all 332 existing strategies use
  only this form).
- **No feature arithmetic, no cross-instrument comparison, no arbitrary
  expressions** — only comparisons over registered feature columns (the
  "whitelist column names" remain the only boundary; no SQL fragments in YAML).
- **Temporal operators kept:** `all / any / not`, `held_for`, `within`,
  `after_event`.
- **Comparison operators kept:** `eq / ne / gt / gte / lt / lte`.
- **2% mandatory adverse-price stop: KEPT.** Reason: 30x leverage, so a 2%
  adverse underlying move ≈ 60% account loss. Gap/slippage losses may exceed
  2%. This is a hard account-risk ceiling, not abstract risk management.
- **One trade per instrument; no pyramiding / reversal / same-bar re-entry.**
- **Signals confirm at close, execute at the next observed open.**
- **One strategy = one timeframe** (not 60m entry + 5m exit).

---

## 7. What to DROP (the over-engineering)

- **SHA256 snapshot directory names** (e.g. `22d25208bac99177`). Meaningless
  to the owner; replaced by simple, human-readable paths.
- **FROZEN_CORE.sha256 hard-fail guard.** Removed.
- **Per-run artifact-hash manifest lists** (the 761-line `manifest.json`
  with `artifact_hashes`). Replaced by a small `run_meta.json`
  (strategy name, time window, instruments, date, feature version, git commit).
- **`store.py` / `audit.py` / `doctor.py`** — not needed for the new scope.

What remains as the only real "audit": **tests pin feature semantics, and the
run report shows what actually happened.** Not cryptographic identity.

---

## 8. Feasibility check already performed (the 332 strategies)

All 332 strategy YAMLs were validated against the current compiler grammar:

- **0** use unregistered features; **0** use unsupported operators; **0** fail
  to parse.
- Distinct features used: **17**, all registered. Comparison ops used:
  `eq/gt/gte/lt/lte`. Temporal ops used: `after_event / held_for / within`.
- All are `version: 1`; timeframes `{5, 60}`; stop_loss is **0.02 everywhere**.

**Conclusion:** the existing corpus is safely inside the current grammar, so
it can be migrated and re-run under the new base without syntax changes.
(The feature-vs-feature relaxation only expands expressiveness; it does not
break any existing file.)

---

## 9. Build plan (the rebuild, done transparently step by step)

Working agreement: each step = explain → write a small version → test →
commit → review. No big hidden diffs. No new strategy mining until the base
is complete.

| # | Component | Contents | Test |
|---|---|---|---|
| 1 | **Data (OCI)** | On-demand: download CSV from OCI → clean → 1m/5m/60m aggregate → Parquet. NOT committed to git. | Small CSV in, verify OHLCV correctness |
| 2 | **Features** | 17 standard features + custom-feature extension point (load from OCI) | Compute a segment, verify SMA/EMA/RSI numbers |
| 3 | **Compiler** | YAML→SQL, feature vs feature **and** vs constant, all/any/not, held_for/within/after_event | Compile a strategy, inspect SQL |
| 4 | **Trade engine** | 2% stop, next-open, take-profit, time exit, feature exit, one-trade-per-instrument | Hand-compute 2–3 fills, verify prices |
| 5 | **Metrics + runner** | Per-month / per-instrument score, annualized score, orchestration | One strategy end-to-end |
| 6 | **Migration** | Bring 332 strategies in from OCI, re-run all | Results sane, no crashes |
| 7 | **Polish** | README, CI, final `.gitignore`, `config_example.yml` | `pytest -q` green |

## 10. Outstanding / not yet built

- The **OCI sync** mechanism (the new repo's primary function: staying in
  sync with OCI, including keeping OCI Parquet "as managed as git").
- OCI credentials / mounting — owned by the user; `config.yml` holds them,
  `config_example.yml` documents the shape.
- `feature-vs-feature` compiler change (small, backward-compatible).
- The `supertrend` "contract card + golden test" sample was proposed as the
  zero-risk first step for standardizing custom-feature documentation.

---

## 11. Decisions log (quick reference)

- ✅ git = open-source code only; OCI = data + alpha features + strategies + runs.
- ✅ Base data downloaded from OCI, not copied in.
- ✅ `config.yml` (out of git) + `config_example.yml` (in git).
- ✅ Rebuild = fresh clean repo, port validated core, go through it together.
- ✅ Custom features = Python + contract card + golden test; code stays in OCI.
- ✅ No interpreter / YAML-DSL / operator-DSL for stateful features.
- ✅ Feature parameters stay fixed (anti-overfit).
- ✅ Feature-vs-feature comparison allowed; feature arithmetic still not.
- ✅ 2% stop kept (30x leverage); one trade per instrument; close-confirm/next-open.
- ✅ Drop SHA256 names, FROZEN_CORE, artifact-hash manifests, store/audit/doctor.
- ✅ 332 strategies verified in-grammar; migrate + re-run under new base.
- ✅ No new strategy mining until the base is complete.
- ⬜ OCI sync mechanism — next major build item.
