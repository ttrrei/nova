import numpy as np
import pandas as pd
import pytest

from nova.catalog import FEATURES, FEATURE_PARAMS, FEATURE_VERSION
from nova.features import compute


def research_frame(n=100):
    close = 100 + np.sin(np.arange(n) / 3) + np.arange(n) / 20
    return pd.DataFrame(
        {
            "open": close,
            "high": close + 0.4,
            "low": close - 0.4,
            "close": close,
            "volume": 10 + np.arange(n) % 7,
            "bar_open_time": pd.date_range(
                "2024-01-01 05:00", periods=n, freq="h", tz="Australia/Sydney"
            ),
        }
    )


@pytest.mark.parametrize("count", [1, 14, 24, 25, 26, 60, 99])
def test_research_features_are_prefix_invariant(count):
    source = research_frame()
    full = compute(source)
    prefix = compute(source.iloc[:count])
    assert FEATURE_VERSION == "nova-features-v2"
    assert FEATURE_PARAMS["research"]["prior_range_bars"] == 24
    assert set(full) == set(FEATURES) - {"close", "volume"}
    for name in full:
        np.testing.assert_allclose(
            full[name][:count], prefix[name], equal_nan=True, err_msg=name
        )


def test_prior_boundaries_exclude_current_bar_and_preserve_unknown_warmup():
    frame = research_frame()
    frame.loc[24, ["high", "low", "close"]] = [150, 50, 140]
    out = compute(frame)
    for name in (
        "prior_high_24",
        "prior_low_24",
        "range_position_24",
        "range_width_atr_24",
        "breakout_up_24",
        "breakout_down_24",
        "failed_breakout_up_24",
        "failed_breakout_down_24",
        "relative_volume_24",
        "efficiency_24",
    ):
        assert np.isnan(out[name][:24]).all(), name
    assert out["prior_high_24"][24] == frame.high.iloc[:24].max()
    assert out["prior_low_24"][24] == frame.low.iloc[:24].min()
    assert out["prior_high_24"][25] == 150
    assert out["prior_low_24"][25] == 50
    assert out["range_position_24"][24] > 1
    assert out["breakout_up_24"][24] == 1
    assert out["failed_breakout_up_24"][24] == 0


@pytest.mark.parametrize("direction", [-1, 1])
def test_failed_breakout_sweep_requires_close_back_inside(direction):
    frame = research_frame()
    upper, lower = frame.high.iloc[:24].max(), frame.low.iloc[:24].min()
    frame.loc[24, ["high", "low", "close"]] = [
        upper + 1,
        lower - 1,
        (upper + lower) / 2,
    ]
    out = compute(frame)
    assert out["failed_breakout_up_24"][24] == 1
    assert out["failed_breakout_down_24"][24] == 1
    frame.loc[24, "close"] = upper + 0.5 if direction == 1 else lower - 0.5
    out = compute(frame)
    suffix = "up" if direction == 1 else "down"
    assert out[f"breakout_{suffix}_24"][24] == 1
    assert out[f"failed_breakout_{suffix}_24"][24] == 0


def test_research_formulas_clock_and_activity_provenance():
    frame = research_frame()
    out = compute(frame)
    i = 40
    atr = out["atr_14"][i]
    upper, lower = frame.high.iloc[i - 24 : i].max(), frame.low.iloc[i - 24 : i].min()
    assert out["range_width_atr_24"][i] == pytest.approx((upper - lower) / atr)
    assert out["range_atr"][i] == pytest.approx((frame.high[i] - frame.low[i]) / atr)
    assert out["return_6_atr"][i] == pytest.approx(
        (frame.close[i] - frame.close[i - 6]) / atr
    )
    assert out["relative_volume_24"][i] == pytest.approx(
        frame.volume[i] / frame.volume.iloc[i - 24 : i].mean()
    )
    path = frame.close.diff().abs().iloc[i - 23 : i + 1].sum()
    assert out["efficiency_24"][i] == pytest.approx(
        abs(frame.close[i] - frame.close[i - 24]) / path
    )
    assert out["utc_hour"][0] == 18  # January Sydney is UTC+11.
    assert FEATURES["relative_volume_24"]["unit"] == "prior_activity_ratio"
    assert FEATURES["utc_hour"]["available_at"] == "bar_close_time"


def test_zero_denominators_are_unknown_and_missing_optional_sources_supported():
    frame = research_frame()
    for name in ("open", "high", "low", "close"):
        frame[name] = 100.0
    frame.volume = 0.0
    out = compute(frame)
    for name in (
        "range_position_24",
        "range_width_atr_24",
        "return_6_atr",
        "range_atr",
        "relative_volume_24",
        "efficiency_24",
    ):
        assert np.isnan(out[name]).all(), name
    assert not any(np.isinf(values).any() for values in out.values())
    out = compute(frame.drop(columns=["volume", "bar_open_time"]))
    assert np.isnan(out["relative_volume_24"]).all()
    assert np.isnan(out["utc_hour"]).all()
