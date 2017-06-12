# -*- coding: utf-8 -*-
import unittest

import os
from tests.stubdata import stubdata
from aip import models, tasks, app as app_module
from aip.libs import utils
import json
import time
from aip.models import Base


class TestUpdateRecords(unittest.TestCase):

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

    def test_database(self):
        self.app.update_storage('foo', 'fingerprint')
        r = self.app.get_record('foo')
        self.assertEqual('foo', r['bibcode'])
        self.assertTrue(r['updated'] != None)
        self.assertTrue(r['processed'] == None)
        
        self.app.update_processed_timestamp('foo')
        r = self.app.get_record('foo')
        self.assertTrue(r['processed'] != None)

if __name__ == '__main__':
    unittest.main()
