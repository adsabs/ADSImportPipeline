# -*- coding: utf-8 -*-
import unittest

from aip.libs import solr_updater
from tests.stubdata import stubdata


class TestSolrAdapter(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_SolrAdapter(self):
        r = solr_updater.SolrAdapter.adapt(stubdata.INPUT_DOC)
        solr_updater.SolrAdapter.validate(r) #Raises AssertionError if not validated
        self.assertEquals(r,stubdata.EXPECTED_SOLR_DOC)
    
        r = solr_updater.SolrAdapter.adapt(stubdata.INPUT_DOC1)
        solr_updater.SolrAdapter.validate(r) #Raises AssertionError if not validated
        self.assertEquals(r,stubdata.EXPECTED_SOLR_DOC1)
    
        r = solr_updater.SolrAdapter.adapt(stubdata.INPUT_DOC2)
        solr_updater.SolrAdapter.validate(r) #Raises AssertionError if not validated
        self.assertEquals(r,stubdata.EXPECTED_SOLR_DOC2)


    def test_transform_json_record(self):
        rec = {
            'id': 1,
            'bibcode': 'abc',
            'bib_data': stubdata.EXPECTED_SOLR_DOC,
            'nonbib_data': {'foo': 'bar'},
            'fulltext': "This is a fooltext",
            'orcid_claims': {
                    'other': ['0000', '0000', '-'],
                    'verified': ['-', 'orcid', '-']
                }
        }
        out = solr_updater.transform_json_record(rec)
        self.assertEqual(out, {
             'abstract': u"all no-skysurvey q'i quotient",
             'adsdata': {'foo': 'bar'},
             'aff': [u'-',
                  u'NASA Kavli space center, Cambridge, MA 02138, USA',
                  u'Einsteininstitute, Zurych, Switzerland'],
             'alternate_title': [u'This is of the alternate'],
             'author': [u"t'Hooft, van X", u'Anders, John Michael', u'Einstein, A'],
             'author_facet': [u'T Hooft, V', u'Anders, J M', u'Einstein, A'],
             'author_facet_hier': [u'0/T Hooft, V',
                  u"1/T Hooft, V/t'Hooft, van X",
                  u'0/Anders, J M',
                  u'1/Anders, J M/Anders, John Michael',
                  u'0/Einstein, A',
                  u'1/Einstein, A/Einstein, A'],
             'author_norm': [u'T Hooft, V', u'Anders, J M', u'Einstein, A'],
             'bibcode': u'testbibcode',
             'bibgroup': [u'Cfa'],
             'bibgroup_facet': [u'Cfa'],
             'bibstem': [u'bibco', u'bibcode'],
             'bibstem_facet': u'bibcode',
             'body': 'This is a fooltext',
             'citation': [u'2014JNuM..455...10C', u'2014JNuM..455...10D'],
             'citation_count': 2,
             'cite_read_boost': 0.52,
             'classic_factor': 5002,
             'database': [u'astronomy', u'physics'],
             'date': u'2013-08-05T00:30:00.000000Z',
                u'doctype': u'catalog',
             'doi': [u'doi:\xc5\xbd\xc5\xa0\xc4\x8c\xc5\x98\xc4\x8e\xc5\xa4\xc5\x87:123456789'],
             'email': [u'-', u'anders@email.com', u'-'],
             'first_author': u"t'Hooft, van X",
             'first_author_facet_hier': [u'0/T Hooft, V', u"1/T Hooft, V/t'Hooft, van X"],
             'first_author_norm': u'T Hooft, V',
             'grant': [u'NASA', u'123456-78', u'NSF-AST', u'0618398'],
             'grant_facet_hier': [u'0/NASA',
                  u'1/NASA/123456-78',
                  u'0/NSF-AST',
                  u'1/NSF-AST/0618398'],
             'id': 1,
             'identifier': [u'arxiv:1234.5678',
                  u'doi:\xc5\xbd\xc5\xa0\xc4\x8c\xc5\x98\xc4\x8e\xc5\xa4\xc5\x87:123456789',
                  u'ARXIV:hep-ph/1234'],
             'issue': u'24i',
             'keyword': [u'Classical Statistical mechanics'],
             'keyword_facet': [u'stat mech'],
             'keyword_norm': [u'stat mech'],
             'keyword_schema': [u'PACS Codes'],
             'links_data': [u'{"title":"", "type":"ned", "instances":"78", "access":"", "url":"http://$NED$/cgi-bin/nph-objsearch?search_type=Search&refcode=2013A%26A...552A.143S"}',
                  u'{"title":"", "type":"postscript", "instances":"", "access":"open", "url":"http://www.aanda.org/10.1051/0004-6361/201321247/postscript"}',
                  u'{"title":"", "type":"electr", "instances":"", "access":"open", "url":"http://dx.doi.org/10.1051%2F0004-6361%2F201321247"}',
                  u'{"title":"", "type":"simbad", "instances":"74", "access":"", "url":"http://$SIMBAD$/simbo.pl?bibcode=2013A%26A...552A.143S"}',
                  u'{"title":"", "type":"pdf", "instances":"", "access":"open", "url":"http://www.aanda.org/10.1051/0004-6361/201321247/pdf"}'],
             'orcid_claims': {'other': ['0000', '0000', '-'],
              'verified': ['-', 'orcid', '-']},
             'orcid_pub': [u'-', u'-', u'-'],
             'page': [u'2056-2078'],
             'property': [u'OPENACCESS',
                  u'OCRABSTRACT',
                  u'ADS_OPENACCESS',
                  u'NONARTICLE',
                  u'NOT REFEREED'],
             'pubdate': u'2013-08-05',
             'read_count': 2,
             'reader': [u'abaesrwersdlfkjsd', u'asfasdflkjsdfsldj'],
             'reference': [u'2014JNuM..455...10R'],
             'simbad_object_facet_hier': [u'0/Other',
                  u'1/Other/5',
                  u'0/Other',
                  u'1/Other/3000001'],
             'simbid': [5, 3000001],
             'simbtype': [u'Other'],
             'title': [u'This is of the title', u'This is of the alternate'],
             'volume': u'l24'
        })
        


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
            s, l = solr_updater.bibstem_mapper(t['bibcode'])
            self.assertEquals([s,l],t['bibstems'])

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
