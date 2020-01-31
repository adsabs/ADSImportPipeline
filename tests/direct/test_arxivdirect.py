
import copy
from mock import patch
import os
import sys
import unittest
import xmltodict

from aip import tasks
from aip import app as app_module
from aip.models import Base
from tests.stubdata import directdata
from tests.stubdata import ADSRECORDS
from aip.direct import ArXivDirect
from aip.classic import read_records

if '/proj/ads/soft/python/lib/site-packages' not in sys.path:
    sys.path.append('/proj/ads/soft/python/lib/site-packages')
try:
    import ads.ADSCachedExports as ads_ex
except ImportError:
    print 'Warning: adspy not available'
    ads_ex = None


class TestArXivDirect(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.proj_home = os.path.join(os.path.dirname(__file__), '../..')
        self._app = tasks.app
        self.app = app_module.ADSImportPipelineCelery('test', local_config={
            'SQLALCHEMY_URL': 'sqlite:///',
            'SQLALCHEMY_ECHO': False
            })
        tasks.app = self.app  # monkey-patch the app object
        Base.metadata.bind = self.app._session.get_bind()
        Base.metadata.create_all()

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        Base.metadata.drop_all()
        self.app.close_app()
        tasks.app = self._app

    @unittest.skipIf(not ads_ex, "ads.ADSCachedExports not available")
    def test_ArXivDirect_add_direct(self):
        with patch.object(self.app, 'forward_message', return_value=None) as next_task:

            # for a novel record (not yet ingested)
            origin_shouldbe = 'ARXIV'
            entryd_shouldbe = ads_ex.iso_8601_time(None)
            test_record = directdata.DIRECT_RAW_INPUT
            test_adsrec = ArXivDirect.add_direct(test_record)
            test_serialized = test_adsrec.root.serialize()
            xdict = xmltodict.parse(test_serialized)['records']['record']['metadata'][0]
            test_origin = xdict['@origin']
            test_entryd = xdict['creation_time']
            self.assertEqual(test_origin,'ARXIV')
            self.assertEqual(test_entryd,entryd_shouldbe)



            origin_shouldbe2 = 'classic'
            entryd_shouldbe2 = '2019-01-01T12:00:00Z'
            test_adsrec = ArXivDirect.add_direct(test_record, '2019-01-01T12:00:00Z')
            test_serialized = test_adsrec.root.serialize()
            xdict = xmltodict.parse(test_serialized)['records']['record']['metadata'][0]
            test_origin = xdict['@origin']
            test_entryd = xdict['creation_time']
#           self.assertEqual(test_origin,'classic')
            self.assertEqual(test_entryd,entryd_shouldbe2)



if __name__ == '__main__':
    unittest.main()
