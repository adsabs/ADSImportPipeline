
from adsputils import get_date
from aip import tasks, app as app_module
from aip.models import Base, Records
from collections import OrderedDict
from mock import patch
from tests.stubdata import stubdata
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


    def test_task_find_new_records(self):
        with patch('aip.tasks.task_read_records.delay', return_value=None) as next_task, \
            patch.object(self.app, 'get_record', return_value = \
                  [{'bibcode': 'foo', 'fingerprint': {'JSON_fingerprint': 'fp_bar'}},
                   {'bibcode': 'baz', 'fingerprint': {'JSON_fingerprint': 'fp_bard'}},
                         ]) as read_recs:
            
            
            self.assertFalse(next_task.called)
            tasks.task_find_new_records([
                                       ('hey', 'fp_hoo'),
                                       ('foo', 'fp_bar'), 
                                       ('baz', {'JSON_fingerprint': 'fp_bard'}),
                                       ])
            self.assertTrue(next_task.called)
            self.assertEqual(next_task.call_count, 2)
            # notice the different order; first we index the differnet fingerprints, the last bibcode was missing...
            self.assertEqual(str(next_task.call_args_list), "[call([('foo', 'fp_bar')]), call(('hey', 'fp_hoo'))]")


    def test_task_read_records(self):
        with patch('aip.tasks.task_merge_metadata.delay', return_value=None) as next_task, \
            patch('aip.libs.read_records.readRecordsFromADSExports', 
                  return_value=[stubdata.ADSRECORDS['2015ApJ...815..133S'], stubdata.ADSRECORDS['2015ASPC..495..401C']]) \
                  as _:
            self.assertFalse(next_task.called)
            tasks.task_read_records([('bibcode', 'fingerprint')])
            self.assertTrue(next_task.called)
    
    
    def test_task_merge_metadata(self):
        self.maxDiff = None
        with patch('aip.tasks.task_output_results.delay', return_value=None) as next_task: 
            self.assertFalse(next_task.called)
            
            out = copy.deepcopy(stubdata.MERGEDRECS['2015ApJ...815..133S'])
            out['id'] = 1
            
            tasks.task_merge_metadata(stubdata.ADSRECORDS['2015ApJ...815..133S'])
            self.assertTrue(next_task.called)
            self.assertEqual(out, next_task.call_args_list[0][0][0])
        
    
    def test_task_output_results(self):
        with patch.object(self.app, 'update_processed_timestamp', return_value=None) as update_timestamp, \
            patch.object(self.app, 'forward_message', return_value=None) as next_task:
            
            self.assertFalse(next_task.called)
            tasks.task_output_results(stubdata.MERGEDRECS['2015ApJ...815..133S'])
            self.assertTrue(next_task.called)
            expected = stubdata.MERGEDRECS['2015ApJ...815..133S'].copy()
            expected.pop('read_count')
            expected.pop('citation_count')
            self.maxDiff = None
            self.assertDictEqual(next_task.call_args[0][0].toJSON(), expected)
            self.assertTrue(update_timestamp.called)
            
    

if __name__ == '__main__':
    unittest.main()