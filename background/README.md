# background/

Read-only reference material for Nova's design: the final user decisions and
the Moneta Next v0.2 workstream that Nova rebuilt from. **Never modify this
tree** (working contract); runtime code must not import from it.

| Path | Contents |
|---|---|
| `luna6.1design`, `sol6.1design` | The final user design decisions (plain text) that are the requirements baseline for Nova. `sol6.1design` takes precedence over earlier proposals. |
| `moneta-next/` | The Moneta Next v0.2 workstream: `START_HERE.md` (working rules), `README.md`, `AGENTS.md`, `examples/` (legacy strategy YAMLs), `migration/` (data contract, provenance, reference library/pipeline/docs), `src/moneta_next/` (reference implementation incl. vendored OANDA client), `tests/`, `verification/`. |
| `moneta-next-*.zip` | Release archives of the Moneta Next starter (excluded by `*.zip`; folder stays visible). |

Treat everything here as frozen historical input: Nova reuses its data and
research decisions, not its OOS machinery or code.
