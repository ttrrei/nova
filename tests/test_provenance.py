import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np

from nova.indicators import supertrend


ROOT = Path(__file__).resolve().parents[1]


def test_source_bytes_and_modified_notice_are_recorded():
    report = json.loads((ROOT / "docs/provenance/reuse.json").read_text())
    source = report["adapted_modules"][0]
    data = (ROOT / source["reference"]).read_bytes()
    assert hashlib.sha256(data).hexdigest() == source["source_sha256"]
    assert (
        hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        == source["git_blob_sha"]
    )
    assert (
        hashlib.sha256((ROOT / source["destination"]).read_bytes()).hexdigest()
        == source["adapted_sha256"]
    )
    assert report["license"] == "Apache-2.0"
    assert (
        hashlib.sha256((ROOT / "LICENSE").read_bytes()).hexdigest()
        == report["license_sha256"]
    )
    assert source["source"] in (ROOT / "NOTICE").read_text()
    assert (ROOT / source["patch"]).is_file()
    for item in report["research_reference_files"]:
        data = (ROOT / item["reference"]).read_bytes()
        assert hashlib.sha256(data).hexdigest() == item["sha256"]
        assert (
            hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            == item["git_blob_sha"]
        )


def test_adapted_supertrend_preserves_pinned_source_numerics():
    path = ROOT / "docs/provenance/reference/supertrend.py"
    spec = importlib.util.spec_from_file_location("pinned_supertrend_reference", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for flat in (False, True):
        close = np.full(200, 100.0) if flat else 100 + np.sin(np.arange(200) / 8) * 3
        high = close + 0.1
        low = close - 0.1
        atr = np.full(200, 0.8)
        atr[:14] = np.nan
        for multiplier in (2.0, 3.0):
            actual = supertrend(high, low, close, atr, multiplier)
            expected = module.supertrend(high, low, close, atr, multiplier)
            for a, b in zip(actual, expected):
                np.testing.assert_array_equal(a, b)
