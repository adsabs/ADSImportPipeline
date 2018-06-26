# -*- coding: utf-8 -*-

from aip import models, tasks, app as app_module
from aip.models import Base
from time import sleep
import os
import unittest


class TestUpdateRecords(unittest.TestCase):

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

    def test_database(self):
        self.app.update_storage('foo', fingerprint='fingerprint', origin='classic')
        r = self.app.get_record('foo')
        self.assertEqual('foo', r['bibcode'])
        self.assertEqual('classic', r['origin'])
        self.assertTrue(r['updated'] != None)
        self.assertTrue(r['processed'] == None)
        self.assertTrue(r['direct_created'] == None)
        
        self.app.update_processed_timestamp('foo')
        r = self.app.get_record('foo')
        self.assertTrue(r['processed'] != None)

        self.app.update_storage('bar', origin='direct')
        r = self.app.get_record('bar')
        self.assertEqual('direct', r['origin'])
        self.assertTrue(r['direct_created'] != None)
        self.assertTrue(r['direct_updated'] != None)
        self.assertEqual(r['direct_created'], r['direct_updated'])

        sleep(.1)
        self.app.update_storage('bar', origin='direct')
        r = self.app.get_record('bar')
        self.assertEqual('direct', r['origin'])
        self.assertTrue(r['direct_created'] != None)
        self.assertNotEqual(r['direct_created'], r['direct_updated'])
        
        
    def test_delete_record(self):
        self.app.update_storage('foo', fingerprint='fingerprint')
        self.app.delete_by_bibcode('foo')
        with self.app.session_scope() as session:
            r = session.query(models.ChangeLog).filter_by(key='deleted').first()
            self.assertEquals(r.oldvalue, 'foo')

    def test_direct_after_delete(self):
        """bibcode can not be added via direct ingest after it has been deleted"""
        r0 = self.app.update_storage('foo', origin='direct')
        self.assertIsNotNone(r0)
        r = self.app.get_record('foo')
        self.assertEqual('direct', r['origin'])
        sleep(.1)
        r1 = self.app.update_storage('foo', fingerprint='fingerprint',
                                     origin='classic')
        self.assertIsNotNone(r1)
        self.assertIsNotNone(r1['updated'])
        self.assertIsNotNone(r1['direct_updated'])
        self.assertNotEqual(r1['updated'], ['direct_updated'])
        r = self.app.get_record('foo')
        self.assertEqual('classic', r['origin'])
        
        self.app.delete_by_bibcode('foo')
        # after delete, it direct can not add it
        r2 = self.app.update_storage('foo', origin='direct')
        self.assertIsNone(r2)
        r = self.app.get_record('foo')
        self.assertIsNone(r)

    def test_compute_orphaned(self):
        self.app.update_storage('foo', fingerprint='fingerprint', origin='classic')
        self.app.update_storage('bar', origin='direct')
        canonical = set()
        canonical.add('foo')
        orphaned = self.app.compute_orphaned(canonical)
        print 'orphaned = ', orphaned
        self.assertEqual(0, len(orphaned))

        canonical = set()
        canonical.add('baz')
        orphaned = self.app.compute_orphaned(canonical)
        self.assertEqual(1, len(orphaned))
        self.assertTrue('foo' in orphaned)

    def test_compute_orphaned_larger(self):
        self.app.update_storage('foo', fingerprint='fingerprint', origin='classic')
        self.app.update_storage('bar', origin='direct')
        self.app.update_storage('bar2', origin='direct')
        self.app.update_storage('baz', fingerprint='fingerprint', origin='classic')
        self.app.update_storage('quux', fingerprint='fingerprint', origin='classic')
        self.app.update_storage('xyzzy', fingerprint='fingerprint', origin='classic')
        self.app.update_storage('spam', fingerprint='fingerprint', origin='classic')
        canonical = set()
        canonical.add('foo')
        canonical.add('spam')
        orphaned = self.app.compute_orphaned(canonical)
        self.assertEqual(3, len(orphaned))
        self.assertTrue('baz' in orphaned)
        self.assertTrue('quux' in orphaned)
        self.assertTrue('xyzzy' in orphaned)


if __name__ == '__main__':
    unittest.main()
