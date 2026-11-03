# runs/

Immutable experiment outputs. Each completed run is a self-contained,
hash-published directory named by its run ID; a failed run leaves a clearly
marked temporary directory that is never registered as complete.

**Repository policy:** per-run `trades.csv` / `signals.csv` are excluded by
the root `.gitignore` file-type rules; the JSON/YAML/MD artifacts (manifest,
summary, compiled SQL, report, strategy copy) remain tracked.

## Layout

| Path | Contents |
|---|---|
| `<run_id>/` | One experiment: `report.md`, `summary.json`, `manifest.json`, `strategy.yaml`, `compiled.sql`, `feature_catalog.json`, `trades.csv`, `signals.csv`, plus `README.md`. |
| `batch_latest.json` | Pointer to the latest reviewed batch of example strategies. |
| `directions/` | The twelve fixed hourly direction hypotheses (one YAML per research family under `strategies/directions/`), run by `scripts/review_directions.py`. Audited results live in `docs/verification/directions/`. |
| `research_campaign/` | The finite twelve-direction research campaign: `campaign.json`, `AGENT_PROTOCOL.md`, `READY.json`, per-direction folders (rounds/experiments/ledgers) and `stores/` (isolated per-direction feature catalogs over shared immutable Parquet). See `AGENT_PROTOCOL.md` inside for the campaign rules. |

## Per-run artifact contract

| Artifact | Contents |
|---|---|
| `report.md` | Human-readable per-instrument screening results |
| `trades.csv` | Entry/exit fills, timestamps, stop/target, reasons, holding bars, returns, costs |
| `signals.csv` | Rows where any entry/exit condition was true (including while holding) |
| `summary.json` | Every UTC month (zero-entry months included), yearly return sums, per-instrument scores |
| `manifest.json` | Effective strategy, dependencies, data/feature/code identities, assumptions, artifact hashes |
| `strategy.yaml` | The exact submitted YAML |
| `compiled.sql` | Generated past-only SQL |
| `feature_catalog.json` | The registered feature vocabulary the compiler used |

Repeating identical inputs verifies and reuses the existing run (replay
identity). Runs are audited with `nova audit runs/<run_id>`; do not edit
published artifacts.
