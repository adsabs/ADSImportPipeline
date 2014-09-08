# -*- coding: utf-8 -*-
import unittest
import sys, os
PROJECT_HOME = os.path.abspath(os.path.join(os.path.dirname(__file__),'../../'))
sys.path.append(PROJECT_HOME)
sys.path.append(os.path.join(PROJECT_HOME,'tests'))

from lib import UpdateRecords
from lib import merger
from stubdata import stubdata

class TestMerger(unittest.TestCase):

  def setUp(self):
    self.A1  = {'name': {'western': u'Accomazzi, Alberto'},   'affiliations': [u'ADS']}
    self.A2  = {'name': {'western': u'Accomazzi, A.'},        'affiliations': [u'CfA', u'SAO']}
    self.C1  = {'name': {'western': u'Grant, Carolyn S.'},    'affiliations': []}
    self.C2  = {'name': {'western': u'Stern Grant, C.'},      'affiliations': [u'Harvard']}
    self.M1  = {'name': {'western': u'Kurtz, Michael'},       'affiliations': []}
    self.M2  = {'name': {'western': u'Krüz, M. J.'},          'affiliations': [u'SAO']}

  # def test_mergeRecords(self):  
  #   self.assertEqual(UpdateRecords.mergeRecords(self.records),self.records)
 
  # def test_mergerlogic_takeAll(self):
  #   self.assertEqual(self.merger.takeAll('foo'),['bar','bar2'])
  def test_AuthorMerger(self):
    A1,A2,C1,C2,M1,M2 = self.A1,self.A2,self.C1,self.C2,self.M1,self.M2
    B1 = {'tempdata':{'origin':'ADS METADATA','type':'general'}}
    B2 = {'tempdata':{'origin':'ISI','type':'general'}}
    
    B1['authors'] = [A1,A2,C1,M2]
    B2['authors'] = [A2,A1,C2,M1]

    blocks = [B1,B2]
    m = merger.Merger(blocks)
    results = m.authorMerger()

    expectedResults = [
      A1,
      A2,
      {'name': {'western': u'Grant, Carolyn S.'}, 'affiliations': [u'Harvard']},
      M2,
    ]
    self.assertEqual(results,expectedResults)


if __name__ == '__main__':
    unittest.main()


