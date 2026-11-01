import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from nova.compiler import compile_strategy
from nova.config import load_strategy
from nova.metrics import summarize
from nova.trades import simulate

ROOT = Path(__file__).resolve().parents[1]
START = datetime(2025, 1, 1, tzinfo=timezone.utc)


def spec():
    value = load_strategy(ROOT / "strategies/mean_reversion.yaml")
    value["execution"] = {key: 0.0 for key in value["execution"]}
    value["exit"] = {"stop_loss_pct": 0.02}
    return value


def bar(index, opening=100, high=100.5, low=99.5, close=100):
    return {
        "instrument": "TEST",
        "bar_open_time": START + timedelta(hours=index),
        "bar_close_time": START + timedelta(hours=index + 1),
        "open": opening,
        "high": high,
        "low": low,
        "close": close,
    }


def signal(row, long=False, short=False, exit_long=False, exit_short=False):
    return {
        "instrument": row["instrument"],
        "bar_open_time": row["bar_open_time"],
        "bar_close_time": row["bar_close_time"],
        "entry_long": long,
        "entry_short": short,
        "exit_long": exit_long,
        "exit_short": exit_short,
    }


class TradeTests(unittest.TestCase):
    def execute(self, rows, side=1, settings=None, signals=None):
        if signals is None:
            signals = [
                signal(
                    row, long=index == 0 and side == 1, short=index == 0 and side == -1
                )
                for index, row in enumerate(rows)
            ]
        return simulate(rows, signals, settings or spec())

    def test_signal_executes_next_open(self):
        rows = [bar(0), bar(1, 101, 101.5, 100.5, 101)]
        trade = self.execute(rows)[0]
        self.assertEqual(trade["entry_time"], rows[1]["bar_open_time"])
        self.assertEqual(trade["entry_price"], 101)
        self.assertEqual(trade["exit_reason"], "end_of_data")

    def test_last_bar_signal_cannot_create_a_trade(self):
        self.assertEqual(self.execute([bar(0)]), [])

    def test_long_stop_is_two_percent_of_entry(self):
        trade = self.execute([bar(0), bar(1, 100, 101, 97, 99)])[0]
        self.assertEqual(trade["exit_price"], 98)
        self.assertAlmostEqual(trade["net_return"], -0.02)

    def test_short_stop_is_two_percent_of_entry(self):
        trade = self.execute([bar(0), bar(1, 100, 103, 99, 101)], side=-1)[0]
        self.assertEqual(trade["exit_price"], 102)
        self.assertAlmostEqual(trade["net_return"], -0.02)

    def test_unknown_long_intrabar_order_selects_loss(self):
        settings = spec()
        settings["exit"]["take_profit_pct"] = 0.02
        trade = self.execute([bar(0), bar(1, 100, 104, 96, 100)], settings=settings)[0]
        self.assertEqual(trade["exit_reason"], "stop_loss")

    def test_unknown_short_intrabar_order_selects_loss(self):
        settings = spec()
        settings["exit"]["take_profit_pct"] = 0.02
        trade = self.execute(
            [bar(0), bar(1, 100, 104, 96, 100)], side=-1, settings=settings
        )[0]
        self.assertEqual(trade["exit_reason"], "stop_loss")

    def test_gap_is_not_clamped_to_stop_price(self):
        trade = self.execute([bar(0), bar(1), bar(2, 95, 96, 94, 95)])[0]
        self.assertEqual(trade["exit_price"], 95)
        self.assertEqual(trade["exit_reason"], "stop_gap")

    def test_known_open_target_precedes_later_intrabar_stop(self):
        settings = spec()
        settings["exit"]["take_profit_pct"] = 0.02
        trade = self.execute(
            [bar(0), bar(1), bar(2, 103, 104, 97, 100)], settings=settings
        )[0]
        self.assertEqual(trade["exit_reason"], "take_profit")

    def test_indicator_exit_executes_next_open_before_later_stop(self):
        rows = [bar(0), bar(1), bar(2, 100, 101, 95, 97)]
        signals = [
            signal(rows[0], long=True),
            signal(rows[1], exit_long=True),
            signal(rows[2]),
        ]
        trade = self.execute(rows, signals=signals)[0]
        self.assertEqual(trade["exit_price"], 100)
        self.assertEqual(trade["exit_reason"], "indicator_exit")

    def test_holding_one_bar_exits_at_following_open(self):
        settings = spec()
        settings["exit"]["max_holding_bars"] = 1
        trade = self.execute([bar(0), bar(1), bar(2)], settings=settings)[0]
        self.assertEqual(trade["exit_time"], START + timedelta(hours=2))
        self.assertEqual(trade["exit_reason"], "time_exit")
        self.assertEqual(trade["bars_held"], 1)

    def test_spread_and_slippage_are_adverse_on_both_sides(self):
        for side in (1, -1):
            settings = spec()
            settings["execution"]["spread_bps"] = 10
            settings["execution"]["slippage_bps_per_side"] = 2
            trade = self.execute([bar(0), bar(1)], side=side, settings=settings)[0]
            self.assertLess(trade["gross_return"], 0)

    def test_observed_bid_ask_does_not_add_synthetic_spread(self):
        rows = [bar(0), bar(1)]
        for row in rows:
            for point in ("open", "high", "low", "close"):
                row["bid_" + point] = row[point] - 0.1
                row["ask_" + point] = row[point] + 0.1
        settings = spec()
        settings["execution"]["spread_bps"] = 100
        trade = self.execute(rows, settings=settings)[0]
        self.assertAlmostEqual(trade["entry_price"], 100.1)
        self.assertAlmostEqual(trade["exit_price"], 99.9)

    def test_flat_commission_and_financing(self):
        settings = spec()
        settings["execution"]["commission_bps_round_trip"] = 3
        settings["execution"]["financing_bps_per_day"] = 24
        trade = self.execute([bar(0), bar(1)], settings=settings)[0]
        self.assertAlmostEqual(trade["cost_return"], 0.0004)

    def test_persistent_signal_has_one_position_and_no_same_bar_reentry(self):
        rows = [bar(0), bar(1, 100, 101, 97, 99), bar(2), bar(3)]
        signals = [signal(row, long=True) for row in rows]
        trades = self.execute(rows, signals=signals)
        self.assertEqual(len(trades), 2)
        self.assertEqual(trades[1]["entry_time"], rows[3]["bar_open_time"])

    def test_conflicting_directions_are_skipped(self):
        rows = [bar(0), bar(1)]
        self.assertEqual(
            self.execute(
                rows, signals=[signal(row, long=True, short=True) for row in rows]
            ),
            [],
        )

    def test_misaligned_signals_are_rejected(self):
        with self.assertRaises(ValueError):
            simulate([bar(0)], [signal(bar(1))], spec())


