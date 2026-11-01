import numpy as np
import pandas as pd
import pytest
import talib

from nova.catalog import FEATURES
from nova.features import compute


def frame(n=200, flat=False):
    c = (
        np.full(n, 100.0)
        if flat
        else 100 + np.sin(np.arange(n) / 8) * 2 + np.arange(n) * 0.01
    )
    return pd.DataFrame({"open": c, "high": c + 0.1, "low": c - 0.1, "close": c})


@pytest.mark.parametrize("count", [1, 6, 15, 24, 60, 120])
def test_all_features_are_prefix_invariant(count):
    source = frame()
    full = compute(source)
    prefix = compute(source.iloc[:count])
    assert set(full) == set(FEATURES) - {"close", "volume"}
    for name in full:
        np.testing.assert_allclose(
            full[name][:count], prefix[name], equal_nan=True, err_msg=name
        )


def test_indicator_parity_and_zero_range_safety():
    f = frame()
    out = compute(f)
    np.testing.assert_allclose(
        out["ema_24"], talib.EMA(f.close.to_numpy(), timeperiod=24), equal_nan=True
    )
    np.testing.assert_allclose(
        out["psar"],
        talib.SAR(f.high.to_numpy(), f.low.to_numpy(), acceleration=0.02, maximum=0.2),
        equal_nan=True,
    )
    np.testing.assert_allclose(
        out["atr_14"],
        talib.ATR(
            f.high.to_numpy(), f.low.to_numpy(), f.close.to_numpy(), timeperiod=14
        ),
        equal_nan=True,
    )
    f = frame(flat=True)
    f.high = f.close
    f.low = f.close
    for name, values in compute(f).items():
        assert not np.isinf(values).any(), name


def test_warmup_is_unknown_and_events_are_one_bar():
    out = compute(frame())
    assert np.isnan(out["sma_24"][:23]).all()
    assert np.isnan(out["sma_cross_up_6_24"][:24]).all()
    assert set(out["psar_direction"][np.isfinite(out["psar_direction"])]) == {-1, 1}
    assert not (
        (out["ema_cross_up_6_24"][1:] == 1) & (out["ema_cross_up_6_24"][:-1] == 1)
    ).any()
