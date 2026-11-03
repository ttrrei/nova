# scripts/

Operational helpers around the `nova` CLI (not installed package code):

| Script | Purpose |
|---|---|
| `check_frozen_core.py` | Verify the frozen core files still match `FROZEN_CORE.sha256`; any change invalidates historical runs |
| `research_round.py` | Execute and record one round of the finite research campaign |
| `review_directions.py` | Run the twelve fixed hourly direction hypotheses into `runs/directions/` and save audited results under `docs/verification/directions/` |
| `review_trades.py` | Inspect actual trades from a published run |
| `summarize_research_campaign.py` | Aggregate campaign ledgers into a summary |
| `verify_rebuild.py` | Replay the rebuild pipeline to confirm reproducibility |

Run with `.venv/bin/python scripts/<name>.py`.
