# Proposal: AGENTS.md — frozen core (for human review)

Status: **proposal only** — `AGENTS.md` has not been changed in this stage.

Suggested addition to `AGENTS.md` (English version; the Chinese version is in
`AGENTS_frozen_core.zh.md`):

---

## Frozen core

The Nova core is **frozen**. A change to causality, the engine, execution or
cost rules, metrics, or the environment (dependencies) makes every historical
result invalid and forces a full re-run of all strategies. An update to an
existing feature invalidates the runs that depend on it.

Never edit, refactor, reformat, rename, or re-import anything under:

- `src/nova/` (all Python files)
- `pyproject.toml`
- `requirements.lock`
- the value of `FEATURE_VERSION`

Integrity is enforced by `FROZEN_CORE.sha256` (repo root) and
`scripts/check_frozen_core.py` (run by `tests/test_frozen_core.py` in every
test session). Regenerating the baseline with `--write` is a **human-only**
action and admits that all historical results are invalidated.

Adding a **new** feature is insert-only and does not invalidate history, but
it is governed by a separate protocol (`docs/proposals/FEATURE_ADDITION_PROTOCOL.md`),
requires the `FEATURE_VERSION` bump rule to be re-applied by a human, and is
not part of routine housekeeping.

Updating, renaming, or deleting an existing feature — or any change to the
engine, execution, costs, metrics, or dependencies — is never allowed without
an explicit human decision.
