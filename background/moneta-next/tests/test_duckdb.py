import csv
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

try:
    import duckdb
except ImportError:
    duckdb = None

from moneta_next.compiler import compile_strategy
from moneta_next.features import prepare_features
from test_core import START, ROOT, bar, spec


def write_bars(path, count=80):
    rows = []
    for index in range(count):
        row = bar(index, 100+index/10, 101+index/10, 99+index/10, 100+index/10)
        row.update(volume=100, is_complete="true")
        rows.append(row)
    with Path(path).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


@unittest.skipIf(duckdb is None, "DuckDB dependency is not installed")
class DuckDBTests(unittest.TestCase):
    def setUp(self):
        self.connection = duckdb.connect()
        self.connection.execute("SET TimeZone='UTC'")

    def tearDown(self):
        self.connection.close()

    def test_feature_warmup_and_reuse(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"bars.csv"
            write_bars(path)
            first = prepare_features(self.connection, path, 60)
            second = prepare_features(self.connection, path, 60)
            self.assertFalse(first["feature_cache_reused"])
            self.assertTrue(second["feature_cache_reused"])
            self.assertEqual(self.connection.execute("SELECT count(*) FROM features WHERE sma_24 IS NULL").fetchone()[0], 23)
            self.assertEqual(self.connection.execute("SELECT count(*) FROM features WHERE sma_cross_up_6_24 IS NULL").fetchone()[0], 24)
            self.assertEqual(self.connection.execute("SELECT count(*) FROM features WHERE sma_cross_down_6_24 IS NULL").fetchone()[0], 24)

    def test_appending_future_bars_does_not_change_past_features(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"bars.csv"
            write_bars(path, 50)
            prepare_features(self.connection, path, 60)
            prefix = self.connection.execute("SELECT * FROM features ORDER BY bar_open_time").fetchall()
            write_bars(path, 80)
            prepare_features(self.connection, path, 60)
            extended = self.connection.execute("SELECT * FROM features ORDER BY bar_open_time LIMIT 50").fetchall()
            self.assertEqual(prefix, extended)

    def test_unknown_feature_negation_does_not_trigger_warmup_entry(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"bars.csv"
            write_bars(path)
            prepare_features(self.connection, path, 60)
            value = spec()
            value["entry"] = {"long": {"not": {"feature": "sma_24", "op": "gt", "value": 0}}}
            signals = self.connection.execute(compile_strategy(value)).fetchall()
            self.assertTrue(all(not row[3] for row in signals[:23]))

    def test_after_event_confirms_on_third_following_close(self):
        self.connection.execute("CREATE TABLE features (instrument VARCHAR, bar_open_time TIMESTAMPTZ, bar_close_time TIMESTAMPTZ, sma_cross_up_6_24 BOOLEAN, sma_alignment_6_24 INTEGER)")
        for index in range(6):
            self.connection.execute("INSERT INTO features VALUES (?, ?, ?, ?, ?)", ["TEST", START+timedelta(hours=index), START+timedelta(hours=index+1), index == 0, 1])
        value = spec()
        value["entry"] = {"long": {"after_event": {"bars": 3,
            "event": {"feature": "sma_cross_up_6_24", "op": "eq", "value": True},
            "condition": {"feature": "sma_alignment_6_24", "op": "eq", "value": 1}}}}
        rows = self.connection.execute(compile_strategy(value)).fetchall()
        self.assertEqual([bool(row[3]) for row in rows], [False, False, False, True, False, False])

    def test_invalid_timeframe_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"bars.csv"
            write_bars(path)
            with self.assertRaises(ValueError):
                prepare_features(self.connection, path, 5)

    def test_both_example_strategies_run_end_to_end(self):
        from moneta_next.cli import run
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root/"bars.csv"
            write_bars(path, 100)
            for name in ["trend_hold.yaml", "mean_reversion.yaml"]:
                destination, summary = run(path, ROOT/"examples"/name, root/"research.duckdb", root/"runs")
                self.assertTrue((destination/"manifest.json").exists())
                self.assertIn("TEST", summary["per_instrument"])


if __name__ == "__main__":
    unittest.main()
