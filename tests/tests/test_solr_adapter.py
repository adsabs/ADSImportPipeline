# -*- coding: utf-8 -*-
import unittest

from aip.libs import solr_adapter
from tests.stubdata import stubdata


class TestSolrAdapter(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_SolrAdapter(self):
        r = solr_adapter.SolrAdapter.adapt(stubdata.INPUT_DOC)
        solr_adapter.SolrAdapter.validate(r) #Raises AssertionError if not validated
        self.assertEquals(r,stubdata.EXPECTED_SOLR_DOC)
    
        r = solr_adapter.SolrAdapter.adapt(stubdata.INPUT_DOC1)
        solr_adapter.SolrAdapter.validate(r) #Raises AssertionError if not validated
        self.assertEquals(r,stubdata.EXPECTED_SOLR_DOC1)
    
        r = solr_adapter.SolrAdapter.adapt(stubdata.INPUT_DOC2)
        solr_adapter.SolrAdapter.validate(r) #Raises AssertionError if not validated
        self.assertEquals(r,stubdata.EXPECTED_SOLR_DOC2)


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
            s, l = solr_adapter.bibstem_mapper(t['bibcode'])
            self.assertEquals([s,l],t['bibstems'])

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
