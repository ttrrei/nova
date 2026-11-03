"""Test that the frozen Nova core is unchanged.

A change to the frozen core (src/nova, pyproject.toml, requirements.lock)
invalidates every historical result, so this runs the same check the script
performs and fails the test suite if the hash baseline is violated.
"""

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "check_frozen_core.py"


@pytest.fixture(scope="module")
def checker():
    spec = importlib.util.spec_from_file_location("check_frozen_core", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_frozen_core_unchanged(checker):
    assert checker.check() == 0
