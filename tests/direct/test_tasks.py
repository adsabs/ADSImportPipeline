
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

if '/proj/ads/soft/python/lib/site-packages' not in sys.path:
    sys.path.append('/proj/ads/soft/python/lib/site-packages')
try:
    import ads.ADSCachedExports as ads_ex
except ImportError:
    print 'Warning: adspy not available'
    ads_ex = None


class TestWorkers(unittest.TestCase):

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

    @unittest.skipUnless(ads_ex, 'adspy not available')
    def test_task_merge_arxiv_direct(self):
        self.maxDiff = None
        with patch('aip.tasks.task_output_direct.delay', return_value=None) as next_task:
            self.assertFalse(next_task.called)

            inputrec = copy.deepcopy(directdata.DIRECT_RAW_INPUT)
            out = copy.deepcopy(directdata.DIRECT_MERGE_INPUT)

            tasks.task_merge_arxiv_direct(inputrec)
            self.assertTrue(next_task.called)
            out['id'] = 1  # from database
            self.assertEqual(next_task.call_args_list[0][0][0], out)
            r = self.app.get_record(directdata.DIRECT_RAW_INPUT['bibcode'])
            self.assertEqual(directdata.DIRECT_RAW_INPUT['bibcode'], r['bibcode'])
            self.assertEqual('direct', r['origin'])

    @unittest.skipUnless(ads_ex, 'adspy not available')
    def test_task_direct_then_classic(self):
        """verify origin changes after classic record is processed"""
        with patch('aip.tasks.task_output_direct.delay', return_value=None) as next_task:
            inputrec = copy.deepcopy(directdata.DIRECT_RAW_INPUT)
            tasks.task_merge_arxiv_direct(inputrec)
            r = self.app.get_record(directdata.DIRECT_RAW_INPUT['bibcode'])
            self.assertEqual('direct', r['origin'])
            # now input the same record from classic and verify origin changes
            # we just need a classic record with the right bibcode
            foo = copy.deepcopy(ADSRECORDS['2015ApJ...815..133S'])
            foo['bibcode'] = u'2017arXiv171105739L'
            with patch('aip.tasks.task_output_results.delay', return_value=None) as next_task:
                # first process via classic/task_merge_metadata
                # we just need a classic record with the right bibcode
                foo = copy.deepcopy(ADSRECORDS['2015ApJ...815..133S'])
                foo['bibcode'] = u'2017arXiv171105739L'
                tasks.task_merge_metadata(foo)
                r = self.app.get_record(directdata.DIRECT_RAW_INPUT['bibcode'])
                self.assertEqual('classic', r['origin'])

    @unittest.skipUnless(ads_ex, 'adspy not available')
    def test_task_classic_then_direct(self):
        """verify if direct arrives after classic the origin field is not overwritten"""
        with patch('aip.tasks.task_output_results.delay', return_value=None) as next_task:
            # process a record via classic/task_merge_metadata
            # we just need a classic record with the right bibcode
            foo = copy.deepcopy(ADSRECORDS['2015ApJ...815..133S'])
            foo['bibcode'] = u'2017arXiv171105739L'
            tasks.task_merge_metadata(foo)
            r = self.app.get_record(directdata.DIRECT_RAW_INPUT['bibcode'])
            self.assertEqual('classic', r['origin'])
            # now ingest direct
            with patch('aip.tasks.task_output_direct.delay', return_value=None):
                inputrec = copy.deepcopy(directdata.DIRECT_RAW_INPUT)
                tasks.task_merge_arxiv_direct(inputrec)
                r = self.app.get_record(directdata.DIRECT_RAW_INPUT['bibcode'])
                self.assertEqual('classic', r['origin'])

    def test_task_output_arxiv_results(self):
        with patch.object(self.app, 'forward_message', return_value=None) as next_task:

            self.assertFalse(next_task.called)
            tasks.task_output_direct(directdata.DIRECT_MERGE_INPUT)
            self.assertTrue(next_task.called)
            expected = directdata.DIRECT_OUTPUT.copy()
            self.maxDiff = None
            self.assertDictEqual(expected, next_task.call_args[0][0].toJSON())


if __name__ == '__main__':
    unittest.main()
