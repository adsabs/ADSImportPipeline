import sys
import os

from collections import OrderedDict
import mock
from mock import patch
from aip import tasks, app as app_module
from adsputils import get_date
from aip.models import Base
import unittest
from tests.stubdata import stubdata

class TestWorkers(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.proj_home = os.path.join(os.path.dirname(__file__), '../..')
        self._app = tasks.app
        self.app = app_module.create_app('test',
            {
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
                  [{'bibcode': 'foo', 'bib_data': {'JSON_fingerprint': 'bar'}},
                   {'bibcode': 'baz', 'bib_data': {'JSON_fingerprint': 'bard'}},
                         ]) as read_recs:
            
            
            self.assertFalse(next_task.called)
            tasks.task_find_new_records([('foo', 'bar'), 
                                       ('baz', 'bar'),
                                       ('hey', 'hoo')])
            self.assertTrue(next_task.called)
            self.assertEqual(next_task.call_count, 3)
            # notice the different order; first we index the differnet fingerprints, the last bibcode was missing...
            self.assertEqual(str(next_task.call_args_list), "[call('foo'), call('baz'), call('hey')]")


    def test_task_read_records(self):
        with patch('aip.tasks.task_merge_metadata.delay', return_value=None) as next_task, \
            patch('aip.libs.read_records.readRecordsFromADSExports', 
                  return_value=[stubdata.ADSRECORDS['2015ApJ...815..133S'], stubdata.ADSRECORDS['2015ASPC..495..401C']]) \
                  as _:
            self.assertFalse(next_task.called)
            tasks.task_read_records([('bibcode', 'fingerprint')])
            self.assertTrue(next_task.called)
    
    
    def test_task_merge_metadata(self):
        with patch('aip.tasks.task_output_results.delay', return_value=None) as next_task: 
            self.assertFalse(next_task.called)
            tasks.task_merge_metadata(stubdata.ADSRECORDS['2015ApJ...815..133S'])
            self.assertTrue(next_task.called)
            next_task.assert_called_with(stubdata.MERGEDRECS['2015ApJ...815..133S'])
        
    
    def test_task_output_results(self):
        with patch.object(self.app, 'update_processed_timestamp', return_value=None) as update_timestamp, \
            patch.object(tasks._forward_message, 'apply_async', return_value=None) as next_task:
            
            self.assertFalse(next_task.called)
            tasks.task_output_results(stubdata.MERGEDRECS['2015ApJ...815..133S'])
            self.assertTrue(next_task.called)
            self.assertEqual(next_task.call_args[0][0], (stubdata.MERGEDRECS['2015ApJ...815..133S']))
            self.assertTrue(update_timestamp.called)
        
    

if __name__ == '__main__':
    unittest.main()