#!/usr/bin/env python3
"""Guard the frozen Nova core.

Nova's core is frozen: a change to causality, the engine, execution or cost
rules, metrics, or the environment (dependencies) invalidates every historical
result and forces a full re-run of all strategies. This script compares the
sha256 of every frozen file against FROZEN_CORE.sha256 at the repo root and
exits non-zero, listing differing files, if anything changed.

Usage:
    python scripts/check_frozen_core.py              # compare; exit 0 if identical
    python scripts/check_frozen_core.py --write      # regenerate the baseline
                                                       (HUMANS ONLY)
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BASELINE_FILE = REPO_ROOT / "FROZEN_CORE.sha256"


def frozen_files() -> list[Path]:
    files = sorted((REPO_ROOT / "src" / "nova").rglob("*.py"))
    files.append(REPO_ROOT / "pyproject.toml")
    files.append(REPO_ROOT / "requirements.lock")
    return files


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_baseline() -> None:
    if sys.stdin.isatty():
        print(
            "WARNING: regenerating FROZEN_CORE.sha256. This is for HUMAN use "
            "only; a changed frozen core invalidates ALL historical results.",
            file=sys.stderr,
        )
    lines = [f"{sha256(path)}  {path.relative_to(REPO_ROOT).as_posix()}"
             for path in frozen_files()]
    BASELINE_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {BASELINE_FILE.name} with {len(lines)} entries")


def check() -> int:
    if not BASELINE_FILE.exists():
        print(f"error: {BASELINE_FILE.name} not found; run with --write first",
              file=sys.stderr)
        return 2
    baseline = {}
    for line in BASELINE_FILE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, _, relpath = line.partition("  ")
        baseline[relpath] = digest

    problems: list[str] = []
    current = {
        path.relative_to(REPO_ROOT).as_posix(): sha256(path)
        for path in frozen_files()
    }

    for relpath in sorted(set(baseline) - set(current)):
        problems.append(f"missing (in baseline, not on disk): {relpath}")
    for relpath in sorted(set(current) - set(baseline)):
        problems.append(f"new (on disk, not in baseline): {relpath}")
    for relpath in sorted(set(baseline) & set(current)):
        if baseline[relpath] != current[relpath]:
            problems.append(f"MODIFIED: {relpath}")

    if problems:
        print("frozen core check FAILED:", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        print(
            "\nA change to the frozen core invalidates every historical "
            "result. Restore the files or escalate to a human.",
            file=sys.stderr,
        )
        return 1
    print(f"frozen core check passed: {len(current)} files identical")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="regenerate FROZEN_CORE.sha256 (humans only)",
    )
    args = parser.parse_args()
    if args.write:
        write_baseline()
        return 0
    return check()


if __name__ == "__main__":
    sys.exit(main())
