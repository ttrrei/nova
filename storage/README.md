# storage/

Storage policy and baseline records for the repository's heavy data:

- `INVENTORY.md` — Stage-1 read-only size/count inventory of the data-bearing
  directories (historical record; the folder-level ignore policy it described
  was superseded by the folder-visible policy — see its note).
- `BASELINE.md` — Stage-0 baseline: HEAD commit, clean tree, `nova-doctor`
  status, 88 passing tests, and the `FROZEN_CORE.sha256` provenance.

Future object-storage policy (Stage 2, `docs/STORAGE_POLICY.md`) will be
recorded here as it lands.
