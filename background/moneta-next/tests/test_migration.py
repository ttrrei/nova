import abc
import ast
import hashlib
import importlib.util
import json
import re
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from moneta_next.alignment import align_closed_features
from moneta_next.catalog import FEATURES
from moneta_next.data_io import schema_mapping, selected_legacy_features, aggregate_sql
from moneta_next.compiler import compile_strategy
from moneta_next.config import load_strategy
from moneta_next.legacy_catalog import ORIGINAL_FEATURE_NAMES, BLOCKED_CACHED_FEATURES, direction_transitions
from moneta_next.vendor.supertrend import supertrend
from moneta_next.vendor.psar import psar_direction
from moneta_next.vendor.market_structure import confirmed_structure
from moneta_next.vendor.catalogue import center_stretch, capped_age
from moneta_next.vendor.utils import param_tag, validate_free_params

ROOT = Path(__file__).resolve().parents[1]


class ProvenanceTests(unittest.TestCase):
    def test_all_archived_files_match_pinned_git_blobs(self):
        report = json.loads((ROOT/'migration/PROVENANCE.json').read_text())
        inventory = json.loads((ROOT/'migration/source_inventory.json').read_text())
        source = {row['path']: row['sha'] for row in inventory['tree']}
        for row in report['reference_files']:
            data = (ROOT/'migration/reference'/row['source_path']).read_bytes()
            git = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
            self.assertEqual(git, row['git_blob_sha'])
            self.assertEqual(git, source[row['source_path']])

    def test_unchanged_runtime_modules_are_byte_identical(self):
        report = json.loads((ROOT/'migration/PROVENANCE.json').read_text())
        for row in report['runtime_reuse']:
            if isinstance(row['changes'], str) and row['changes'].startswith('none;'):
                self.assertEqual((ROOT/'migration/reference'/row['source']).read_bytes(), (ROOT/row['destination']).read_bytes())

    def test_no_old_strategy_or_oos_module_is_a_runtime_import(self):
        for path in (ROOT/'src/moneta_next').rglob('*.py'):
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    self.assertFalse((node.module or '').startswith(('strategy', 'pipeline', 'migration.reference')))


class IndicatorReuseTests(unittest.TestCase):
    def series(self, count=160):
        x = np.arange(count)
        close = 100+np.sin(x/4)*4+x/100
        return close+0.8, close-0.8, close, np.full(count, 1.5)

    def test_supertrend_prefix_invariance(self):
        h,l,c,a = self.series()
        a[:12] = np.nan
        full = supertrend(h,l,c,a,3)
        prefix = supertrend(h[:95],l[:95],c[:95],a[:95],3)
        for left, right in zip(full, prefix):
            np.testing.assert_allclose(left[:95],right,equal_nan=True)

    def test_supertrend_warmup_and_direction_domain(self):
        h,l,c,a = self.series()
        a[:12] = np.nan
        line, direction = supertrend(h,l,c,a,3)
        self.assertTrue(np.isnan(line[:12]).all())
        self.assertTrue(set(direction[12:]) <= {-1,1})

    def test_supertrend_rejects_nonpositive_multiplier(self):
        with self.assertRaises(ValueError):
            supertrend(*self.series(), 0)

    def test_psar_direction_preserves_source_convention(self):
        np.testing.assert_allclose(psar_direction(np.array([3.,2.,1.]), np.array([2.,2.,np.nan])), [1,-1,np.nan], equal_nan=True)

    def test_parameter_tags_and_validation(self):
        self.assertEqual(param_tag(0.02),'0p02')
        self.assertEqual(param_tag(0.20),'0p2')
        validate_free_params(((0.02,0.20),),(3.,))
        with self.assertRaises(ValueError):
            validate_free_params(((0.3,0.2),),(3.,))

    def test_confirmed_structure_never_backdates_pivot(self):
        h,l,c,a = self.series()
        n = len(c)
        out = confirmed_structure(h,l,c,a,np.ones(n,dtype=bool),np.zeros(n,dtype=bool),left=6,right=6,max_age=120)
        index = np.where(out['swing_high_confirmed']==1)[0]
        self.assertGreater(len(index),0)
        self.assertTrue(np.all(index-out['swing_high_pivot_index'][index] == 6))

    def test_structure_prefix_invariance_and_gap_reset(self):
        h,l,c,a = self.series()
        valid, reset = np.ones(len(c),dtype=bool),np.zeros(len(c),dtype=bool)
        reset[80] = True
        out = confirmed_structure(h,l,c,a,valid,reset)
        prefix = confirmed_structure(h[:90],l[:90],c[:90],a[:90],valid[:90],reset[:90])
        for name in out:
            np.testing.assert_allclose(out[name][:90],prefix[name],equal_nan=True)
        self.assertTrue(np.isnan(out['last_confirmed_swing_high'][80]))

    def test_center_stretch_prefix_and_degenerate_input(self):
        _,_,close,_ = self.series()
        for full, prefix in zip(center_stretch(close,24),center_stretch(close[:90],24)):
            np.testing.assert_allclose(full[:90],prefix,equal_nan=True)
        for values in center_stretch(np.ones(50),24):
            self.assertTrue(np.isnan(values).all())

    def test_capped_age_resets_at_gap(self):
        out = capped_age(np.ones(5),np.ones(5,dtype=bool),np.array([False,True,True,False,True]),cap=6)
        np.testing.assert_array_equal(out,[1,2,3,1,2])

    def test_direction_transitions_are_nullable_one_bar_events(self):
        out = direction_transitions({'psar_dir_0p02_0p2':[-1,-1,1,1,-1,np.nan,1]})
        np.testing.assert_allclose(out['psar_flip_up_0p02_0p2'],[np.nan,0,1,0,0,np.nan,np.nan],equal_nan=True)
        np.testing.assert_allclose(out['psar_flip_down_0p02_0p2'],[np.nan,0,0,0,1,np.nan,np.nan],equal_nan=True)


