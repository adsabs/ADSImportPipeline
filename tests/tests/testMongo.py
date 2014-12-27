import sys, os
PROJECT_HOME = os.path.abspath(os.path.join(os.path.dirname(__file__),'../../'))
sys.path.append(PROJECT_HOME)
from settings import MONGO
from lib import MongoConnection
import json
import pymongo
import logging

import unittest


class TestMongo(unittest.TestCase):
  def setUp(self):
    MONGO['DATABASE'] = 'unittests_tmp'
    MONGO['COLLECTION'] = 'unittests_tmp'
    MONGO['PORT'] = '27017'
    self.mongo = MongoConnection.PipelineMongoConnection(**MONGO)
    #self.mongo.conn.drop_database(self.mongo.database)
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
      d['_id'] = self.mongo._getNextSequence()
      self.mongo.db[self.mongo.collection].insert(d,w=1,multi=False)

  def test_upsertRecords(self):
    m = self.mongo
    records = [
      {
        'bibcode': 'test3',
        'metadata': {
          'relations': {
            'alternates': [
              {'content': 'test1'},
            ],
          },
        },
      },
      {
        'bibcode': 'test4',
        'metadata': {
          'relations': {
            'alternates': [
              {'content': None},
            ],
          },
        },
      },
      {
        'bibcode': 'test5',
        'metadata': {
          'relations': {
            'alternates': [],
          },
        },
      },
    ]
    m.upsertRecords(records)
    results = sorted(list(m.db[m.collection].find()),key=lambda k: k['bibcode'])
    self.assertEqual(results,[
      {u'_id': 2, u'bibcode': u'test2', u'JSON_fingerprint': u'2'}, 
      {u'_id': 1, u'bibcode': u'test3', u'metadata': {u'relations': {u'alternates': [{u'content': u'test1'}]}}}, 
      {u'_id': 3, u'bibcode': u'test4', u'metadata': {u'relations': {u'alternates': [{u'content': None}]}}}, 
      {u'_id': 4, u'bibcode': u'test5', u'metadata': {u'relations': {u'alternates': []}}}
    ])

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

  def test_remove(self):
    def alldocs():
      return list( self.mongo.db[self.mongo.collection].find() )
    self.mongo.remove()
    self.assertEqual(alldocs(),self.docs)

    self.mongo.remove(2)
    self.assertEqual([{
          u'_id': 1,
          u'bibcode':u'test1',
          u'JSON_fingerprint':u'1',
        }],alldocs())

    record = {
      u'_id':self.mongo._getNextSequence(),
      u'bibcode':u'test4',
      }
    self.mongo.db[self.mongo.collection].insert(record,w=1,multi=False)
    self.mongo.remove({'bibcode':'test1'})
    self.assertEqual(record,alldocs()[0])

    self.mongo.remove(force=True)
    self.assertEqual([],alldocs())


  def test_getRecordsFromBibcodes(self):
    results = self.mongo.getRecordsFromBibcodes([i[0] for i in self.records])
    self.assertEqual(results,self.docs)

  def test_getAllBibcodes(self):
    results = self.mongo.getAllBibcodes()
    self.assertEqual(results,[i['bibcode'] for i in self.docs])

  def test_getRecords_NotIn_Bibcodes(self):
    results = self.mongo.getRecordsFromBibcodes([i[0] for i in self.records],op="$nin")
    self.assertEqual(results,[])

    record = {
      u'_id':self.mongo._getNextSequence(),
      u'bibcode':u'test4',
      }
    bibcodes = [i['bibcode'] for i in self.docs]
    bibcodes.append(record['bibcode'])
    results = self.mongo.getRecordsFromBibcodes(bibcodes)
    results = [i['bibcode'] for i in results]
    self.assertEqual(json.dumps(list(set(bibcodes).difference(results))),json.dumps([record['bibcode']]))

    self.mongo.db[self.mongo.collection].insert(record,w=1,multi=False)
    results = self.mongo.getRecordsFromBibcodes([i[0] for i in self.records],op="$nin")
    self.assertEqual(results[0],record)

    results = self.mongo.getRecordsFromBibcodes([i[0] for i in self.records],op="$nin",iterate=True)
    self.assertEqual(results[0],record)

  def test_findIgnoredRecords(self):
    results = self.mongo.findNewRecords([
        ('test1','ignore'),
        ('test2','ignore'),
        ('test3','ignore'),
    ])

    self.assertEqual(results,
      [
        (u'test1',u'1'),
        (u'test2',u'2'),
        (u'test3',u'ignore'),
    ])    

  def tearDown(self):
    self.mongo.conn.drop_database(self.mongo.database)
    self.mongo.close()
