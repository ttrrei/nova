# runs/directions/

Immutable experiment outputs of the twelve fixed hourly direction
hypotheses (one per research family; strategies in `strategies/directions/`).

Each child directory is one published run (`<run_id>/`), containing the
standard artifact set — `report.md`, `summary.json`, `manifest.json`,
`strategy.yaml`, `compiled.sql`, `feature_catalog.json`, `trades.csv`,
`signals.csv` — plus `README.md`. Per-run trade CSVs are excluded by the
root file-type rules; the JSON/YAML/MD artifacts stay tracked.

Audited copies live in `docs/verification/directions/`. Runs were produced
by `scripts/review_directions.py` and are replayable via
`scripts/verify_rebuild.py`.
