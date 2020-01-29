
import copy
from mock import patch
import os
import sys
import unittest

from aip import tasks
from aip import app as app_module
from aip.models import Base
from tests.stubdata import directdata
from tests.stubdata import ADSRECORDS
from aip.direct import ArXivDirect

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

    def test_ArXivDirect_add_direct(self):
        with patch.object(self.app, 'forward_message', return_value=None) as next_task:

            # self.assertFalse(next_task.called)
            # tasks.task_output_direct(directdata.DIRECT_MERGE_INPUT)
            # self.assertTrue(next_task.called)
            # expected = directdata.DIRECT_OUTPUT.copy()
            # self.maxDiff = None
            # self.assertDictEqual(expected, next_task.call_args[0][0].toJSON())
            self.assertEqual('a','b')


if __name__ == '__main__':
    unittest.main()
