import csv
import importlib.util
import json
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

try:
    import duckdb
except ImportError:
    duckdb = None

from moneta_next.data_io import convert
from moneta_next.features import prepare_features
from moneta_next.catalog import FEATURES
from test_core import START, ROOT


def raw_csv(path, count=65, quotes=True):
    rows = []
    for index in range(count):
        row = {'instrument':'EUR_USD','time':(START+timedelta(minutes=index)).isoformat(),
               'is_complete':True,'volume':10,'mid_o':100+index/100,'mid_h':101+index/100,
               'mid_l':99+index/100,'mid_c':100.5+index/100}
        if quotes:
            for side,delta in [('bid',-0.1),('ask',0.1)]:
                for field in ('o','h','l','c'):
                    row[f'{side}_{field}'] = row[f'mid_{field}']+delta
        rows.append(row)
    with Path(path).open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


@unittest.skipIf(duckdb is None,'DuckDB dependency is not installed')
class MigrationDuckDBTests(unittest.TestCase):
    def test_raw_to_five_minute_preserves_bid_ask_and_drops_partial(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            raw_csv(root/'raw.csv',count=6)
            report=convert(root/'raw.csv',root/'normalized.parquet',1,5)
            self.assertEqual(report['output_rows'],1)
            with duckdb.connect() as con:
                row=con.execute('SELECT bid_open,ask_close,n_bars FROM read_parquet(?)',[str(root/'normalized.parquet')]).fetchone()
                self.assertAlmostEqual(row[0],99.9)
                self.assertAlmostEqual(row[1],100.64)
                self.assertEqual(row[2],5)

    def test_raw_mid_only_parquet_runs_through_core(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            raw_csv(root/'raw.csv',quotes=False)
            convert(root/'raw.csv',root/'normalized.parquet',1,5)
            with duckdb.connect() as con:
                result=prepare_features(con,root/'normalized.parquet',5)
                self.assertEqual(result['price_source'],'mid_with_configured_spread')

    def test_duplicate_survivor_prefers_complete_quotes(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            folder=root/'old'
            folder.mkdir()
            raw_csv(folder/'a.csv',count=5,quotes=True)
            # Same schema, but missing quote payloads in the second file.
            with (folder/'a.csv').open() as stream:
                rows=list(csv.DictReader(stream))
            for row in rows:
                for name in row:
                    if name.startswith(('bid_','ask_')):
                        row[name]=''
            with (folder/'b.csv').open('w',newline='') as stream:
                writer=csv.DictWriter(stream,fieldnames=list(rows[0]))
                writer.writeheader(); writer.writerows(rows)
            report=convert(folder,root/'normalized.csv',1)
            self.assertEqual(report['complete_candidates'],10)
            self.assertEqual(report['deduplicated_rows'],5)
            with (root/'normalized.csv').open() as stream:
                self.assertTrue(all(row['bid_open'] for row in csv.DictReader(stream)))

    def test_parquet_export_reuses_catalogue_without_replacing_working_table(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            raw_csv(root/'raw.csv')
            convert(root/'raw.csv',root/'normalized.parquet',1,5)
            with duckdb.connect() as con:
                result=prepare_features(con,root/'normalized.parquet',5,feature_dir=root/'store')
                self.assertEqual(len(result['parquet_exports']),2)
                self.assertEqual(con.execute("SELECT table_type FROM information_schema.tables WHERE table_name='features_core'").fetchone()[0],'BASE TABLE')
                self.assertEqual(con.execute('SELECT count(*) FROM data_tables').fetchone()[0],2)

    def test_imported_feature_profile_derives_psar_events(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            raw_csv(root/'raw.csv',count=65,quotes=False)
            convert(root/'raw.csv',root/'normalized.csv',1)
            with (root/'normalized.csv').open() as stream:
                rows=list(csv.DictReader(stream))
            for index,row in enumerate(rows):
                row['psar_dir_0p02_0p2']=-1 if index<30 else 1
            with (root/'normalized.csv').open('w',newline='') as stream:
                writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
            with duckdb.connect() as con:
                prepare_features(con,root/'normalized.csv',1,profile='imported')
                self.assertEqual(con.execute('SELECT count(*) FROM features WHERE psar_flip_up_0p02_0p2').fetchone()[0],1)

    def test_cannot_reuse_cached_features_across_resampling(self):
        with self.assertRaises(ValueError):
            convert('irrelevant','irrelevant.parquet',1,60,reuse_features=True)


@unittest.skipUnless(duckdb is not None and importlib.util.find_spec('talib') and importlib.util.find_spec('pandas_ta_classic'),'Full legacy numerical dependencies are not installed')
class LegacyNumericalTests(unittest.TestCase):
    def test_full_feature_profile_matches_registered_names_and_known_talib_outputs(self):
        import numpy as np
        import pandas as pd
        import talib
        from moneta_next.legacy_engine import compute_instrument_features
        from moneta_next.legacy_catalog import ORIGINAL_FEATURE_NAMES
        count=500
        c=100+np.sin(np.arange(count)/13)+np.arange(count)/100
        frame=pd.DataFrame({'instrument':'EUR_USD','time':pd.date_range('2025-01-01',periods=count,freq='h',tz='UTC'),
            'open':c,'high':c+1,'low':c-1,'close':c,'volume':100.,'n_bars':60})
        calculated=compute_instrument_features(frame,3600)
        self.assertEqual(set(calculated),ORIGINAL_FEATURE_NAMES)
        upper,middle,lower=talib.BBANDS(c,timeperiod=24,nbdevup=2,nbdevdn=2,matype=0)
        np.testing.assert_allclose(calculated['bb_upper_24'],upper,equal_nan=True)
        np.testing.assert_allclose(calculated['bb_mid_24'],middle,equal_nan=True)
        down,up=talib.AROON(c+1,c-1,timeperiod=24)
        np.testing.assert_allclose(calculated['aroon_up_24'],up,equal_nan=True)


if __name__=='__main__':
    unittest.main()
