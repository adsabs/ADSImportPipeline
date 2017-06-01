import sys
import os

from collections import OrderedDict
import mock
from mock import patch
from aip import app
from aip.libs.utils import get_date
import unittest
from tests.stubdata import stubdata

class TestWorkers(unittest.TestCase):
    

    @patch('aip.app.task_read_records.delay', return_value=None)
    @patch('aip.libs.update_records.get_record', 
           return_value=[{'bibcode': 'foo', 'bib_data': {'JSON_fingerprint': 'bar'}},
                         {'bibcode': 'baz', 'bib_data': {'JSON_fingerprint': 'bard'}},
                         ])
    def test_task_find_new_records(self, read_recs, next_task, *args):
        self.assertFalse(next_task.called)
        app.task_find_new_records([('foo', 'bar'), 
                                   ('baz', 'bar'),
                                   ('hey', 'hoo')])
        self.assertTrue(next_task.called)
        self.assertEqual(next_task.call_count, 2)
        self.assertEqual(str(next_task.call_args_list), "[call('baz'), call('hey')]")


    @patch('aip.app.task_merge_metadata.delay', return_value=None)
    @patch('aip.libs.read_records.readRecordsFromADSExports', 
           return_value=[stubdata.ADSRECORDS['2015ApJ...815..133S'], stubdata.ADSRECORDS['2015ASPC..495..401C']])
    def test_task_read_records(self, read_recs, next_task, *args):
        self.assertFalse(next_task.called)
        app.task_read_records([('bibcode', 'fingerprint')])
        self.assertTrue(next_task.called)
    
    
    @patch('aip.app.task_update_record.delay', return_value=None)
    def test_task_merge_metadata(self, next_task, *args):
        self.assertFalse(next_task.called)
        app.task_merge_metadata(stubdata.ADSRECORDS['2015ApJ...815..133S'])
        self.assertTrue(next_task.called)
        next_task.assert_called_with(u'2015ApJ...815..133S', u'metadata', stubdata.MERGEDRECS['2015ApJ...815..133S'])
        
    
    @patch('aip.libs.update_records.update_storage', return_value=None)
    @patch('aip.app.task_update_solr.delay', return_value=None)
    def test_task_update_record(self, next_task, update_storage, *args):
        self.assertFalse(next_task.called)
        app.task_update_record('2015ApJ...815..133S', 'metadata', stubdata.MERGEDRECS['2015ApJ...815..133S'])
        self.assertTrue(next_task.called)
        self.assertTrue(update_storage.called)
        
    
    @patch('aip.libs.update_records.update_processed_timestamp', return_value=None)
    @patch('aip.libs.solr_updater.update_solr', return_value=None)
    @patch('aip.libs.update_records.get_record', return_value={'bib_data_updated': get_date(),
                                                               'nonbib_data_updated': get_date(),
                                                               'orcid_claims_updated': get_date(),
                                                               'processed': get_date('2012'),})
    @patch('aip.app.task_update_solr.apply_async', return_value=None)
    def test_task_update_solr(self, apply_async, get_record, update_solr, update_timestamp):
        self.assertFalse(update_solr.called)
        app.task_update_solr('2015ApJ...815..133S')
        self.assertTrue(update_solr.called)
        self.assertTrue(update_timestamp.called)
        
    
    @patch('aip.libs.update_records.update_processed_timestamp', return_value=None)
    @patch('aip.libs.solr_updater.update_solr', return_value=None)
    @patch('aip.libs.update_records.get_record', return_value={'bib_data_updated': get_date(),
                                                               'nonbib_data_updated': get_date(),
                                                               'orcid_claims_updated': get_date(),
                                                               'processed': get_date('2025'),})
    @patch('aip.app.task_update_solr.apply_async', return_value=None)
    def test_task_update_solr2(self, apply_async, get_record, update_solr, update_timestamp):
        self.assertFalse(update_solr.called)
        app.task_update_solr('2015ApJ...815..133S')
        self.assertFalse(update_solr.called)
        self.assertFalse(update_timestamp.called)
        

    
    @patch('aip.libs.update_records.update_processed_timestamp', return_value=None)
    @patch('aip.libs.solr_updater.update_solr', return_value=None)
    @patch('aip.libs.update_records.get_record', return_value={'bib_data_updated': get_date(),
                                                               'nonbib_data_updated': get_date(),
                                                               'orcid_claims_updated': get_date(),
                                                               'processed': get_date('2025'),})
    @patch('aip.app.task_update_solr.apply_async', return_value=None)
    def test_task_update_solr3(self, apply_async, get_record, update_solr, update_timestamp):
        self.assertFalse(update_solr.called)
        app.task_update_solr('2015ApJ...815..133S', force=True)
        self.assertTrue(update_solr.called)
        self.assertTrue(update_timestamp.called)

    
    @patch('aip.libs.update_records.update_processed_timestamp', return_value=None)
    @patch('aip.libs.solr_updater.update_solr', return_value=None)
    @patch('aip.libs.update_records.get_record', return_value={'bib_data_updated': None,
                                                               'nonbib_data_updated': get_date(),
                                                               'orcid_claims_updated': get_date(),
                                                               'processed': None,})
    @patch('aip.app.task_update_solr.apply_async', return_value=None)
    def test_task_update_solr4(self, apply_async, get_record, update_solr, update_timestamp):
        self.assertFalse(update_solr.called)
        app.task_update_solr('2015ApJ...815..133S')
        self.assertFalse(update_solr.called)
        self.assertFalse(update_timestamp.called)
        self.assertTrue(apply_async.called)
        
    
    @patch('aip.libs.update_records.update_processed_timestamp', return_value=None)
    @patch('aip.libs.solr_updater.update_solr', return_value=None)
    @patch('aip.libs.update_records.get_record', return_value={'bib_data_updated': None,
                                                               'nonbib_data_updated': get_date(),
                                                               'orcid_claims_updated': get_date(),
                                                               'processed': None,})
    @patch('aip.app.task_update_solr.apply_async', return_value=None)
    def test_task_update_solr5(self, apply_async, get_record, update_solr, update_timestamp):
        self.assertFalse(update_solr.called)
        app.task_update_solr('2015ApJ...815..133S', force=True, delayed=2)
        self.assertFalse(update_solr.called)
        self.assertFalse(update_timestamp.called)
        self.assertTrue(apply_async.called)
        apply_async.assert_called_with(('2015ApJ...815..133S', 3), countdown=100.0)
        
    
    @patch('aip.libs.update_records.update_processed_timestamp', return_value=None)
    @patch('aip.libs.solr_updater.update_solr', return_value=None)
    @patch('aip.libs.update_records.get_record', return_value={'bib_data_updated': get_date(),
                                                               'nonbib_data_updated': None,
                                                               'orcid_claims_updated': get_date(),
                                                               'processed': None,})
    @patch('aip.app.task_update_solr.apply_async', return_value=None)
    def test_task_update_solr6(self, apply_async, get_record, update_solr, update_timestamp):
        self.assertFalse(update_solr.called)
        app.task_update_solr('2015ApJ...815..133S', force=True)
        self.assertTrue(update_solr.called)
        self.assertTrue(update_timestamp.called)
        self.assertFalse(apply_async.called)
