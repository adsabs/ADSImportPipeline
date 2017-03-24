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

  def xtest_SolrAdapter(self):

    r = SolrUpdater.SolrAdapter.adapt(stubdata.INPUT_MONGO_DOC)
    SolrUpdater.SolrAdapter.validate(r) #Raises AssertionError if not validated
    self.assertEquals(r,stubdata.EXPECTED_SOLR_DOC)

    r = SolrUpdater.SolrAdapter.adapt(stubdata.INPUT_MONGO_DOC1)
    SolrUpdater.SolrAdapter.validate(r) #Raises AssertionError if not validated
    self.assertEquals(r,stubdata.EXPECTED_SOLR_DOC1)

    r = SolrUpdater.SolrAdapter.adapt(stubdata.INPUT_MONGO_DOC2)
    SolrUpdater.SolrAdapter.validate(r) #Raises AssertionError if not validated
    self.assertEquals(r,stubdata.EXPECTED_SOLR_DOC2)

  def test_SolrAdapter(self):
    "combine mongo and sql input docs and verify correct Solr record created"
    x = stubdata.INPUT_MONGO_DOC.copy()
    x.update({'adsdata': stubdata.INPUT_SQL_SOLR_CHECK})
    z = SolrUpdater.SolrAdapter.adapt(x)
    self.assertEquals(z, stubdata.EXPECTED_SOLR_DOC)
    SolrUpdater.SolrAdapter.validate(z)

    x = stubdata.INPUT_MONGO_DOC1.copy()
    x.update({'adsdata': stubdata.INPUT_SQL_SOLR_CHECK1})
    z = SolrUpdater.SolrAdapter.adapt(x)
    self.assertEquals(z, stubdata.EXPECTED_SOLR_DOC1)
    SolrUpdater.SolrAdapter.validate(z)

    x = stubdata.INPUT_MONGO_DOC2.copy()
    x.update({'adsdata': stubdata.INPUT_SQL_SOLR_CHECK2})
    z = SolrUpdater.SolrAdapter.adapt(x)
    self.assertEquals(z, stubdata.EXPECTED_SOLR_DOC2)
    SolrUpdater.SolrAdapter.validate(z)


  def tearDown(self):
    pass


class TestBibstemMapper(unittest.TestCase):
  def setUp(self):
    pass

  def test_BibstemMapper(self):
    test_cases = [
      { 'bibcode': '2013MPEC....X...07.',
        'bibstems': [ 'MPEC.', 'MPEC.....' ] },
      { 'bibcode': '2000astro.ph.12401H',
        'bibstems': [ 'arXiv', 'arXiv....' ] },
      { 'bibcode': '1978ApJ...221L..29B',
        'bibstems': [ 'ApJL.', 'ApJL..221' ] },
      { 'bibcode': '2010ApJ...724.1099L',
        'bibstems': [ 'ApJ..', 'ApJ...724' ] },
      { 'bibcode': '2015rmtm.book...81D',
        'bibstems': [ 'rmtm.', 'rmtm.book' ] }
      ]
    for t in test_cases:
      s, l = SolrUpdater.bibstem_mapper(t['bibcode'])
      self.assertEquals([s,l],t['bibstems'])

  def tearDown(self):
    pass

if __name__ == '__main__':
    unittest.main()
