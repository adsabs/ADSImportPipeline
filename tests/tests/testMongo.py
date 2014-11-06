import sys, os
PROJECT_HOME = os.path.abspath(os.path.join(os.path.dirname(__file__),'../../'))
sys.path.append(PROJECT_HOME)
from settings import MONGO
from lib import MongoConnection

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

  def tearDown(self):
    self.mongo.conn.drop_database(self.mongo.database)
    self.mongo.close()
