import sys, os

PROJECT_HOME = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(PROJECT_HOME)
from settings import SQL_ADSDATA
from lib import SqlConnection
from stubdata import stubdata
import json
import pymongo
import logging

import unittest


class TestSql(unittest.TestCase):
    """due to an improper file name, these tests are not currently found
    
    these sqlite tests will not run because arrays are not supported.
    the tests should be changed to use an external Postgres instance"""

    def setUp(self):
        SQL_ADSDATA['DATABASE'] = 'unittests_'
        SQL_ADSDATA['SCHEMA'] = ''
        self.sql = SqlConnection.PipelineSqlConnection(**SQL_ADSDATA)

        self.records = stubdata.INPUT_SQL_DOC
        row_view = self.sql.get_row_view_table()
        self.sql.meta.create_all(self.sql.engine)
        ins = row_view.insert()
        self.sql.conn.execute(ins, self.records)

    def test_getRecordsFromBibcodes(self):
        results = self.sql.getRecordsFromBibcodes('doesNotExist')
        self.assertEquals(len(results), 0, "non-existent bibcode check")

        results = self.sql.getRecordsFromBibcodes(self.records[0].get('bibcode'))
        self.assertEqual(1, len(results), 'single bibcode length check')
        self.assertEqual(self.records[0].get('bibcode'), results[0].bibcode, 'single bibcode check')

        bibcodes = [x.get('bibcode') for x in self.records[:-1]]
        results = self.sql.getRecordsFromBibcodes(bibcodes)
        bibcodes_results = [x.bibcode for x in results]
        self.assertEqual(len(self.records) - 1, len(results), 'multiple bibcode query length check')
        for bibcode in bibcodes:
            self.assertTrue(bibcode in bibcodes_results, 'multiple bibcode query present check')

        bibcodes = [x.get('bibcode') for x in self.records]
        results = self.sql.getRecordsFromBibcodes(bibcodes)
        bibcodes_results = [x.bibcode for x in results]
        self.assertEqual(len(self.records), len(results), 'multiple bibcode query length check')
        for bibcode in bibcodes:
            self.assertTrue(bibcode in bibcodes_results, 'multiple bibcode query present check')

    def test_getAllBibcodes(self):
        results = self.sql.getAllBibcodes()
        self.assertEqual(len(self.records), len(results), 'get all bibcodes check')


    def test_getRecords_NotIn_Bibcodes(self):

        bibcodes = [x.get('bibcode') for x in self.records]
        results = self.sql.getRecordsFromBibcodes(bibcodes, op='$nin')
        self.assertEqual(0, len(results), 'bibcodes not in list check, all bibcodes excluded')

        first_bibcode = self.records[0].get('bibcode')
        results = self.sql.getRecordsFromBibcodes(first_bibcode, op='$nin')
        bibcodes_results = [x.bibcode for x in results]
        self.assertTrue(first_bibcode not in bibcodes_results,
                        'bibcodes not in list check, one bibcode excluded')
        self.assertEqual(len(bibcodes_results), len(self.records) - 1,
                         'bibcodes not in list check, one bibcode excluded')

        second_bibcode = self.records[1].get('bibcode')
        results = self.sql.getRecordsFromBibcodes([first_bibcode, second_bibcode], op='$nin')
        bibcodes_results = [x.bibcode for x in results]
        self.assertTrue(first_bibcode not in bibcodes_results,
                        'bibcodes not in list check, two bibcodes excluded')
        self.assertTrue(second_bibcode not in bibcodes_results,
                        'bibcodes not in list check, two bibcodes excluded')
        self.assertEqual(len(bibcodes_results), len(self.records) - 2,
                         'bibcodes not in list check, two bibcodes excluded')

    def test_invalidOpParameter(self):
        with self.assertRaises(ValueError):
            results = self.sql.getRecordsFromBibcodes('doesNotMatter', op='$badValue')

    def tearDown(self):
        row_table = self.sql.get_row_view_table()
        self.sql.close()
        row_table.drop(self.sql.engine)
