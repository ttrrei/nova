# data/import-check/

A throwaway independent data store used for the Parquet import acceptance
check (invoked with `--store data/import-check` so the primary store stays
untouched). Mirrors the standard layout inside:

- `raw_parquet/` — the imported native Parquet input(s)
- `market/60m/` — market snapshot rebuilt from that input
- `features/60m/` — feature snapshot rebuilt on top of it
- `nova.duckdb` — the store-local catalog (excluded by type)
- `tmp/` — ephemeral scratch

Contents are excluded by the root file-type rules except manifests and this
README; the whole point of this folder is to prove the import pipeline works
on native Parquet without touching the primary data root.
