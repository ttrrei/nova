import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path

import duckdb
import numpy as np
import pyarrow.parquet as pq
import pytest

from nova.data import aggregate, ingest
from nova.features import build
from nova.runner import run
from nova.audit import audit_run

START = datetime(2024, 1, 1, tzinfo=timezone.utc)


def write_source(
    path, count=24 * 60 * 4, quoted=True, kind="oanda", instruments=("TEST",)
):
    rows = []
    for instrument in instruments:
        for i in range(count):
            o = 100 + np.sin(i / 720)
            c = 100 + np.sin((i + 1) / 720)
            row = {
                "instrument": instrument,
                "is_complete": "true",
                "time": (START + timedelta(minutes=i)).isoformat(),
                "volume": 10,
                "mid_o": o,
                "mid_h": max(o, c) + 0.05,
                "mid_l": min(o, c) - 0.05,
                "mid_c": c,
            }
            if quoted:
                for side, offset in [("bid", -0.01), ("ask", 0.01)]:
                    for point in ("o", "h", "l", "c"):
                        row[f"{side}_{point}"] = row[f"mid_{point}"] + offset
            if kind == "canonical":
                row["bar_open_time"] = row.pop("time")
                row["bar_close_time"] = (START + timedelta(minutes=i + 1)).isoformat()
                for full, short in zip(
                    ("open", "high", "low", "close"), ("o", "h", "l", "c")
                ):
                    row[full] = row.pop(f"mid_{short}")
                    if quoted:
                        for side in ("bid", "ask"):
                            row[f"{side}_{full}"] = row.pop(f"{side}_{short}")
            rows.append(row)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def rewrite(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def test_end_to_end_both_examples_reuse_and_audit(tmp_path):
    source = tmp_path / "source.csv"
    write_source(source)
    root = tmp_path / "store"
    first = ingest(source, root)
    second = ingest(source, root)
    assert first["snapshot_id"] == second["snapshot_id"]
    market = aggregate(root, 60)
    bars = pq.read_table(market["files"][0]["path"]).to_pandas()
    assert len(bars) == 96
    assert (bars.bid_open < bars.ask_open).all()
    manifest = build(root, 60)
    assert build(root, 60)["snapshot_id"] == manifest["snapshot_id"]
    repo = Path(__file__).resolve().parents[1]
    for name in ("mean_reversion.yaml", "trend_hold.yaml"):
        dest, summary = run(repo / "strategies" / name, root, tmp_path / "runs")
        assert summary["per_instrument"]["TEST"]["trade_count"] > 0
        assert audit_run(dest)["status"] == "passed"
        assert run(repo / "strategies" / name, root, tmp_path / "runs")[0] == dest
    with duckdb.connect(str(root / "nova.duckdb"), read_only=True) as con:
        assert con.execute("SELECT count(*) FROM experiment_runs").fetchone()[0] == 2
        assert con.execute("SELECT count(*) FROM features_60m").fetchone()[0] == 96


def test_duplicate_selection_incomplete_and_conflict_provenance(tmp_path):
    source = tmp_path / "source.csv"
    rows = write_source(source, count=3)
    duplicate = dict(rows[0])
    duplicate["volume"] = 11
    rows.extend([dict(rows[0]), duplicate, dict(rows[1], is_complete="false")])
    rewrite(source, rows)
    result = ingest(source, tmp_path / "store")
    assert result["files"][0]["rows"] == 3
    assert result["quality"]["duplicate_complete_rows_removed"] == 2
    assert result["quality"]["conflicting_duplicate_keys"] == 1
    assert result["quality"]["incomplete_rows_dropped"] == 1


@pytest.mark.parametrize(
    "change",
    [
        {"mid_l": 200},
        {"mid_o": float("nan")},
        {"volume": -1},
        {"time": "2024-01-01T00:00:00"},
        {"is_complete": "maybe"},
        {"instrument": "../escape"},
        {"ask_o": 1},
    ],
)
def test_invalid_raw_data_rejected(tmp_path, change):
    path = tmp_path / "source.csv"
    rows = write_source(path, count=3)
    rows[0].update(change)
    rewrite(path, rows)
    with pytest.raises((ValueError, duckdb.Error)):
        ingest(path, tmp_path / "store")


def test_partial_buckets_dropped_without_imputation(tmp_path):
    path = tmp_path / "source.csv"
    rows = write_source(path, count=125)
    del rows[10]
    rewrite(path, rows)
    root = tmp_path / "store"
    ingest(path, root)
    market = aggregate(root, 60)
    assert market["quality"]["partial_buckets_dropped"] == 2
    frame = pq.read_table(market["files"][0]["path"]).to_pandas()
    assert len(frame) == 1
    assert frame.bar_open_time.iloc[0].hour == 1


def test_canonical_mid_only_input(tmp_path):
    path = tmp_path / "source.csv"
    write_source(path, count=120, quoted=False, kind="canonical")
    root = tmp_path / "store"
    result = ingest(path, root, kind="canonical")
    assert result["files"][0]["quoted_bars"] == 0
    assert aggregate(root, 60)["files"][0]["quoted_bars"] == 0


def test_requested_bounds_are_half_open_and_history_keeps_warmup(tmp_path):
    source = tmp_path / "source.csv"
    write_source(source)
    root = tmp_path / "store"
    ingest(source, root)
    aggregate(root, 60)
    build(root, 60)
    repo = Path(__file__).resolve().parents[1]
    dest, summary = run(
        repo / "strategies/trend_hold.yaml",
        root,
        tmp_path / "runs",
        since="2024-01-03",
        until="2024-01-04",
    )
    stats = summary["per_instrument"]["TEST"]
    assert sum(r["observed_bars"] for r in stats["monthly_entries"]) == 24
    assert stats["window"] == {
        "start": "2024-01-03T00:00:00+00:00",
        "end_exclusive": "2024-01-04T00:00:00+00:00",
    }
    assert audit_run(dest)["status"] == "passed"


def test_source_snapshot_tampering_detected(tmp_path):
    source = tmp_path / "source.csv"
    write_source(source, count=120)
    root = tmp_path / "store"
    manifest = ingest(source, root)
    Path(manifest["files"][0]["path"]).write_bytes(b"broken")
    with pytest.raises(ValueError, match="changed"):
        aggregate(root, 60)


def test_universal_run_isolates_instruments_and_zero_trade_results(tmp_path):
    import yaml

    source = tmp_path / "source.csv"
    write_source(source, count=60 * 96, instruments=("AAA", "BBB"))
    root = tmp_path / "store"
    ingest(source, root)
    aggregate(root, 60)
    build(root, 60)
    repo = Path(__file__).resolve().parents[1]
    strategy = yaml.safe_load((repo / "strategies/trend_hold.yaml").read_text())
    strategy["entry"] = {"long": {"feature": "close", "op": "lt", "value": 0}}
    strategy_path = tmp_path / "empty.yaml"
    strategy_path.write_text(yaml.safe_dump(strategy))
    dest, summary = run(strategy_path, root, tmp_path / "runs")
    assert summary["total_trades"] == 0
    assert set(summary["per_instrument"]) == {"AAA", "BBB"}
    assert all(
        row["net_trade_return_sum"] == 0 for row in summary["per_instrument"].values()
    )
    assert audit_run(dest)["trades_checked"] == 0
    assert (
        (dest / "trades.csv").read_text().startswith("instrument,direction,signal_time")
    )


def test_interrupted_import_resumes_validated_staging(tmp_path, monkeypatch):
    import nova.data as data

    source = tmp_path / "source.csv"
    write_source(source, count=120)
    root = tmp_path / "store"
    original = data._file_record

    def interrupted(*args):
        raise OSError("simulated export interruption")

    monkeypatch.setattr(data, "_file_record", interrupted)
    with pytest.raises(OSError, match="interruption"):
        ingest(source, root)
    monkeypatch.setattr(data, "_file_record", original)
    manifest = ingest(source, root)
    assert manifest["files"][0]["rows"] == 120
    assert not list((root / "tmp").glob("ingest-*.duckdb"))


def test_new_source_requires_rebuilding_aggregates_and_features(tmp_path):
    source = tmp_path / "source.csv"
    write_source(source, count=120)
    root = tmp_path / "store"
    ingest(source, root)
    aggregate(root, 60)
    build(root, 60)
    new_source = tmp_path / "extended.csv"
    write_source(new_source, count=180)
    ingest(new_source, root)
    with pytest.raises(ValueError, match="source changed"):
        build(root, 60)
    aggregate(root, 60)
    repo = Path(__file__).resolve().parents[1]
    with pytest.raises(ValueError, match="Feature version changed"):
        run(repo / "strategies/trend_hold.yaml", root, tmp_path / "runs")
    assert build(root, 60)["files"][0]["rows"] == 3


def test_asset_with_no_complete_buckets_is_reported_without_crashing(tmp_path):
    source = tmp_path / "source.csv"
    rows = write_source(source, count=120, instruments=("FULL", "SPARSE"))
    rows = [r for i, r in enumerate(rows) if r["instrument"] == "FULL" or i % 2 == 0]
    rewrite(source, rows)
    root = tmp_path / "store"
    ingest(source, root)
    manifest = aggregate(root, 60)
    assert [r["instrument"] for r in manifest["files"]] == ["FULL"]
    assert manifest["quality"]["partial_buckets_dropped"] == 2
