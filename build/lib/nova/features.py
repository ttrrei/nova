"""Causal feature snapshots, computed once per instrument into core/domain tables."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import talib

from .catalog import FEATURES, FEATURE_PARAMS, FEATURE_VERSION
from .common import file_hash, identity, sql_string, write_json
from .data import _verify_files
from .indicators import supertrend
from .store import connect, dataset, parquet_view, register


def _divide(a, b):
    return np.divide(
        a, b, out=np.full_like(a, np.nan, dtype=float), where=np.isfinite(b) & (b != 0)
    )


def _cross(a, b):
    valid = np.isfinite(a) & np.isfinite(b)
    previous = np.r_[False, valid[:-1]]
    past_a = np.r_[np.nan, a[:-1]]
    past_b = np.r_[np.nan, b[:-1]]
    return (
        np.where(valid & previous, (a > b) & (past_a <= past_b), np.nan),
        np.where(valid & previous, (a < b) & (past_a >= past_b), np.nan),
    )


def compute(frame):
    """One bar-close output per input; recursive indicators retain their prefix state.

    No fixed warm-up rows are discarded. Each feature is NULL until its own
    inputs are available, and snapshot history always starts at the source head.
    """
    c, h, low = [
        frame[name].to_numpy(dtype=np.float64) for name in ("close", "high", "low")
    ]
    if not len(c):
        raise ValueError("Features require nonempty bars")
    prev = np.r_[c[0], c[:-1]]
    tr = np.maximum.reduce([h - low, np.abs(h - prev), np.abs(low - prev)])
    result = {
        "atr_sma_14": pd.Series(tr).rolling(14, min_periods=14).mean().to_numpy(),
        "atr_14": talib.ATR(h, low, c, timeperiod=14),
        "rsi_14": talib.RSI(c, timeperiod=14),
    }
    for n in FEATURE_PARAMS["sma"]:
        result[f"sma_{n}"] = talib.SMA(c, timeperiod=n)
    for n in FEATURE_PARAMS["ema"]:
        result[f"ema_{n}"] = talib.EMA(c, timeperiod=n)
    for name in ("sma", "ema"):
        a, b = result[f"{name}_6"], result[f"{name}_24"]
        result[f"{name}_alignment_6_24"] = np.where(
            np.isfinite(a) & np.isfinite(b), np.sign(a - b), np.nan
        )
        result[f"{name}_cross_up_6_24"], result[f"{name}_cross_down_6_24"] = _cross(
            a, b
        )
    result["close_sma24_distance_atr"] = _divide(
        c - result["sma_24"], result["atr_sma_14"]
    )
    result["close_ema60_distance_atr"] = _divide(c - result["ema_60"], result["atr_14"])
    result["psar"] = talib.SAR(h, low, **FEATURE_PARAMS["psar"])
    result["psar_direction"] = np.where(
        np.isfinite(result["psar"]), np.where(c > result["psar"], 1.0, -1.0), np.nan
    )
    result["supertrend"], result["supertrend_direction"] = supertrend(
        h, low, c, result["atr_14"], 3.0
    )
    for name in ("psar", "supertrend"):
        result[f"{name}_distance_atr"] = _divide(c - result[name], result["atr_14"])
        direction = result[f"{name}_direction"]
        prior = np.r_[np.nan, direction[:-1]]
        valid = np.isfinite(direction) & np.isfinite(prior)
        result[f"{name}_flip_up"] = np.where(
            valid, (direction == 1) & (prior == -1), np.nan
        )
        result[f"{name}_flip_down"] = np.where(
            valid, (direction == -1) & (prior == 1), np.nan
        )
    return result


def feature_runtime():
    return {
        "talib": talib.__version__,
        "numpy": np.__version__,
        "pandas": pd.__version__,
    }


def current_market(con, minutes):
    market = dataset(con, "market", minutes)
    if (
        "parent_snapshot_id" in market
        and market["parent_snapshot_id"] != dataset(con, "market", 1)["snapshot_id"]
    ):
        raise ValueError(
            "Market source changed; run nova aggregate again before features or experiments"
        )
    return market


def build(root="data", minutes=60):
    root = Path(root).resolve()
    with connect(root) as con:
        market = current_market(con, minutes)
        _verify_files(market)
        snapshot = identity(
            {
                "market": market["snapshot_id"],
                "version": FEATURE_VERSION,
                "parameters": FEATURE_PARAMS,
                "minutes": minutes,
                "runtime": feature_runtime(),
            }
        )
        destination = root / "features" / f"{minutes}m" / snapshot[:16]
        manifest_path = destination / "manifest.json"
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text())
            _verify_files(manifest)
            _register_features(con, manifest, manifest_path)
            return manifest
        destination.mkdir(parents=True, exist_ok=True)
        files = []
        for source in market["files"]:
            frame = pq.read_table(source["path"]).to_pandas()
            result = compute(frame)
            keys = ["instrument", "bar_open_time", "bar_close_time"]
            for domain in ("core", "trend", "momentum"):
                columns = {
                    name: pa.array(frame[name])
                    for name in (frame.columns if domain == "core" else keys)
                }
                for name, definition in FEATURES.items():
                    if definition["domain"] == domain and name in result:
                        values = result[name]
                        columns[name] = (
                            pa.array(
                                values, mask=~np.isfinite(values), type=pa.float64()
                            )
                            if definition["unit"] != "boolean"
                            else pa.array(
                                values == 1, mask=~np.isfinite(values), type=pa.bool_()
                            )
                        )
                path = destination / f"{source['instrument']}_{domain}.parquet"
                pq.write_table(
                    pa.table(columns), path, compression="zstd", row_group_size=65536
                )
                files.append(
                    {
                        "instrument": source["instrument"],
                        "domain": domain,
                        "path": str(path),
                        "sha256": file_hash(path),
                        "rows": len(frame),
                    }
                )
            print(
                f"Built {minutes}m features: {source['instrument']} ({len(frame):,} bars)",
                flush=True,
            )
        manifest = {
            "snapshot_id": snapshot,
            "market_snapshot_id": market["snapshot_id"],
            "timeframe_minutes": minutes,
            "feature_version": FEATURE_VERSION,
            "parameters": FEATURE_PARAMS,
            "runtime": feature_runtime(),
            "catalog": FEATURES,
            "files": files,
            "volume_semantics": market["volume_semantics"],
            "windows": {
                r["instrument"]: {"start": r["start"], "end": r["end"]}
                for r in market["files"]
            },
        }
        write_json(manifest_path, manifest)
        _register_features(con, manifest, manifest_path)
        return manifest


def _register_features(con, manifest, path):
    minutes = manifest["timeframe_minutes"]
    register(con, "features", minutes, manifest["snapshot_id"], path)
    for domain in ("core", "trend", "momentum"):
        parquet_view(
            con,
            f"features_{domain}_{minutes}m",
            [r["path"] for r in manifest["files"] if r["domain"] == domain],
        )
    con.execute(f"""CREATE OR REPLACE VIEW features_{minutes}m AS SELECT c.*,t.* EXCLUDE(instrument,bar_open_time,bar_close_time),
        m.* EXCLUDE(instrument,bar_open_time,bar_close_time) FROM features_core_{minutes}m c
        JOIN features_trend_{minutes}m t USING(instrument,bar_open_time,bar_close_time)
        JOIN features_momentum_{minutes}m m USING(instrument,bar_open_time,bar_close_time)""")


def instrument_view(con, manifest, instrument):
    files = {
        r["domain"]: r["path"]
        for r in manifest["files"]
        if r["instrument"] == instrument
    }
    if not files:
        raise ValueError(f"Unknown instrument: {instrument}")
    con.execute(f"""CREATE OR REPLACE TEMP VIEW features AS SELECT c.*,t.* EXCLUDE(instrument,bar_open_time,bar_close_time),
        m.* EXCLUDE(instrument,bar_open_time,bar_close_time) FROM read_parquet({sql_string(files["core"])}) c
        JOIN read_parquet({sql_string(files["trend"])}) t USING(instrument,bar_open_time,bar_close_time)
        JOIN read_parquet({sql_string(files["momentum"])}) m USING(instrument,bar_open_time,bar_close_time)""")
