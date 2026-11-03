# Ignored Paths Inventory (Stage 1)

Recorded: 2026-11-03 (local time), commit `2e0ec22` (Stage 0).
Read-only inventory: size and file count only. No file contents, and no
file names from `background/`.

> **Policy supersession (2026-11-03, later same day):** the user directive
> "every folder stays visible in the code repository" supersedes this
> folder-level ignore policy. The directory entries listed below are no
> longer wholesale-ignored; only their heavy file contents remain excluded
> by the root `.gitignore` file-type rules. This file remains as a
> historical size/count record, not as the active policy.

## Ignored directories

| Path | Size | File count |
|---|---|---|
| `data/` | 16 GB | 519 |
| `runs/` | 3.6 GB | 2029 |
| `legacy/` | 31 GB | 29656 |
| `background/` | 2.0 MB | 103 |

## Other ignored items

- `.venv/`, `.pytest_cache/`, `.ruff_cache/`, `build/`, `dist/`,
  `src/nova_research.egg-info/`, `*.py[cod]` / `__pycache__/` — regenerable
  local artifacts (see `.gitignore`, Stage 4 for the full grouping).
- `guidance_raw/` — does not exist yet on disk; it is created by the
  Stage 10 layout (`guidance/` inbox + `guidance_raw/` raw material).

## Notes

- No tracked file is currently ignored by mistake
  (`git ls-files --others --ignored --exclude-standard` is empty).
- Totals: ~52.6 GB across the four data-bearing directories. These are the
  candidates for the OCI Object Storage policy defined in Stage 2
  (`docs/STORAGE_POLICY.md`).
