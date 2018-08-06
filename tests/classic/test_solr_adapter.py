# -*- coding: utf-8 -*-
import unittest

from aip.classic import solr_adapter
from tests.stubdata import ADSRECORDS


class TestSolrAdapter(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_SolrAdapter(self):
        r = solr_adapter.SolrAdapter.adapt(ADSRECORDS['testbibcode'])
        solr_adapter.SolrAdapter.validate(r) #Raises AssertionError if not validated
        self.assertEquals(r, {'abstract': u"all no-skysurvey q'i quotient",
         'aff': [u'-',
          u'NASA Kavli space center, Cambridge, MA 02138, USA',
          u'Einsteininstitute, Zurych, Switzerland'],
         'alternate_title': [u'This is of the alternate'],
         'author': [u"t'Hooft, van X", u'Anders, John Michael', u'Einstein, A'],
         'author_count': 3,
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
         'database': [u'astronomy', u'physics'],
         'date': u'2013-08-05T00:30:00.000000Z',
         'doctype': u'catalog',
         'doctype_facet_hier': [u'0/Non-Article', u'1/Non-Article/Catalog'],
         'doi': [u'doi:\xc5\xbd\xc5\xa0\xc4\x8c\xc5\x98\xc4\x8e\xc5\xa4\xc5\x87:123456789'],
         'email': [u'-', u'anders@email.com', u'-'],
         'entry_date': '2003-03-21T00:00:00.000000Z',
         'first_author': u"t'Hooft, van X",
         'first_author_facet_hier': [u'0/T Hooft, V', u"1/T Hooft, V/t'Hooft, van X"],
         'first_author_norm': u'T Hooft, V',
         'id': 99999999,
         'identifier': [u'arxiv:1234.5678',
          u'doi:\xc5\xbd\xc5\xa0\xc4\x8c\xc5\x98\xc4\x8e\xc5\xa4\xc5\x87:123456789',
          u'ARXIV:hep-ph/1234'],
         'issue': u'24i',
         'keyword': [u'Classical Statistical mechanics'],
         'keyword_facet': [u'stat mech'],
         'keyword_norm': [u'stat mech'],
         'keyword_schema': [u'PACS Codes'],
         'links_data': [u'{"access": "", "instances": "78", "title": "", "type": "ned", "url": "http://$NED$/cgi-bin/nph-objsearch?search_type=Search&refcode=2013A%26A...552A.143S"}',
          u'{"access": "open", "instances": "", "title": "", "type": "postscript", "url": "http://www.aanda.org/10.1051/0004-6361/201321247/postscript"}',
          u'{"access": "open", "instances": "", "title": "", "type": "electr", "url": "http://dx.doi.org/10.1051%2F0004-6361%2F201321247"}',
          u'{"access": "", "instances": "74", "title": "", "type": "simbad", "url": "http://$SIMBAD$/simbo.pl?bibcode=2013A%26A...552A.143S"}',
          u'{"access": "open", "instances": "", "title": "", "type": "pdf", "url": "http://www.aanda.org/10.1051/0004-6361/201321247/pdf"}'],
         'orcid_pub': [u'-', u'-', u'-'],
         'page': [u'2056-2078'],
         'page_count': 0,
         'property': [u'OPENACCESS',
          u'OCRABSTRACT',
          u'ADS_OPENACCESS',
          u'NONARTICLE',
          u'NOT REFEREED'],
         'pubdate': u'2013-08-05',
         'title': [u'This is of the title', u'This is of the alternate'],
         'volume': u'l24'})
    
        r = solr_adapter.SolrAdapter.adapt(ADSRECORDS['testbibcode2'])
        solr_adapter.SolrAdapter.validate(r) #Raises AssertionError if not validated
        self.assertEquals(r, {
            "first_author": u"Kurtz, Michael J.",
        #    "links_data": [u"{\"title\":\"\",\"type\":\"spires\",\"instances\":\"\"}", "{\"title\":\"\",\"type\":\"electr\",\"instances\":\"\"}", "{\"title\":\"\",\"type\":\"spires\",\"instances\":\"\"}"],
            "entry_date": '2003-03-21T00:00:00.000000Z', 
            "first_author_norm": u"Kurtz, M", 
            "year": u"2000", 
            "bibcode": u"2000A&AS..143...41K_test", 
            "author_facet_hier": [
                u"0/Kurtz, M", u"1/Kurtz, M/Kurtz, Michael J",
                u"0/Eichhorn, G", u"1/Eichhorn, G/Eichhorn, Guenther", 
                u"0/Accomazzi, A", u"1/Accomazzi, A/Accomazzi, Alberto", 
                u"0/Grant, C", u"1/Grant, C/Grant, Carolyn S", 
                u"0/Murray, S", u"1/Murray, S/Murray, Stephen S",
                u"0/Watson, J", u"1/Watson, J/Watson, Joyce M"], 
            "bibstem": [u"A&AS", u"A&AS..143"], 
            "aff": [
                u"Harvard-Smithsonian Center for Astrophysics, Cambridge, MA 02138, USA", 
                u"Harvard-Smithsonian Center for Astrophysics, Cambridge, MA 02138, USA", 
                u"Harvard-Smithsonian Center for Astrophysics, Cambridge, MA 02138, USA", 
                u"Harvard-Smithsonian Center for Astrophysics, Cambridge, MA 02138, USA",
                u"Harvard-Smithsonian Center for Astrophysics, Cambridge, MA 02138, USA", 
                u"Harvard-Smithsonian Center for Astrophysics, Cambridge, MA 02138, USA"], 
            "keyword": [u"METHODS: DATA ANALYSIS", 
                        u"ASTRONOMICAL DATABASES: MISCELLANEOUS", 
                        u"PUBLICATIONS: BIBLIOGRAPHY", 
                        u"SOCIOLOGY OF ASTRONOMY", 
                        u"Astrophysics"], 
            "keyword_norm": [u"methods data analysis", u"-", u"-", u"-",
                             u"astrophysics"], 
            "keyword_schema": [u"Astronomy", u"Astronomy",
                               u"Astronomy", u"Astronomy", u"arXiv"], 
            "keyword_facet": [u"methods data analysis",
                              u"astrophysics"], 
            "email": [u"-", u"-", u"-", u"-", u"-", u"-"],
            "orcid_pub": [u"-", u"-", u"0000-0002-4110-3511", u"-", u"-", u"-"],
            "arxiv_class": [u"Astrophysics"], 
            "bibgroup": [u"CfA"],
            "bibgroup_facet": [u"CfA"],
            "author_facet": [u"Kurtz, M", u"Eichhorn, G",
                             u"Accomazzi, A", u"Grant, C", u"Murray, S", u"Watson, J"],
            "bibstem_facet": u"A&AS", 
            "pub": u"Astronomy and Astrophysics Supplement Series", 
            "volume": u"143", 
            "doi": [u"10.1051/aas:2000170"],
            "eid": u"here is the eid",
            "author_norm": [u"Kurtz, M", u"Eichhorn, G", u"Accomazzi, A", u"Grant, C",
                            u"Murray, S", u"Watson, J"], 
            "date": u"2000-04-01T00:00:00.000000Z",
            "pubdate": u"2000-04-00", 
            "id": 99999998,
            "identifier": [u"10.1051/aas:2000170"],
            "database": [u"astronomy"], 
            "author":
                [u"Kurtz, Michael J.", u"Eichhorn, Guenther", u"Accomazzi, Alberto",
                 u"Grant, Carolyn S.", u"Murray, Stephen S.", u"Watson, Joyce M."],
            "author_count": 6,
            "pub_raw": u"Astronomy and Astrophysics Supplement, v.143, p.41-59", 
        #    "cite_read_boost": 0.45,
            "first_author_facet_hier": [u"0/Kurtz, M", u"1/Kurtz, M/Kurtz, Michael J"], 
            "title": [u"The NASA Astrophysics Data System: Overview"],
            "property": [u"REFEREED", u"ARTICLE"], 
            "page": [u"41",u"here is the eid"],
            "page_count": 19,
            "page_range": u'41-59',
            'vizier':[u'tab1',u'tab2'],
            'vizier_facet':[u'tab1',u'tab2'],
            'doctype': u'article',
            'doctype_facet_hier': [u'0/Article', u'1/Article/Journal Article'],
            'pubnote': [u'19 pages, 22 figures; Astron.Astrophys.Suppl.Ser. 143 (2000) 41-59; doi:10.1051/aas:2000170']
        })
    
        r = solr_adapter.SolrAdapter.adapt({
            "id" : 99999997,
            "modtime" : '2014-06-18T21:06:49',
            'bibcode' : u'2014arXiv1406.4542H',
            "text": {},
            "entry_date": "2003-02-21",
            "metadata" : {
                "references": [],
                'properties': {'refereed': False, 'openaccess': True, 
                               'doctype': {'content': u'article', 'origin': u'ADS metadata'}, 
                               'private': False, 'ocrabstract': False, 'ads_openaccess':False,
                               'eprint_openaccess': True, 'pub_openaccess': False
                           },
                "relations": {},
                "general" : {
                    "publication" : {
                        "origin" : u"ARXIV",
                        'dates' : [
                            {
                                'type' : u'date-preprint',
                                'content' : u'2014-06-00'
                                }
                            ]
                        },
                    'authors': [
                        {'name': {'normalized': u'T Hooft, V', 'western': u"t'Hooft, van X", 'native': ''}, 
                         'number': u'1', 'affiliations': [], 'orcid': '', 'type': 'regular', 'emails': []},
                        {'name': {'normalized': u'Anders, J M', 'western': u'Anders, John Michael', 'native': ''}, 
                         'number': u'2', 'affiliations': [u'NASA Kavli space center, Cambridge, MA 02138, USA'], 
                         'orcid': '', 'type': 'regular', 'emails': [u'anders@email.com']},
                        {'name': {'normalized': u'Einstein, A', 'western': u'Einstein, A', 'native': ''}, 
                         'number': u'3', 'affiliations': [u'Einsteininstitute, Zurych, Switzerland'], 
                         'orcid': '', 'type': 'regular', 'emails': []}],
                    }
                },
            'orcid_claims': {'verified': [u'-', u'1111-2222-3333-4444', u'-']}
            })
        solr_adapter.SolrAdapter.validate(r) #Raises AssertionError if not validated
        self.assertEquals(r, {
            "id" : 99999997,
            'bibcode' : u'2014arXiv1406.4542H',
            'date':     u'2014-06-01T00:00:00.000000Z',
            'bibstem': [u'arXiv', u'arXiv1406'],
            'bibstem_facet': u'arXiv',
            'entry_date': '2003-02-21T00:00:00.000000Z',
            'pubdate' : u'2014-06-00',
            "property": [u"OPENACCESS", u"EPRINT_OPENACCESS", u"ARTICLE", u"NOT REFEREED"],
            'doctype': u'article',

            'aff': [u'-',
                  u'NASA Kavli space center, Cambridge, MA 02138, USA',
                  u'Einsteininstitute, Zurych, Switzerland'],
           'author': [u"t'Hooft, van X", u'Anders, John Michael', u'Einstein, A'],
           'author_facet': [u'T Hooft, V', u'Anders, J M', u'Einstein, A'],
           'author_facet_hier': [u'0/T Hooft, V',
                                 u"1/T Hooft, V/t'Hooft, van X",
                                 u'0/Anders, J M',
                                 u'1/Anders, J M/Anders, John Michael',
                                 u'0/Einstein, A',
                                 u'1/Einstein, A/Einstein, A'],
           'author_norm': [u'T Hooft, V', u'Anders, J M', u'Einstein, A'],
            'email': [u'-', u'anders@email.com', u'-'],
            'first_author': u"t'Hooft, van X",
            'first_author_facet_hier': [u'0/T Hooft, V', u"1/T Hooft, V/t'Hooft, van X"],
            'first_author_norm': u'T Hooft, V',
            'orcid_pub': [u'-', u'-', u'-'],
            'orcid_user': [u'-', u'1111-2222-3333-4444', u'-'],
            'page_count': 0,
            'author_count': 3,
            'doctype_facet_hier': [u'0/Article', u'1/Article/Journal Article']
        })

        # test editor/series field
        r = solr_adapter.SolrAdapter.adapt({
            "id" : 99999996,
            'bibcode' : u'2018arXiv180303598K',
            "text": {},
            "entry_date": "2018-03-11T00:00:00Z",
            "metadata" : {
                "references": [],
                'properties': {'refereed': False, 'openaccess': True,
                               'doctype': {'content': u'article', 'origin': u'ADS metadata'},
                               'private': False, 'ocrabstract': False, 'ads_openaccess':False,
                               'eprint_openaccess': True, 'pub_openaccess': False},
                "relations": {},
                "general" : {
                    "publication" : {
                        "origin" : u"ARXIV",
                        'dates' : [
                            {
                                'type' : u'date-preprint',
                                'content' : u'2018-03-00'
                                }
                            ]
                        },
                    'series': u'series name go here if this was a series',
                    'authors': [
                        {'name': {'normalized': u'Accomazzi, A', 'western': u"Accomazzi, Alberto", 'native': ''},
                         'number': u'1', 'affiliations': [], 'orcid': '', 'type': 'editor', 'emails': []}],
                }
            },
        })
        solr_adapter.SolrAdapter.validate(r) #Raises AssertionError if not validated
        self.assertEquals(r, {
            "id" : 99999996,
            'bibcode' : u'2018arXiv180303598K',
            'date':     u'2018-03-01T00:00:00.000000Z',
            'bibstem': [u'arXiv', u'arXiv1803'],
            'bibstem_facet': u'arXiv',
            'entry_date': '2018-03-11T00:00:00.000000Z',
            'pubdate' : u'2018-03-00',
            "property": [u"OPENACCESS", u"EPRINT_OPENACCESS", u"ARTICLE", u"NOT REFEREED"],
            'doctype': u'article',

            'aff': [u'-'],
           'author_facet': [u'Accomazzi, A'],
           'author_facet_hier': [u'0/Accomazzi, A', u'1/Accomazzi, A/Accomazzi, Alberto'],
           'author_norm': [u'Accomazzi, A'],
            'email': [u'-'],
            'first_author': u'Accomazzi, Alberto',
            'first_author_facet_hier': [u'0/Accomazzi, A', u'1/Accomazzi, A/Accomazzi, Alberto'],
            'first_author_norm': u'Accomazzi, A',
            'orcid_pub': [u'-'],
            'author_count': 1,
            'page_count': 0,
            'doctype_facet_hier': [u'0/Article', u'1/Article/Journal Article'],
            'series': u'series name go here if this was a series',
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
            s, l = solr_adapter.bibstem_mapper(t['bibcode'])
            self.assertEquals([s,l],t['bibstems'])

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
