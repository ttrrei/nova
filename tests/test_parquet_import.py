from datetime import timedelta

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from nova.data import ingest, aggregate
from nova.features import build
from nova.doctor import check_environment
from test_data import START, write_source


def test_raw_parquet_preserves_quotes_and_matches_csv_values(tmp_path):
    csv = tmp_path / "raw.csv"
    write_source(csv, count=120)
    frame = pd.read_csv(csv)
    frame["time"] = pd.to_datetime(frame.time, utc=True)
    parquet = tmp_path / "raw.parquet"
    frame.to_parquet(parquet, index=False)
    csv_manifest = ingest(csv, tmp_path / "csv-store")
    parquet_manifest = ingest(parquet, tmp_path / "parquet-store")
    csv_values = pq.read_table(csv_manifest["files"][0]["path"]).to_pandas()
    parquet_values = pq.read_table(parquet_manifest["files"][0]["path"]).to_pandas()
    pd.testing.assert_frame_equal(csv_values, parquet_values)
    assert parquet_manifest["input_format"] == "parquet"
    assert parquet_manifest["files"][0]["quoted_bars"] == 120


def test_canonical_parquet_end_to_end(tmp_path):
    csv = tmp_path / "canonical.csv"
    write_source(csv, count=120, kind="canonical")
    frame = pd.read_csv(csv)
    for col in ("bar_open_time", "bar_close_time"):
        frame[col] = pd.to_datetime(frame[col], utc=True)
    path = tmp_path / "canonical.parquet"
    frame.to_parquet(path, index=False)
    root = tmp_path / "store"
    ingest(path, root, kind="canonical")
    assert aggregate(root, 60)["files"][0]["rows"] == 2
    assert build(root, 60)["files"][0]["rows"] == 2


def test_gold_market_import_drops_partial_buckets_and_all_cached_indicators(tmp_path):
    frame = pd.DataFrame(
        {
            "instrument": ["TEST"] * 4,
            "time": pd.date_range(START, periods=4, freq="h"),
            "open": [100.0] * 4,
            "high": [101.0] * 4,
            "low": [99.0] * 4,
            "close": [100.0] * 4,
            "volume": [100.0] * 4,
            "n_bars": [60, 59, 60, 60],
            "aroon_up_24": [999.0] * 4,
            "bb_upper_24": [-1.0] * 4,
            "vwap": [0.0] * 4,
            "h1_rsi_24": [999.0] * 4,
        }
    )
    path = tmp_path / "gold.parquet"
    frame.to_parquet(path, index=False)
    manifest = ingest(path, tmp_path / "store", kind="ohlcv", minutes=60)
    assert manifest["quality"]["incomplete_rows_dropped"] == 1
    assert manifest["files"][0]["rows"] == 3
    assert set(manifest["ignored_columns"]) == {
        "aroon_up_24",
        "bb_upper_24",
        "vwap",
        "h1_rsi_24",
    }
    table = pq.read_table(manifest["files"][0]["path"])
    assert "vwap" not in table.column_names
    assert table.column("source_bars").to_pylist() == [60] * 3
    assert manifest["data_producer_revision"].startswith("unknown")


def test_ohlcv_short_quotes_preserved(tmp_path):
    frame = pd.DataFrame(
        {
            "instrument": ["TEST"],
            "time": [START],
            "open": [100.0],
            "high": [101.0],
            "low": [99.0],
            "close": [100.0],
            "volume": [10.0],
            "n_bars": [60],
        }
    )
    for side, offset in [("bid", -0.1), ("ask", 0.1)]:
        for full, short in zip(("open", "high", "low", "close"), ("o", "h", "l", "c")):
            frame[f"{side}_{short}"] = frame[full] + offset
    path = tmp_path / "quotes.parquet"
    frame.to_parquet(path, index=False)
    manifest = ingest(path, tmp_path / "store", kind="ohlcv", minutes=60)
    row = pq.read_table(manifest["files"][0]["path"]).to_pylist()[0]
    assert row["bid_open"] == 99.9 and row["ask_close"] == 100.1


@pytest.mark.parametrize(
    "case", ["naive", "wrong_duration", "misaligned", "invalid_count", "partial_quote"]
)
def test_invalid_parquet_data_rejected(tmp_path, case):
    row = {
        "instrument": "TEST",
        "time": START,
        "open": 100.0,
        "high": 101.0,
        "low": 99.0,
        "close": 100.0,
        "volume": 10.0,
        "n_bars": 60,
    }
    if case == "naive":
        row["time"] = START.replace(tzinfo=None)
    if case == "misaligned":
        row["time"] = START + timedelta(minutes=1)
    if case == "invalid_count":
        row["n_bars"] = 60.5
    if case == "partial_quote":
        row["bid_open"] = 99.9
    kind = "ohlcv"
    if case == "wrong_duration":
        row["bar_open_time"] = row.pop("time")
        row["bar_close_time"] = START + timedelta(minutes=59)
        row["is_complete"] = True
        kind = "canonical"
    path = tmp_path / "invalid.parquet"
    pq.write_table(pa.Table.from_pylist([row]), path)
    with pytest.raises(ValueError):
        ingest(path, tmp_path / "store", kind=kind, minutes=60)


def test_mixed_input_formats_are_rejected(tmp_path):
    folder = tmp_path / "mixed"
    folder.mkdir()
    write_source(folder / "input.csv", count=1)
    pd.read_csv(folder / "input.csv").to_parquet(folder / "input.parquet", index=False)
    with pytest.raises(ValueError, match="homogeneous"):
        ingest(folder, tmp_path / "store")


def test_doctor_reports_actual_dependency_import_errors(monkeypatch):
    import nova.doctor as doctor

    actual = doctor.importlib.import_module

    def missing(name):
        if name == "talib":
            raise ImportError("native library unavailable")
        return actual(name)

    monkeypatch.setattr(doctor.importlib, "import_module", missing)
    result = check_environment()
    assert result["status"] == "unavailable"
    assert result["packages"]["talib"]["error"] == "native library unavailable"
