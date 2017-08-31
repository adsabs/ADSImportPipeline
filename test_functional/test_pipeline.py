"""
Functional test

Loads the ADSOrcid workers. It then injects input onto the first worker and 
traces what they do. 

"""

import unittest
import time
import json
from aip import models, tasks




class TestPipeline(unittest.TestCase):
    """
    Class for testing the overall functionality of the import pipeline.
    The interaction between the pipeline workers.
    
    Make sure you have the correct values set in the local_config.py
    These tests will use that config! At mininum:
    
        SQLALCHEMY_URL = 'sqlite:////tmp/test.db'
        CELERY_BROKER = 'pyamqp://guest:guest@localhost:6672/ads_orcid'
        API_TOKEN = '.......'
    """
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.app = tasks.app
    
    
    def tearDown(self):
        unittest.TestCase.tearDown(self)
    

    def test_functionality_on_new_claim(self):
        """
        Main test, it pretends we have received claims from the 
        ADSWS
        
        For this, you need to have 'db' and 'rabbitmq' containers running.
        :return: no return
        """
        
        # clean the slate (production: 0000-0003-3041-2092, staging: 0000-0001-8178-9506) 
        with self.app.session_scope() as session:
            session.query(models.AuthorInfo).filter_by(orcidid='0000-0003-3041-2092').delete()
            session.query(models.ClaimsLog).filter_by(orcidid='0000-0003-3041-2092').delete()
            session.query(models.Records).filter_by(bibcode='2015ASPC..495..401C').delete()
            kv = session.query(models.KeyValue).filter_by(key='last.check').first()
            if kv is None:
                kv = models.KeyValue(key='last.check')
            kv.value = '2051-11-09T22:56:52.518001Z'
                
        
        # send a test claim
        tasks.task_find_new_records(tasks.task_find_new_records([
                                       ('hey', 'fp_hoo'),
                                       ]))
        
        time.sleep(2)
        
        # check results
        with self.app.session_scope() as session:
            r = session.query(models.Records).filter_by(bibcode='2015ASPC..495..401C').first()
            self.assertEquals(json.loads(r.claims)['verified'],
                              ['0000-0003-3041-2092', '-','-','-','-','-','-','-','-','-', ] 
                              )
            

if __name__ == '__main__':
    unittest.main()