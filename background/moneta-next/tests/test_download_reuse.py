import importlib.util
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch


@unittest.skipUnless(importlib.util.find_spec('requests'),'Optional requests dependency is not installed')
class DownloadReuseTests(unittest.TestCase):
    def check_page_boundary(self, inclusive):
        from moneta_next.vendor import oanda
        from moneta_next.download import download
        import csv
        start=datetime(2025,1,1,tzinfo=timezone.utc)
        times=[start+timedelta(minutes=i) for i in range(9)]

        class FakeSession:
            def get(self,url,params,headers,timeout):
                lower=datetime.fromisoformat(params['from'].replace('Z','+00:00'))
                upper=datetime.fromisoformat(params['to'].replace('Z','+00:00'))
                picked=[t for t in times if lower<=t<upper or inclusive and t==upper]
                candles=[{'time':t.isoformat(),'complete':True,'volume':5,
                    'mid':{'o':'100','h':'101','l':'99','c':'100'},
                    'bid':{'o':'99.9','h':'100.9','l':'98.9','c':'99.9'},
                    'ask':{'o':'100.1','h':'101.1','l':'99.1','c':'100.1'}} for t in picked]
                class Response:
                    def raise_for_status(self): pass
                    def json(self): return {'candles':candles}
                return Response()

        with tempfile.TemporaryDirectory() as directory, patch.object(oanda,'PAGE_SIZE',3):
            path=download('EUR_USD',times[0].isoformat(),times[-1].isoformat(),Path(directory)/'raw.csv',session=FakeSession(),token='offline-fixture')
            with path.open() as stream:
                rows=list(csv.DictReader(stream))
            self.assertEqual(len(rows),9)
            self.assertEqual(len({row['time'] for row in rows}),9)
            self.assertTrue(all(row['ask_c'] for row in rows))

    def test_inclusive_api_end_does_not_duplicate_or_drop_candles(self):
        self.check_page_boundary(True)

    def test_exclusive_api_end_does_not_drop_last_candle(self):
        self.check_page_boundary(False)
