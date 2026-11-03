# Feature Addition Protocol (for human review)

Status: **proposal** — written for human review; not yet approved.
Companion translation: `FEATURE_ADDITION_PROTOCOL.zh.md`
(governing version is the English one if the two ever differ).

## Why

Nova's core is frozen because a change to causality, the engine, execution
or cost rules, metrics, or dependencies invalidates every historical result.
A **new** feature is the one category of feature change that *can* be
insert-only — it changes no existing column — and therefore does not
invalidate history, provided the proof requirements below are met.

## Allowed (insert)

A **new feature** may be added when all of the following hold:

1. It has a unique new name and occupies a new column; no existing
   feature column is touched.
2. It is registered in the feature catalog.
3. `FEATURE_VERSION` is bumped, as `AGENTS.md` requires.
4. Causality tests cover the new column (per-bar, past-only semantics).
5. All proof requirements below are satisfied **before** the change is
   accepted.

## Not allowed without an explicit human decision

- **Update:** any change to an existing feature's formula, parameters,
  warm-up, dtype, NaN rule, or row filter.
- **Rename:** renaming an existing feature.
- **Delete:** removing an existing feature or its column.
- Any change to the engine, execution, costs, or metrics.
- Any dependency change (including `pyproject.toml` or `requirements.lock`).

## Proof required before an insert is accepted

1. A fingerprint of **every** existing feature column, per instrument and
   timeframe, is identical before and after the change.
2. The row timestamps are identical before and after.
3. `requirements.lock` is unchanged.
4. Replaying the historical runs reproduces identical trade lists.
5. The engine does not select columns by position and does not use
   `SELECT *` anywhere on the feature path.

The fingerprint and replay tooling is built in a **later feature-addition
task**, not in this housekeeping plan.

## If an update to an existing feature is unavoidable

Only the runs whose manifest lists that feature as a dependency are
invalidated. Those runs must be **listed from the manifests before the
human decides**, so the human sees exactly which historical results are at
risk.
