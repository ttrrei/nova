import pytest

from test_core import bar, signal, spec
from nova.trades import simulate


def test_short_return_is_linear_entry_notional_and_short_gap_is_adverse():
    rows = [bar(0), bar(1), bar(2, 105, 106, 104, 105)]
    signals = [signal(rows[0], short=True), signal(rows[1]), signal(rows[2])]
    trade = simulate(rows, signals, spec())[0]
    assert trade["net_return"] == pytest.approx(-0.05)
    assert trade["stop_price"] == 102
    assert trade["exit_reason"] == "stop_gap"


def test_existing_indicator_exit_uses_open_before_unknown_target_and_stop():
    rows = [bar(0), bar(1), bar(2, 100, 104, 96, 100)]
    settings = spec()
    settings["exit"]["take_profit_pct"] = 0.02
    signals = [
        signal(rows[0], long=True),
        signal(rows[1], exit_long=True),
        signal(rows[2]),
    ]
    trade = simulate(rows, signals, settings)[0]
    assert trade["exit_price"] == 100
    assert trade["exit_reason"] == "indicator_exit"


def test_stream_length_mismatch_is_rejected():
    with pytest.raises(ValueError, match="align"):
        simulate(iter([bar(0)]), iter([]), spec())


@pytest.mark.parametrize("side", [1, -1])
def test_observed_quotes_costs_and_intrabar_time_precision(side):
    rows = [bar(0), bar(1, 100, 104, 96, 100)]
    for row in rows:
        for point in ("open", "high", "low", "close"):
            row["bid_" + point] = row[point] - 0.1
            row["ask_" + point] = row[point] + 0.1
    settings = spec()
    settings["execution"].update(
        spread_bps=50,
        slippage_bps_per_side=1,
        commission_bps_round_trip=3,
        financing_bps_per_day=24,
    )
    signals = [signal(rows[0], long=side == 1, short=side == -1), signal(rows[1])]
    trade = simulate(rows, signals, settings)[0]
    expected_entry = (100 + side * 0.1) * (1 + side * 0.0001)
    assert trade["entry_price"] == pytest.approx(expected_entry)
    assert trade["exit_price"] == pytest.approx(
        expected_entry * (1 - side * 0.02) * (1 - side * 0.0001)
    )
    assert trade["exit_time_precision"] == "bar_interval"
    assert trade["cost_return"] == pytest.approx(0.0004)
