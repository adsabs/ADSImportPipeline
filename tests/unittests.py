#!/usr/bin/env python

import unittest

import sys,os
import time
import json
import logging
import pymongo
import cPickle as pickle

PROJECT_HOME = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
sys.path.append(PROJECT_HOME)
from settings import MONGO,CLASSIC_BIBCODES

from lib import SolrUpdater
from lib import MongoConnection
from lib import EnforceSchema
from lib import UpdateRecords
from lib import merger
from stubdata import stubdata

class TestADSExportsConnection(unittest.TestCase):
  def test_instantiation(self):
    try:
      from ads.ADSExports import ADSRecords
    except ImportError:
      sys.path.append('/proj/ads/soft/python/lib/site-packages')
      from ads.ADSExports import ADSRecords
      print "Warning: Fallback to explicit path declaration for import"
    self.adsRecords = ADSRecords('full','XML')
    self.assertIsInstance(self.adsRecords,ADSRecords)

class TestBibcodeFiles(unittest.TestCase):
  def setUp(self):
    self.content = []
    for filename in CLASSIC_BIBCODES.values()+[os.path.join(PROJECT_HOME,'tests','merge_test_cases.txt')]:
      with open(os.path.abspath(filename)) as fp:
        results = []
        for line in fp:
          if line and not line.startswith("#"):
            results.append( tuple(line.strip().split('\t')) )
      print "Read %(num_entries)s entires from %(filename)s" % {'num_entries':len(results),'filename':filename}
      self.content.append(results)

  def test_textContent(self):
    for content in self.content:
      for L in content:
        self.assertIsInstance(L,tuple)
        self.assertEqual(len(L),2) #The bibcode files are expected to have a <bibcode,note> per line
        self.assertEqual(len(L[0]),19) #Bibcodes should always have a fixed length of 19 characters

  def tearDown(self):
    del self.content

class TestMongo(unittest.TestCase):
  def setUp(self):
    MONGO['DATABASE'] = 'unittests_tmp'
    MONGO['COLLECTION'] = 'unittests_tmp'
    self.mongo = MongoConnection.PipelineMongoConnection(**MONGO)
    self.mongo.conn.drop_database(self.mongo.database)
    self.records = [
        ('test1','1'),
        ('test2','foo'),
        ('test3','3'),
      ]
    self.docs = [
        {
          'bibcode':'test1',
          'JSON_fingerprint':'1',
        },
        {
          'bibcode':'test2',
          'JSON_fingerprint':'2',
        },
      ]
    for d in self.docs:
      query = {'bibcode':d['bibcode']} 
      self.mongo.db[self.mongo.collection].update(query,d,upsert=True,w=1,multi=False)

  def test_instantiation(self):
    m = self.mongo
    self.assertTrue(m.host)
    self.assertTrue(m.port)
    self.assertTrue(m.database)
    self.assertTrue(m.collection)
    self.assertTrue(m.uri)
    self.assertIsInstance(m.logger, logging.Logger)
    self.assertIsInstance(m.conn, pymongo.mongo_client.MongoClient)

  def test_findNewRecords(self):
    results = self.mongo.findNewRecords(self.records)
    self.assertEqual(results,
      [
        ('test2','foo'),
        ('test3','3'),
      ])

  def tearDown(self):
    self.mongo.conn.drop_database(self.mongo.database)
    self.mongo.close()

class TestEnforceSchema(unittest.TestCase):
  def setUp(self):
    self.e = EnforceSchema.Enforcer()
    self.general = self.e._generalEnforcer(stubdata.GENERAL)
    self.properties = self.e._propertiesEnforcer(stubdata.PROPERTIES)
    self.references = self.e._referencesEnforcer(stubdata.REFERENCES)
    self.relations = self.e._relationsEnforcer(stubdata.RELATIONS)

  def test_enforceMetadataSchema(self):
    blocks = self.e.enforceMetadataSchema([stubdata.GENERAL,stubdata.PROPERTIES,stubdata.REFERENCES,stubdata.RELATIONS])
    self.assertIsInstance(blocks,list)
    self.assertEqual(blocks,[
      self.general,
      self.properties,
      self.references,
      self.relations,
    ])

  def test_generalEnforcer(self):
    #self.maxDiff=None
    self.assertEqual(self.general,stubdata.GENERAL_ENFORCED)

  def test_propertiesEnforcer(self):
    #self.maxDiff=None
    self.assertEqual(self.properties,stubdata.PROPERTIES_ENFORCED)

  def test_referencesEnforcer(self):
    #self.maxDiff=None
    self.assertEqual(self.references,stubdata.REFERENCES_ENFORCED)

  def test_relationsEnforcer(self):
    #self.maxDiff=None
    self.assertEqual(self.relations,stubdata.RELATIONS_ENFORCED)

class testMerger(unittest.TestCase):
  def setUp(self):
    self.records=stubdata.METADATA_BLOCKS
    self.merger = merger.Merger(self.records)
  def test_mergeRecords(self):  
    self.assertEqual(UpdateRecords.mergeRecords(self.records),self.records)
 
  def test_mergerlogic_takeAll(self):
    self.assertEqual(self.merger.takeAll('foo'),['bar','bar2'])

test_cases = (
  TestBibcodeFiles, 
  TestMongo, 
  #TestADSExportsConnection,
  TestEnforceSchema,
  #testMerger,
  )

if __name__ == '__main__':

  suite = unittest.TestSuite()
  for test_class in test_cases:
    tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
    suite.addTests(tests)
    print "Loaded", test_class

  unittest.TextTestRunner(verbosity=3).run(suite)
