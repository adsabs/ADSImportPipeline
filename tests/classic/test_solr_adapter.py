# -*- coding: utf-8 -*-
import unittest

from aip.classic import solr_adapter
from tests.stubdata import ADSRECORDS
from adsputils import get_date


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
         'entry_date': '2003-03-22T00:00:00.000000Z',
         'first_author': u"t'Hooft, van X",
         'first_author_facet_hier': [u'0/T Hooft, V', u"1/T Hooft, V/t'Hooft, van X"],
         'first_author_norm': u'T Hooft, V',
         'id': 99999999,
         'identifier': [u'arxiv:1234.5678',
          u'doi:\xc5\xbd\xc5\xa0\xc4\x8c\xc5\x98\xc4\x8e\xc5\xa4\xc5\x87:123456789',
          u'testbibcode',
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
         'pubdate': u'2013-08-05',
         'title': [u'This is of the title', u'This is of the alternate'],
         'volume': u'l24'})
    
        r = solr_adapter.SolrAdapter.adapt(ADSRECORDS['testbibcode2'])
        solr_adapter.SolrAdapter.validate(r) #Raises AssertionError if not validated
        self.assertEquals(r, {
            "first_author": u"Kurtz, Michael J.",
        #    "links_data": [u"{\"title\":\"\",\"type\":\"spires\",\"instances\":\"\"}", "{\"title\":\"\",\"type\":\"electr\",\"instances\":\"\"}", "{\"title\":\"\",\"type\":\"spires\",\"instances\":\"\"}"],
            "entry_date": '2003-03-22T00:00:00.000000Z',
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
            "identifier": [u"10.1051/aas:2000170", u"2000A&AS..143...41K_test"],
            "database": [u"astronomy"], 
            "author":
                [u"Kurtz, Michael J.", u"Eichhorn, Guenther", u"Accomazzi, Alberto",
                 u"Grant, Carolyn S.", u"Murray, Stephen S.", u"Watson, Joyce M."],
            "author_count": 6,
            "pub_raw": u"Astronomy and Astrophysics Supplement, v.143, p.41-59", 
        #    "cite_read_boost": 0.45,
            "first_author_facet_hier": [u"0/Kurtz, M", u"1/Kurtz, M/Kurtz, Michael J"], 
            "title": [u"The NASA Astrophysics Data System: Overview"],
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
                         'orcid': '', 'type': 'editor', 'emails': []}],
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
            'entry_date': '2003-02-22T00:00:00.000000Z',
            'pubdate' : u'2014-06-00',
            'doctype': u'article',
            
            'aff': [u'-',
                  u'NASA Kavli space center, Cambridge, MA 02138, USA'],
            'author': [u"t'Hooft, van X", u'Anders, John Michael'],
            'author_facet': [u'T Hooft, V', u'Anders, J M'],
            'author_facet_hier': [u'0/T Hooft, V',
                                  u"1/T Hooft, V/t'Hooft, van X",
                                  u'0/Anders, J M',
                                  u'1/Anders, J M/Anders, John Michael'],
            'author_norm': [u'T Hooft, V', u'Anders, J M'],
            'editor': [u'Einstein, A'],
            'email': [u'-', u'anders@email.com', u'-'],
            'first_author': u"t'Hooft, van X",
            'first_author_facet_hier': [u'0/T Hooft, V', u"1/T Hooft, V/t'Hooft, van X"],
            'first_author_norm': u'T Hooft, V',
            'orcid_pub': [u'-', u'-'],
            'orcid_user': [u'-', u'1111-2222-3333-4444', u'-'],
            'page_count': 0,
            'author_count': 2,
            'doctype_facet_hier': [u'0/Article', u'1/Article/Journal Article'],
            'identifier': [u'2014arXiv1406.4542H'],
        })

        # test addition of type = collaboration, which should act similar to type = regular
        r = solr_adapter.SolrAdapter.adapt({
            "id": 99999998,
            "modtime": '2014-06-18T21:06:49',
            'bibcode': u'2014arXiv1406.4542H',
            "text": {},
            "entry_date": "2003-02-21",
            "metadata": {
                "references": [],
                'properties': {'refereed': False, 'openaccess': True,
                               'doctype': {'content': u'article', 'origin': u'ADS metadata'},
                               'private': False, 'ocrabstract': False, 'ads_openaccess': False,
                               'eprint_openaccess': True, 'pub_openaccess': False
                               },
                "relations": {},
                "general": {
                    "publication": {
                        "origin": u"ARXIV",
                        'dates': [
                            {
                                'type': u'date-preprint',
                                'content': u'2014-06-00'
                            }
                        ]
                    },
                    'authors': [
                        {'name': {'normalized': u'T Hooft, V', 'western': u"t'Hooft, van X", 'native': ''},
                         'number': u'1', 'affiliations': [], 'orcid': '', 'type': 'regular', 'emails': []},
                        {'name': {'normalized': u'Anders, J M', 'western': u'Anders, John Michael', 'native': ''},
                         'number': u'2', 'affiliations': [u'NASA Kavli space center, Cambridge, MA 02138, USA'],
                         'orcid': '', 'type': 'collaboration', 'emails': [u'anders@email.com']},
                        {'name': {'normalized': u'Einstein, A', 'western': u'Einstein, A', 'native': ''},
                         'number': u'3', 'affiliations': [u'Einsteininstitute, Zurych, Switzerland'],
                         'orcid': '', 'type': 'editor', 'emails': []}],
                }
            },
            'orcid_claims': {'verified': [u'-', u'1111-2222-3333-4444', u'-']}
        })
        solr_adapter.SolrAdapter.validate(r)  # Raises AssertionError if not validated
        self.assertEquals(r, {
            "id": 99999998,
            'bibcode': u'2014arXiv1406.4542H',
            'date': u'2014-06-01T00:00:00.000000Z',
            'bibstem': [u'arXiv', u'arXiv1406'],
            'bibstem_facet': u'arXiv',
            'entry_date': '2003-02-22T00:00:00.000000Z',
            'pubdate': u'2014-06-00',
            'doctype': u'article',

            'aff': [u'-',
                    u'NASA Kavli space center, Cambridge, MA 02138, USA'],
            'author': [u"t'Hooft, van X", u'Anders, John Michael'],
            'author_facet': [u'T Hooft, V', u'Anders, J M'],
            'author_facet_hier': [u'0/T Hooft, V',
                                  u"1/T Hooft, V/t'Hooft, van X",
                                  u'0/Anders, J M',
                                  u'1/Anders, J M/Anders, John Michael'],
            'author_norm': [u'T Hooft, V', u'Anders, J M'],
            'editor': [u'Einstein, A'],
            'email': [u'-', u'anders@email.com', u'-'],
            'first_author': u"t'Hooft, van X",
            'first_author_facet_hier': [u'0/T Hooft, V', u"1/T Hooft, V/t'Hooft, van X"],
            'first_author_norm': u'T Hooft, V',
            'orcid_pub': [u'-', u'-'],
            'orcid_user': [u'-', u'1111-2222-3333-4444', u'-'],
            'page_count': 0,
            'author_count': 2,
            'doctype_facet_hier': [u'0/Article', u'1/Article/Journal Article'],
            'identifier': [u'2014arXiv1406.4542H'],
        })

        # test identifer arXiv with bibcode
        r = solr_adapter.SolrAdapter.adapt({
            "id": 99999981,
            "modtime": '2018-07-30T21:06:49',
            'bibcode': u'2018arXiv180710779B',
            "text": {},
            "entry_date": "2018-07-30",
            "metadata": {
                "references": [],
                'properties': {'refereed': False, 'openaccess': True,
                               'doctype': {'content': u'article', 'origin': u'ADS metadata'},
                               'private': False, 'ocrabstract': False, 'ads_openaccess': False,
                               'eprint_openaccess': True, 'pub_openaccess': False
                               },
                "relations": {
                    'identifiers': [
                        {
                            'bibcode': u'2018arXiv180710779B',
                            'content': u'arXiv:1807.10779'
                        }
                    ]
                },
                "general": {
                    "publication": {
                        "origin": u"ARXIV",
                        'dates': [
                            {
                                'type': u'date-preprint',
                                'content': u'2018-07-30'
                            }
                        ]
                    },
                    'authors': [
                        {'name': {'normalized': u'T Hooft, V', 'western': u"t'Hooft, van X", 'native': ''},
                         'number': u'1', 'affiliations': [], 'orcid': '', 'type': 'regular', 'emails': []}],
                }
            },
        })
        solr_adapter.SolrAdapter.validate(r)  # Raises AssertionError if not validated
        self.assertEquals(r, {
            "id": 99999981,
            'bibcode': u'2018arXiv180710779B',
            'date': u'2018-07-30T00:30:00.000000Z',
            'bibstem': [u'arXiv', u'arXiv1807'],
            'bibstem_facet': u'arXiv',
            'entry_date': '2018-07-31T00:00:00.000000Z',
            'pubdate': u'2018-07-30',
            'doctype': u'article',

            'aff': [u'-'],
            'author': [u"t'Hooft, van X"],
            'author_facet': [u'T Hooft, V'],
            'author_facet_hier': [u'0/T Hooft, V',
                                  u"1/T Hooft, V/t'Hooft, van X"],
            'author_norm': [u'T Hooft, V'],
            'email': [u'-'],
            'first_author': u"t'Hooft, van X",
            'first_author_facet_hier': [u'0/T Hooft, V', u"1/T Hooft, V/t'Hooft, van X"],
            'first_author_norm': u'T Hooft, V',
            'orcid_pub': [u'-'],
            'page_count': 0,
            'author_count': 1,
            'doctype_facet_hier': [u'0/Article', u'1/Article/Journal Article'],

            'identifier': [u'2018arXiv180710779B', u'arXiv:1807.10779'],
        })

        # test identifer arXiv with bibcode, different kind of arXiv id, plus made sure links are captured properly
        r = solr_adapter.SolrAdapter.adapt({
            "id": 99999982,
            "modtime": '1968-09-00T21:06:49',
            'bibcode': u'1968NuPhB...7...79F',
            "text": {},
            "entry_date": "2004-06-09T00:00:00.000000Z",
            "metadata": {
                "references": [],
                'properties': {'refereed': False, 'openaccess': True,
                               'doctype': {'content': u'article', 'origin': u'ADS metadata'},
                               'private': False, 'ocrabstract': False, 'ads_openaccess': False,
                               'eprint_openaccess': True, 'pub_openaccess': False
                               },
                "relations": {
                    'identifiers': [
                        {
                            'bibcode': u'2002quant.ph..6057F',
                            'content': u'arXiv:quant-ph/0206057'
                        }
                    ],
                    'preprints': [{'content': u'arXiv:quant-ph/0206057'}],
                    'links': [
                        {
                            'url': u'http://arxiv.org/abs/quant-ph/0206057',
                            'access': u'open',
                            'type': u'preprint',
                        },
                        {
                            'url': u'http://inspirehep.net/search?p=find+eprint+quant-ph/0206057',
                            'type': u'spires',
                        },
                        {
                            'url': u'http://adsabs.harvard.edu/abs/2002quant.ph..6057F',
                            'type': u'ADSlink'
                        }
                    ]
                },
                "general": {
                    "publication": {
                        "origin": u"ARXIV",
                        'dates': [
                            {
                                'type': u'date-preprint',
                                'content': u'1968-09-00'
                            }
                        ]
                    },
                    'authors': [
                        {'name': {'normalized': u'T Hooft, V', 'western': u"t'Hooft, van X", 'native': ''},
                         'number': u'1', 'affiliations': [], 'orcid': '', 'type': 'regular', 'emails': []}],
                }
            },
        })
        solr_adapter.SolrAdapter.validate(r)  # Raises AssertionError if not validated
        self.assertEquals(r, {
            "id": 99999982,
            'bibcode': u'1968NuPhB...7...79F',
            'date': u'1968-09-01T00:00:00.000000Z',
            'bibstem': [u'NuPhB', u'NuPhB...7'],
            'bibstem_facet': u'NuPhB',
            'entry_date': '2004-06-10T00:00:00.000000Z',
            'pubdate': u'1968-09-00',
            'doctype': u'article',

            'aff': [u'-'],
            'author': [u"t'Hooft, van X"],
            'author_facet': [u'T Hooft, V'],
            'author_facet_hier': [u'0/T Hooft, V',
                                  u"1/T Hooft, V/t'Hooft, van X"],
            'author_norm': [u'T Hooft, V'],
            'email': [u'-'],
            'first_author': u"t'Hooft, van X",
            'first_author_facet_hier': [u'0/T Hooft, V', u"1/T Hooft, V/t'Hooft, van X"],
            'first_author_norm': u'T Hooft, V',
            'orcid_pub': [u'-'],
            'page_count': 0,
            'author_count': 1,
            'doctype_facet_hier': [u'0/Article', u'1/Article/Journal Article'],

            'identifier': [u'1968NuPhB...7...79F', u'arXiv:quant-ph/0206057'],
            'links_data': [
                u'{"access": "open", "instances": "", "title": "", "type": "preprint", "url": "http://arxiv.org/abs/quant-ph/0206057"}',
                u'{"access": "", "instances": "", "title": "", "type": "spires", "url": "http://inspirehep.net/search?p=find+eprint+quant-ph/0206057"}',
                u'{"access": "", "instances": "", "title": "", "type": "ADSlink", "url": "http://adsabs.harvard.edu/abs/2002quant.ph..6057F"}'
            ],
        })

        # test identifer ascl
        r = solr_adapter.SolrAdapter.adapt({
            "id": 99999983,
            "modtime": '1968-09-00T21:06:49',
            'bibcode': u'2018ascl.soft02007G',
            "text": {},
            "entry_date": "2004-06-09T00:00:00.000000Z",
            "metadata": {
                "references": [],
                'properties': {'refereed': False, 'openaccess': True,
                               'doctype': {'content': u'Software', 'origin': ''},
                               'private': False, 'ocrabstract': False, 'ads_openaccess': False,
                               'eprint_openaccess': True, 'pub_openaccess': False
                               },
                "relations": {
                    'identifiers': [
                        {
                            'type': u'ascl',
                            'content': u'ascl:1802.007'
                        }
                    ]
                },
                "general": {
                    "publication": {
                        "origin": u"ASCL",
                        'dates': [
                            {
                                'type': u'date-published',
                                'content': u'2018-02-00'
                            }
                        ]
                    },
                    'authors': [
                        {'name': {'normalized': u'T Hooft, V', 'western': u"t'Hooft, van X", 'native': ''},
                         'number': u'1', 'affiliations': [], 'orcid': '', 'type': 'regular', 'emails': []}],
                }
            },
        })
        solr_adapter.SolrAdapter.validate(r)  # Raises AssertionError if not validated
        self.assertEquals(r, {
            "id": 99999983,
            'bibcode': u'2018ascl.soft02007G',
            'date': u'2018-02-01T00:00:00.000000Z',
            'bibstem': [u'ascl', u'ascl.soft'],
            'bibstem_facet': u'ascl.soft',
            'entry_date': '2004-06-10T00:00:00.000000Z',
            'pubdate': u'2018-02-00',
            'doctype': u'software',

            'aff': [u'-'],
            'author': [u"t'Hooft, van X"],
            'author_facet': [u'T Hooft, V'],
            'author_facet_hier': [u'0/T Hooft, V',
                                  u"1/T Hooft, V/t'Hooft, van X"],
            'author_norm': [u'T Hooft, V'],
            'email': [u'-'],
            'first_author': u"t'Hooft, van X",
            'first_author_facet_hier': [u'0/T Hooft, V', u"1/T Hooft, V/t'Hooft, van X"],
            'first_author_norm': u'T Hooft, V',
            'orcid_pub': [u'-'],
            'page_count': 0,
            'author_count': 1,
            'doctype_facet_hier': ["0/Non-Article", "1/Non-Article/Software"],

            'identifier': [u'ascl:1802.007', u'2018ascl.soft02007G'],
        })

        # test addition of type = review, which should act similar to type = regular
        r = solr_adapter.SolrAdapter.adapt({
            "id": 99999984,
            "modtime": "2017-08-27T23:33:35",
            'bibcode': u'1988Sci...240..668D',
            "text": {},
            "entry_date": "2002-06-26",
            "metadata": {
                "references": [],
                'properties': {'refereed': False, 'openaccess': False,
                               'doctype': {'content': u'article', 'origin': u'ADS metadata'},
                               'private': False, 'ocrabstract': False, 'ads_openaccess': False,
                               'eprint_openaccess': False, 'pub_openaccess': False
                               },
                "relations": {},
                "general": {
                    "publication": {
                        "origin": u"JSTOR",
                        'dates': [
                            {
                                'type': u'date-published',
                                'content': u'1988-04-00'
                            }
                        ]
                    },
                    'authors': [
                        {'name': {'normalized': u'De Zeeuw, T', 'western': u'De Zeeuw, Tim', 'native': ''},
                         'number': u'1', 'affiliations': [],
                         'orcid': '', 'type': 'book', 'emails': []},
                        {'name': {'normalized': u'Miller, R', 'western': u"Miller, Richard H.", 'native': ''},
                         'number': u'2', 'affiliations': [], 'orcid': '', 'type': 'review', 'emails': []},
                    ]
               }
            },
            'orcid_claims': {'verified': [u'-']}
        })
        solr_adapter.SolrAdapter.validate(r)  # Raises AssertionError if not validated
        self.assertEquals(r, {
            "id": 99999984,
            'bibcode': u'1988Sci...240..668D',
            'date': u'1988-04-01T00:00:00Z',
            'bibstem': [u'Sci', u'Sci...240'],
            'bibstem_facet': u'Sci',
            'entry_date': '2002-06-27T00:00:00.000000Z',
            'pubdate': u'1988-04-00',
            'date': u'1988-04-01T00:00:00.000000Z',
            'doctype': u'article',
            'aff': [u'-'],
            'author': [u"Miller, Richard H."],
            'author_facet': [u'Miller, R'],
            'author_facet_hier': [u'0/Miller, R', u'1/Miller, R/Miller, Richard H'],
            'author_norm': [u'Miller, R'],
            'book_author': [u'De Zeeuw, Tim'],
            'email': [u'-', u'-'],
            'first_author': u"Miller, Richard H.",
            'first_author_facet_hier': [u'0/Miller, R', u'1/Miller, R/Miller, Richard H'],
            'first_author_norm': u'Miller, R',
            'orcid_pub': [u'-'],
            'orcid_user': [u'-', u'-'],
            'page_count': 0,
            'author_count': 1,
            'doctype_facet_hier': [u'0/Article', u'1/Article/Journal Article'],
            'identifier': [u'1988Sci...240..668D'],
        })

        # check the entry_date updates - don't update if the timestamp is setup
        r = solr_adapter.SolrAdapter.adapt({
            "id": 99999997,
            "modtime": '2014-06-18T21:06:49',
            'bibcode': u'2014arXiv1406.4542H',
            "text": {},
            "entry_date": "2003-02-21T02:30:00.000000Z",
            "metadata": {
                "references": [],
                'properties': {'refereed': False, 'openaccess': True,
                               'doctype': {'content': u'article', 'origin': u'ADS metadata'},
                               'private': False, 'ocrabstract': False, 'ads_openaccess': False,
                               'eprint_openaccess': True, 'pub_openaccess': False
                               },
                "relations": {},
                "general": {
                    "publication": {
                        "origin": u"ARXIV",
                        'dates': [
                            {
                                'type': u'date-preprint',
                                'content': u'2014-06-00'
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
                         'orcid': '', 'type': 'editor', 'emails': []}],
                }
            },
            'orcid_claims': {'verified': [u'-', u'1111-2222-3333-4444', u'-']}
        })
        solr_adapter.SolrAdapter.validate(r)  # Raises AssertionError if not validated
        self.assertEquals(r, {
            "id": 99999997,
            'bibcode': u'2014arXiv1406.4542H',
            'date': u'2014-06-01T00:00:00.000000Z',
            'bibstem': [u'arXiv', u'arXiv1406'],
            'bibstem_facet': u'arXiv',
            'entry_date': '2003-02-21T02:30:00.000000Z',
            'pubdate': u'2014-06-00',
            'doctype': u'article',

            'aff': [u'-',
                    u'NASA Kavli space center, Cambridge, MA 02138, USA'],
            'author': [u"t'Hooft, van X", u'Anders, John Michael'],
            'author_facet': [u'T Hooft, V', u'Anders, J M'],
            'author_facet_hier': [u'0/T Hooft, V',
                                  u"1/T Hooft, V/t'Hooft, van X",
                                  u'0/Anders, J M',
                                  u'1/Anders, J M/Anders, John Michael'],
            'author_norm': [u'T Hooft, V', u'Anders, J M'],
            'editor': [u'Einstein, A'],
            'email': [u'-', u'anders@email.com', u'-'],
            'first_author': u"t'Hooft, van X",
            'first_author_facet_hier': [u'0/T Hooft, V', u"1/T Hooft, V/t'Hooft, van X"],
            'first_author_norm': u'T Hooft, V',
            'orcid_pub': [u'-', u'-'],
            'orcid_user': [u'-', u'1111-2222-3333-4444', u'-'],
            'page_count': 0,
            'author_count': 2,
            'doctype_facet_hier': [u'0/Article', u'1/Article/Journal Article'],
            'identifier': [u'2014arXiv1406.4542H'],
        })

        # check the entry_date updates - don't update if the date is today
        now = get_date()
        today = now.date()
        r = solr_adapter.SolrAdapter.adapt({
            "id": 99999997,
            "modtime": '2014-06-18T21:06:49',
            'bibcode': u'2014arXiv1406.4542H',
            "text": {},
            "entry_date": '{}-{:02d}-{:02d}'.format(today.year, today.month, today.day),
            "metadata": {
                "references": [],
                'properties': {'refereed': False, 'openaccess': True,
                               'doctype': {'content': u'article', 'origin': u'ADS metadata'},
                               'private': False, 'ocrabstract': False, 'ads_openaccess': False,
                               'eprint_openaccess': True, 'pub_openaccess': False
                               },
                "relations": {},
                "general": {
                    "publication": {
                        "origin": u"ARXIV",
                        'dates': [
                            {
                                'type': u'date-preprint',
                                'content': u'2014-06-00'
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
                         'orcid': '', 'type': 'editor', 'emails': []}],
                }
            },
            'orcid_claims': {'verified': [u'-', u'1111-2222-3333-4444', u'-']}
        })
        solr_adapter.SolrAdapter.validate(r)  # Raises AssertionError if not validated
        self.assertEquals(r, {
            "id": 99999997,
            'bibcode': u'2014arXiv1406.4542H',
            'date': u'2014-06-01T00:00:00.000000Z',
            'bibstem': [u'arXiv', u'arXiv1406'],
            'bibstem_facet': u'arXiv',
            'entry_date': '{}-{:02d}-{:02d}T00:00:00.000000Z'.format(today.year, today.month, today.day),
            'pubdate': u'2014-06-00',
            'doctype': u'article',

            'aff': [u'-',
                    u'NASA Kavli space center, Cambridge, MA 02138, USA'],
            'author': [u"t'Hooft, van X", u'Anders, John Michael'],
            'author_facet': [u'T Hooft, V', u'Anders, J M'],
            'author_facet_hier': [u'0/T Hooft, V',
                                  u"1/T Hooft, V/t'Hooft, van X",
                                  u'0/Anders, J M',
                                  u'1/Anders, J M/Anders, John Michael'],
            'author_norm': [u'T Hooft, V', u'Anders, J M'],
            'editor': [u'Einstein, A'],
            'email': [u'-', u'anders@email.com', u'-'],
            'first_author': u"t'Hooft, van X",
            'first_author_facet_hier': [u'0/T Hooft, V', u"1/T Hooft, V/t'Hooft, van X"],
            'first_author_norm': u'T Hooft, V',
            'orcid_pub': [u'-', u'-'],
            'orcid_user': [u'-', u'1111-2222-3333-4444', u'-'],
            'page_count': 0,
            'author_count': 2,
            'doctype_facet_hier': [u'0/Article', u'1/Article/Journal Article'],
            'identifier': [u'2014arXiv1406.4542H'],
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
            'bibstems': [ 'rmtm.', 'rmtm.book' ] },
          { 'bibcode': '2018SPIE10974E..13W',
            'bibstems': [ 'SPIE.', 'SPIE10974' ] }
          ]
        for t in test_cases:
            s, l = solr_adapter.bibstem_mapper(t['bibcode'])
            self.assertEquals([s,l],t['bibstems'])

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
