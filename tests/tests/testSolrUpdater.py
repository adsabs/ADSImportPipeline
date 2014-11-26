# -*- coding: utf-8 -*-
import unittest
import sys, os
PROJECT_HOME = os.path.abspath(os.path.join(os.path.dirname(__file__),'../../'))
sys.path.append(PROJECT_HOME)
sys.path.append(os.path.join(PROJECT_HOME,'tests'))

from lib import SolrUpdater
from stubdata import stubdata



class TestSolrAdapter(unittest.TestCase):
  def setUp(self):
    self.maxDiff = None

  def test_SolrAdapter(self):

    r = SolrUpdater.SolrAdapter.adapt(stubdata.INPUT_MONGO_DOC)
    SolrUpdater.SolrAdapter.validate(r) #Raises AssertionError if not validated
    self.assertEquals(r,stubdata.EXPECTED_SOLR_DOC)

    r = SolrUpdater.SolrAdapter.adapt(stubdata.INPUT_MONGO_DOC1)
    SolrUpdater.SolrAdapter.validate(r) #Raises AssertionError if not validated
    self.assertEquals(r,stubdata.EXPECTED_SOLR_DOC1)

    r = SolrUpdater.SolrAdapter.adapt(stubdata.INPUT_MONGO_DOC2)
    SolrUpdater.SolrAdapter.validate(r) #Raises AssertionError if not validated
    self.assertEquals(r,stubdata.EXPECTED_SOLR_DOC2)

  def tearDown(self):
    pass

if __name__ == '__main__':
    unittest.main()