class AlignmentTests(unittest.TestCase):
    def test_hourly_context_visible_at_its_close_only(self):
        times = np.array(['2025-01-01T00:55','2025-01-01T01:00','2025-01-01T01:05','2025-01-01T02:00'],dtype='datetime64[m]')
        context = np.array(['2025-01-01T01:00','2025-01-01T02:00'],dtype='datetime64[m]')
        np.testing.assert_allclose(align_closed_features(times,context,[10,20]),[np.nan,10,10,20],equal_nan=True)

    def test_duplicate_context_is_rejected(self):
        times = np.array(['2025-01-01','2025-01-01'],dtype='datetime64[D]')
        with self.assertRaises(ValueError):
            align_closed_features(times[:1],times,[1,2])

    def test_empty_context_returns_unknown(self):
        out = align_closed_features(np.array(['2025-01-01'],dtype='datetime64[D]'),np.array([],dtype='datetime64[D]'),[])
        self.assertTrue(np.isnan(out).all())


class SchemaTests(unittest.TestCase):
    def test_raw_schema_and_quotes_are_mapped(self):
        columns = ['instrument','time','volume','is_complete']+[f'{side}_{field}' for side in ('mid','bid','ask') for field in ('o','h','l','c')]
        mapping = schema_mapping(columns)
        self.assertEqual(mapping['price']['open'],'mid_o')
        self.assertEqual(mapping['quotes']['ask_close'],'ask_c')

    def test_legacy_aggregate_requires_bar_count(self):
        columns = ['instrument','time','open','high','low','close','volume']
        with self.assertRaises(ValueError):
            schema_mapping(columns)
        self.assertEqual(schema_mapping(columns+['n_bars'])['mode'],'legacy_ohlcv_or_gold')

    def test_partial_quote_schema_rejected(self):
        columns = ['instrument','time','open','high','low','close','volume','n_bars','bid_o']
        with self.assertRaises(ValueError):
            schema_mapping(columns)

    def test_known_bad_cached_features_are_excluded(self):
        self.assertEqual(len(BLOCKED_CACHED_FEATURES),36)
        selected = selected_legacy_features(ORIGINAL_FEATURE_NAMES | {'h1_rsi_24'},True)
        self.assertEqual(len(selected),226)
        self.assertNotIn('bb_upper_24',selected)
        self.assertNotIn('aroon_up_24',selected)
        self.assertNotIn('vwap',selected)
        self.assertIn('psar_dir_0p02_0p2',selected)
        self.assertEqual(selected_legacy_features(ORIGINAL_FEATURE_NAMES,False),[])

    def test_full_registry_has_expected_names_and_safe_identifiers(self):
        self.assertEqual(len(ORIGINAL_FEATURE_NAMES),262)
        self.assertEqual(len(FEATURES),293)
        self.assertTrue(all(re.fullmatch('[A-Za-z_][A-Za-z0-9_]*',name) for name in FEATURES))

    def test_all_five_yaml_examples_compile_against_registry(self):
        paths=list((ROOT/'examples').glob('*.yaml'))
        self.assertEqual(len(paths),5)
        for path in paths:
            sql=compile_strategy(load_strategy(path),instrument_filter=True)
            self.assertIn('WHERE instrument=?',sql)
            self.assertNotIn('FOLLOWING',sql.upper())

    def test_aggregation_preserves_quote_ohlc_and_complete_counts(self):
        sql = aggregate_sql(60)
        for side in ('bid','ask'):
            self.assertIn(f'arg_min({side}_open, bar_open_time)',sql)
            self.assertIn(f'arg_max({side}_close, bar_open_time)',sql)
        self.assertIn('HAVING sum(n_bars)=60',sql)
        with self.assertRaises(ValueError):
            aggregate_sql(True)


