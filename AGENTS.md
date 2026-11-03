# Nova working contract

The final user decisions in background/sol6.1design and background/moneta-next/START_HERE.md take precedence over earlier proposals. Read docs/DESIGN.md before changing scope.

- YAML is the only strategy language; no arbitrary SQL, Python, eval or callbacks in strategies.
- Registered causal per-bar features live in a Hybrid store: core and domain wide Parquet tables queried by DuckDB. Strategy temporal conditions compile to past-only SQL.
- Universal means identical rules and feature parameters across instruments. Report each instrument; never sum their returns into a portfolio.
- Mandatory exit at an adverse underlying-price move of 2% from each actual entry fill. Gap/slippage losses may exceed 2%.
- Trade-level research only. No sizing, leverage, margin, equity, account CAGR, HWM or account circuit breakers.
- Signals confirm at close, execute at the next observed open. One trade per instrument; no pyramiding/reversal/same-bar re-entry. Unknown intrabar ordering favors the losing exit; known opening chronology takes precedence.
- Monthly opportunities are actual openings, including zero-entry months. Annualized score is the arithmetic sum of net trade returns divided by full calendar years (365.25 days).
- Reuse historical data/research without legacy OOS machinery. Preserve activity-volume provenance.
- Feature computation changes require a FEATURE_VERSION bump. Snapshot identity includes inputs, timeframe, feature settings and versions.
- Test causality, temporal confirmation, long/short fills/stops/gaps/costs, zero-trade months, data contracts and reproducibility.
- Integrate and inspect real trades before expanding features or adding AI search. No distributed infrastructure or speculative platform modules.
- Never modify background/ or legacy/. Runtime code must not import from either.
- Repo visibility policy (user directive, supersedes earlier notes): every folder in the project stays visible in the code repository. No directory is ignored wholesale; large data files and generated run artifacts are excluded by file type (`*.parquet`, `*.csv`, `*.duckdb`, `*.npy`, `*.zip`, `*.gz`, `*.so`, `*.log`, `*.pyc`/`__pycache__`), and each folder keeps a tracked `README.md` placeholder so the directory remains visible while its heavy contents stay out of the repository.

