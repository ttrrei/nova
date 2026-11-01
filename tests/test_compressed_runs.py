import csv
import gzip
import json
from pathlib import Path

import pytest

from nova.audit import audit_run
from nova.common import csv_artifact, file_hash, open_text
from nova.compiler import compile_strategy
from nova.config import load_strategy
from nova.data import aggregate, ingest
from nova.features import build, instrument_view
from nova.runner import run, write_csv
from nova.store import connect
from nova.trades import simulate
from test_data import write_source


@pytest.mark.parametrize("quoted", [True, False])
def test_compressed_execution_matches_plain_and_full_feature_projection(
    tmp_path, quoted
):
    source = tmp_path / "source.csv"
    write_source(source, quoted=quoted)
    root = tmp_path / "store"
    ingest(source, root)
    aggregate(root, 60)
    features = build(root, 60)
    strategy = Path(__file__).resolve().parents[1] / "strategies/mean_reversion.yaml"
    plain, plain_summary = run(strategy, root, tmp_path / "runs")
    compressed, compressed_summary = run(
        strategy, root, tmp_path / "runs", compress_artifacts=True
    )
    assert plain != compressed
    assert plain_summary == compressed_summary
    assert plain_summary["total_trades"] > 0
    assert audit_run(plain) == audit_run(compressed)
    assert audit_run(compressed)["status"] == "passed"
    manifest = json.loads((compressed / "manifest.json").read_text())
    assert manifest["inputs"]["csv_compression"] == "gzip-v1"
    assert (
        "csv_compression"
        not in json.loads((plain / "manifest.json").read_text())["inputs"]
    )
    for name in ("signals.csv", "trades.csv"):
        assert not (compressed / name).exists()
        assert (
            gzip.decompress((compressed / (name + ".gz")).read_bytes())
            == (plain / name).read_bytes()
        )

    # Independent full-feature projection exercises the previous cursor contract;
    # narrowing the rows sent to the state machine must preserve every trade.
    spec = load_strategy(strategy)
    with connect(root) as con:
        instrument_view(con, features, "TEST")
        cursor = con.execute(
            f"""SELECT b.*,s.entry_long,s.entry_short,s.exit_long,s.exit_short
                FROM features b JOIN ({compile_strategy(spec)}) s
                USING(instrument,bar_open_time,bar_close_time)
                ORDER BY b.bar_open_time"""
        )
        names = [column[0] for column in cursor.description]
        rows = [dict(zip(names, row)) for row in cursor.fetchall()]
    expected = simulate(rows, rows, spec)
    expected_csv = tmp_path / "expected.csv"
    with (plain / "trades.csv").open(newline="") as stream:
        fields = csv.DictReader(stream).fieldnames
    write_csv(expected_csv, expected, fields)
    assert expected_csv.read_bytes() == (plain / "trades.csv").read_bytes()

    assert (
        run(strategy, root, tmp_path / "runs", compress_artifacts=True)[0] == compressed
    )
    duplicate, duplicate_summary = run(
        strategy, root, tmp_path / "second_output", compress_artifacts=True
    )
    assert duplicate_summary == compressed_summary
    for name, digest in manifest["artifact_hashes"].items():
        assert file_hash(duplicate / name) == digest

    # Hash verification detects damage on both independent audit and cached reuse.
    with (compressed / "trades.csv.gz").open("ab") as stream:
        stream.write(b"changed")
    with pytest.raises(ValueError, match="Artifact hash mismatch"):
        audit_run(compressed)
    with pytest.raises(ValueError, match="Run artifact changed"):
        run(strategy, root, tmp_path / "runs", compress_artifacts=True)


def test_compressed_text_has_no_time_or_filename_and_resolves_unambiguously(tmp_path):
    for name in ("one.csv.gz", "two.csv.gz"):
        with open_text(tmp_path / name, "w", newline="") as stream:
            stream.write("a,b\r\n1,2\r\n")
    data = (tmp_path / "one.csv.gz").read_bytes()
    assert data == (tmp_path / "two.csv.gz").read_bytes()
    assert data[3] & 8 == 0  # No original filename in the gzip header.
    assert data[4:8] == b"\x00\x00\x00\x00"
    assert csv_artifact(tmp_path, "one.csv") == tmp_path / "one.csv.gz"
    with open_text(csv_artifact(tmp_path, "one.csv"), newline="") as stream:
        assert list(csv.reader(stream)) == [["a", "b"], ["1", "2"]]
    (tmp_path / "one.csv").write_text("ambiguous")
    with pytest.raises(ValueError, match="Expected one"):
        csv_artifact(tmp_path, "one.csv")
