# Nova Housekeeping Baseline (Stage 0)

Recorded: 2026-11-03 (local time)

- HEAD commit: `f9cd556b0d86d7361b137fac2926fcf67e2ac605`
- Working tree at record time: clean (`git status --short` empty)
- `nova-doctor`: status `ready` — duckdb 1.5.6, pyarrow 26.0.0, numpy 2.5.4,
  pandas 3.0.6, talib 0.8.2, yaml 6.0.3, pytz 2026.6
- `pytest -q`: **88 passed, 0 failed** (7.38s)

`FROZEN_CORE.sha256` was generated from this state (18 files: 16 under
`src/nova/`, plus `pyproject.toml` and `requirements.lock`). Any later change
to those files fails `scripts/check_frozen_core.py` and invalidates every
historical run.
