# data/market/

Cleaned, sorted market candles aggregated into UTC buckets, one snapshot per
timeframe. Each subfolder `<minutes>m/` holds snapshot directories named by
a short ID (e.g. `60m/ecaa0a6c6cd7eb46/`), each containing:

- one Parquet per instrument (e.g. `EUR_USD.parquet`) — excluded by type;
- `manifest.json` — tracked; records source identities (all SHA256s), source
  contract, data version and validation counters (duplicates, conflicting
  keys, removed rows, partial buckets).

Built by `nova aggregate --minutes <5|60>` from the cleaned one-minute
base. Only complete buckets are kept (no synthetic fills); calendar gaps
remain gaps; Bid/Ask quote columns exist only when every source minute
carried quotes.
