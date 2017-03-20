# -*- coding: utf-8 -*-
import unittest

from aip.libs import update_records
from tests.stubdata import stubdata
from aip import db, models
from aip.libs import utils
import json
import time


class TestUpdateRecords(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        db.init_app({
            'SQLALCHEMY_URL': 'sqlite:///',
            'SQLALCHEMY_ECHO': False
        })
        models.Base.metadata.bind = db.session.get_bind()
        models.Base.metadata.create_all()

    def tearDown(self):
        models.Base.metadata.drop_all()
        db.close_app()
        unittest.TestCase.tearDown(self)

    
    def test_crate_records(self):
        now = utils.get_date()
        last_time = utils.get_date()
        for k in ['bib_data', 'nonbib_data', 'orcid_claims']:
            update_records.update_storage('abc', k, stubdata.EXPECTED_SOLR_DOC)
            with db.session_scope() as session:
                r = session.query(models.Records).filter_by(bibcode='abc').first()
                self.assertTrue(r.id == 1)
                j = r.toJSON()
                self.assertEquals(j[k], stubdata.EXPECTED_SOLR_DOC)
                t = j[k + '_updated']
                self.assertTrue(now < t)
                self.assertTrue(last_time < j['updated'])
                last_time = j['updated']
        
        update_records.update_storage('abc', 'fulltext', 'foo bar')
        with db.session_scope() as session:
            r = session.query(models.Records).filter_by(bibcode='abc').first()
            self.assertTrue(r.id == 1)
            j = r.toJSON()
            self.assertEquals(j['fulltext'], u'foo bar')
            t = j['fulltext_updated']
            self.assertTrue(now < t)
        
        r = update_records.get_record('abc')
        self.assertEquals(r['id'], 1)
        self.assertEquals(r['processed'], None)
        
        r = update_records.get_record(['abc'])
        self.assertEquals(r[0]['id'], 1)
        self.assertEquals(r[0]['processed'], None)
        
        r = update_records.get_record('abc', load_only=['id'])
        self.assertEquals(r['id'], 1)
        self.assertFalse('processed' in r)
        
        update_records.update_processed_timestamp('abc')
        r = update_records.get_record('abc')
        self.assertTrue(r['processed'] > now)

if __name__ == '__main__':
    unittest.main()