def isolated_group(name, talib):
    """Exercise real migrated wiring against the documented TA-Lib tuple API.

    This is not a numerical TA-Lib parity test; optional live tests do that.
    """
    tree = ast.parse((ROOT/'src/moneta_next/legacy_engine.py').read_text())
    nodes = [node for node in tree.body if isinstance(node,ast.ClassDef) and node.name in {'BaseFeatureGroup',name}]
    namespace = {'abc':abc,'np':np,'talib':talib,'PSAR_PARAMS':(),'ST_MULTS':(),'EPS':1e-12,'KC_MULT':2.,'BB_SIGMA':2.}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'<reviewed legacy group>','exec'),namespace)
    return namespace[name]()


class ReturnOrderRepairTests(unittest.TestCase):
    def fake(self):
        array = lambda *args,**kwargs: np.full(30,100.)
        fake = {name:array for name in ['SMA','EMA','ADX','PLUS_DI','MINUS_DI','MAX','MIN','TRANGE','ATR','STDDEV']}
        fake['ATR'] = lambda *args,**kwargs: np.full(30,4.)
        fake['AROON'] = lambda *args,**kwargs: (np.full(30,20.),np.full(30,80.))
        fake['BBANDS'] = lambda *args,**kwargs: (np.full(30,110.),np.full(30,100.),np.full(30,90.))
        return SimpleNamespace(**fake)

    def test_aroon_down_up_contract_is_respected(self):
        group = isolated_group('TrendGroup',self.fake())
        prices = np.full(30,100.)
        values = group.compute(prices,prices+1,prices-1,prices,prices,(6,),(),{'psar_params':(),'st_mults':()})
        self.assertEqual(values['aroon_up_6'][0],80)
        self.assertEqual(values['aroon_down_6'][0],20)

    def test_bbands_upper_middle_lower_contract_is_respected(self):
        group = isolated_group('VolatilityGroup',self.fake())
        prices = np.full(30,100.)
        values = group.compute(prices,prices+1,prices-1,prices,prices,(6,),(),{})
        self.assertEqual(values['bb_upper_6'][0],110)
        self.assertEqual(values['bb_mid_6'][0],100)
        self.assertAlmostEqual(values['bb_width_6'][0],0.2)
        self.assertAlmostEqual(values['bb_pctb_6'][0],0.5)

    @unittest.skipUnless(importlib.util.find_spec('pandas'),'Optional pandas dependency is not installed')
    def test_first_gap_flag_is_initialized(self):
        import pandas as pd
        tree = ast.parse((ROOT/'src/moneta_next/legacy_engine.py').read_text())
        node = next(node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='is_gap_bar_series')
        namespace = {'np':np,'pd':pd}
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<reviewed gap helper>','exec'),namespace)
        times = pd.Series(pd.date_range('2025-01-01',periods=4,freq='h',tz='UTC'))
        np.testing.assert_array_equal(namespace['is_gap_bar_series'](times,3600),[0,0,0,0])


if __name__ == '__main__':
    unittest.main()
