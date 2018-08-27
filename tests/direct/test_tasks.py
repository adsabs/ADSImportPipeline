
from adsputils import get_date
from aip import tasks, app as app_module
from aip.models import Base, Records
from collections import OrderedDict
from mock import patch
from tests.stubdata import ADSRECORDS, mergerdata, directdata
import mock, copy
import os
import sys
import unittest
from adsmsg import BibRecord

class TestWorkers(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.proj_home = os.path.join(os.path.dirname(__file__), '../..')
        self._app = tasks.app
        self.app = app_module.ADSImportPipelineCelery('test',local_config={
            'SQLALCHEMY_URL': 'sqlite:///',
            'SQLALCHEMY_ECHO': False
            })
        tasks.app = self.app # monkey-patch the app object
        Base.metadata.bind = self.app._session.get_bind()
        Base.metadata.create_all()


    def tearDown(self):
        unittest.TestCase.tearDown(self)
        Base.metadata.drop_all()
        self.app.close_app()
        tasks.app = self._app



    def test_task_merge_arxiv_direct(self):
        self.maxDiff = None
        with patch('aip.tasks.task_output_direct.delay', return_value=None) as next_task:
            self.assertFalse(next_task.called)

            inputrec = copy.deepcopy(directdata.DIRECT_RAW_INPUT)
            out = copy.deepcopy(directdata.DIRECT_MERGE_INPUT)

            tasks.task_merge_arxiv_direct(inputrec)
            self.assertTrue(next_task.called)
            self.assertEqual(next_task.call_args_list[0][0][0],out)


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