class ConfigurationTests(unittest.TestCase):
    def load_text(self, text):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "strategy.yaml"
            path.write_text(text, encoding="utf-8")
            return load_strategy(path)

    def test_duplicate_yaml_keys_rejected(self):
        with self.assertRaises(ValueError):
            self.load_text("id: one\nid: two\n")

    def test_strategy_python_escape_rejected(self):
        with self.assertRaises(ValueError):
            self.load_text(
                (ROOT / "strategies/mean_reversion.yaml").read_text()
                + "\npython: print('escape')\n"
            )

    def test_non_two_percent_stop_rejected(self):
        with self.assertRaises(ValueError):
            self.load_text(
                (ROOT / "strategies/mean_reversion.yaml")
                .read_text()
                .replace("0.02", "0.03")
            )

    def test_unknown_feature_and_sql_injection_rejected(self):
        value = spec()
        value["entry"] = {
            "long": {"feature": "close; DROP TABLE bars", "op": "gt", "value": 0}
        }
        with self.assertRaises(ValueError):
            compile_strategy(value)

    def test_boolean_parameter_is_not_a_number(self):
        value = spec()
        value["entry"] = {"long": {"feature": "close", "op": "gt", "value": True}}
        with self.assertRaises(ValueError):
            compile_strategy(value)

    def test_event_requires_boolean_comparison(self):
        value = spec()
        value["entry"] = {
            "long": {"feature": "sma_cross_up_6_24", "op": "eq", "value": 1}
        }
        with self.assertRaises(ValueError):
            compile_strategy(value)

    def test_temporal_operators_emit_past_only_windows(self):
        sql = compile_strategy(load_strategy(ROOT / "strategies/trend_hold.yaml"))
        self.assertIn("lag(", sql)
        self.assertIn("PRECEDING AND CURRENT ROW", sql)
        self.assertNotIn("LEAD(", sql.upper())
        self.assertNotIn("FOLLOWING", sql.upper())


class MetricTests(unittest.TestCase):
    def test_zero_entry_months_are_not_dropped(self):
        start, end = START, datetime(2025, 4, 1, tzinfo=timezone.utc)
        trade = {
            "instrument": "TEST",
            "entry_time": START,
            "exit_time": START + timedelta(hours=1),
            "net_return": 0.01,
        }
        result = summarize([trade], {"TEST": (start, end)})["per_instrument"]["TEST"]
        self.assertEqual(
            [row["actual_entries"] for row in result["monthly_entries"]], [1, 0, 0]
        )
        self.assertFalse(result["passes_initial_screen"])
        self.assertAlmostEqual(
            result["annualized_trade_return_score"],
            0.01 / ((end - start).days / 365.25),
        )

    def test_pooled_months_include_no_entry_months(self):
        result = summarize([], {"TEST": (START, START + timedelta(days=60))})
        self.assertEqual(
            result["pooled_monthly_actual_entries"],
            {"2025-01": 0, "2025-02": 0, "2025-03": 0},
        )

    def test_no_trade_years_remain_in_annual_report(self):
        result = summarize(
            [], {"TEST": (START, datetime(2027, 1, 1, tzinfo=timezone.utc))}
        )
        self.assertEqual(
            result["per_instrument"]["TEST"]["yearly_net_trade_return_sum"],
            {"2025": 0.0, "2026": 0.0},
        )

    def test_no_complete_months_cannot_pass_monthly_screen(self):
        result = summarize([], {"TEST": (START, START + timedelta(days=2))})[
            "per_instrument"
        ]["TEST"]
        self.assertIsNone(result["every_full_month_has_entry"])
        self.assertFalse(result["passes_initial_screen"])

    def test_monthly_count_uses_open_not_exit_date(self):
        entry = datetime(2025, 1, 31, 23, tzinfo=timezone.utc)
        trade = {
            "instrument": "TEST",
            "entry_time": entry,
            "exit_time": entry + timedelta(hours=2),
            "net_return": 0.01,
        }
        result = summarize(
            [trade], {"TEST": (START, datetime(2025, 3, 1, tzinfo=timezone.utc))}
        )["per_instrument"]["TEST"]
        self.assertEqual(result["monthly_entries"][0]["actual_entries"], 1)
        self.assertEqual(result["yearly_net_trade_return_sum"], {"2025": 0.01})


if __name__ == "__main__":
    unittest.main()
