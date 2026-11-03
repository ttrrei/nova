# background/moneta-next/

Frozen Moneta Next v0.2 reference workstream. Entry point: `START_HERE.md`
(final working rules); `README.md` describes the project.

| Folder | Contents |
|---|---|
| `examples/` | Legacy strategy YAML hypotheses (trend hold, mean reversion, Supertrend, EMA pullback, PSAR confirmation) used as reviewed inputs. |
| `migration/` | Data contract (`DATA_CONTRACT.md`), migration guide/summary, provenance and research knowledge JSONs, and `reference/` (config, docs, library, pipeline, research, strategy, tests from the legacy codebase). |
| `src/moneta_next/` | Reference implementation: `legacy_engine.py`, vendored OANDA client, vendor modules. Never imported by Nova's runtime. |
| `tests/` | Reference test suite for the v0.2 code. |
| `verification/` | Verification artifacts of the v0.2 release. |

Read-only: Nova's contract (AGENTS.md) forbids modifying `background/`.
