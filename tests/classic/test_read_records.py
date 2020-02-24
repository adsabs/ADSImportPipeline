import unittest
import sys
import mock
from collections import OrderedDict
from tests.stubdata import ADSRECORDS

if '/proj/ads/soft/python/lib/site-packages' not in sys.path:
    sys.path.append('/proj/ads/soft/python/lib/site-packages')

try:
    from ads.ADSCachedExports import ADSRecords
except ImportError:
    ADSRecords = None
    print "Warning: Fallback to explicit path declaration for import"

# used to mock the canonicalization of records
CANONICALDICT = {
    '2014arXiv1401.2993T': '2014MNRAS.439.1884T',
    '2014MNRAS.439.1884T': '2014MNRAS.439.1884T',
    
    '2013arXiv1306.3186H': '2013MNRAS.434.1889H', 
    '2013MNRAS.434.1889H': '2013MNRAS.434.1889H', 
    
    '1978Natur.275..624M': '1978Natur.275..624M',
    
    '1988ESASP.281b.287G': '1988ESASP.281b.287G',
    '1988IUE88...2..287G': '1988ESASP.281b.287G',
    '1988IUES....1..287G': '1988ESASP.281b.287G',
    '1988uvai....2..287G': '1988ESASP.281b.287G',
    
    '2014PhRvD..90d4013F': '2014PhRvD..90d4013F',
    '2013arXiv1311.6899F': '2014PhRvD..90d4013F',
    
    '2020slow.bibcode...': '2020fake.canonical.'
    }

# a sample of real-world records (except for last one) with fake fingerprints
RECORDS = OrderedDict([
        ('2014arXiv1401.2993T','b'), #This is an alternate to 'f'
        ('2014MNRAS.439.1884T','f'), #This is the canonical of 'b'
        
        ('2013MNRAS.434.1889H','d'), #This is the canonical of 'g'
        ('2013arXiv1306.3186H','g'), #This is the alternate of 'd'
        
        ('1978Natur.275..624M','c'), #No alternates, already canonical
        
        ('1988ESASP.281b.287G','x1'), #Canonical, the following are alternates
        ('1988IUE88...2..287G','a1'),
        ('1988IUES....1..287G','a2'),
        ('1988uvai....2..287G','a3'),
        
        ('2014PhRvD..90d4013F','h'), #This is the canonical of 'h'
        ('2013arXiv1311.6899F','k'), #This it the alternate of 'k'

        ('2020slow.bibcode...','fake') #This one has no canonical
        ])

# this is what read_records should return for the records above
# when run in strict mode
EXPECTED_STRICT =  [
    ('2014MNRAS.439.1884T', 'b;f'),
    ('2013MNRAS.434.1889H', 'd;g'),
    ('1978Natur.275..624M', 'c'),
    ('1988ESASP.281b.287G','a1;a2;a3;x1'),
    ('2014PhRvD..90d4013F','h;k'),
    ]

# results when not run in strict mode
EXPECTED = EXPECTED_STRICT + [('2020slow.bibcode...','fake')]


class TestCanonical(unittest.TestCase):

    # here we mock the entire conversion class so that we can use
    # the fake canonical mappings in CANONICALDICT
    class mock_ConvertBibcodes(object):
        def __init__(self):
            # create inverse mapping
            self.altdict = dict()
            _ = [ (v,k) for (k,v) in CANONICALDICT.items() ] 
            for (k,v) in _:
                if not k: continue
                if k == v: continue
                self.altdict.setdefault(k, [])
                self.altdict[k].append(v)

        def Canonicalize(self, biblist, remove_matches=False):
            newlist = []
            for bibcode in biblist:
                res = CANONICALDICT.get(bibcode)
                if res:
                    bibcode = res
                newlist.append(bibcode)
            return list(set(newlist))

        def getAlternates(self, bibcode):
            return self.altdict.get(bibcode, [])

    def test_getalternates(self):
        from aip.classic import read_records
        import copy
        if not hasattr(read_records, 'ConvertBibcodes'):
            read_records.ConvertBibcodes = self.mock_ConvertBibcodes
        # here we have to prevent the import of ads and ads.Looker needed by aip.classic.conversions
        # so we can mock the conversion of bibcodes.  Ugly as hell but it works
        with mock.patch.dict(sys.modules, { 'ads': mock.Mock(), 'ads.Looker': mock.Mock() } ), \
                mock.patch('aip.classic.conversions.ConvertBibcodes', return_value=self.mock_ConvertBibcodes):
            records = copy.deepcopy(RECORDS)
            results = read_records.canonicalize_records(records)
            self.assertEqual(results, EXPECTED)
            records = copy.deepcopy(RECORDS)
            results = read_records.canonicalize_records(records, force_canonical=True)
            self.assertEqual(results, EXPECTED_STRICT)


class TestADSExports(unittest.TestCase):

    @unittest.skipIf(not ADSRecords, "ads.ADSCachedExports not available")
    def test_canonicalize_records(self):
        from aip.classic import read_records
        results = read_records.canonicalize_records(RECORDS)
        self.assertEqual(results, EXPECTED)

    def test_readRecordsFromADSExports(self):
        from aip.classic import read_records
        if not hasattr(read_records, 'ADSRecords'):
            read_records.ADSRecords = {}
        
        adsrecord = mock.Mock()
        with mock.patch('aip.classic.read_records.ADSRecords', return_value=adsrecord), \
            mock.patch.object(adsrecord, 'export', return_value=adsrecord), \
            mock.patch('aip.classic.read_records.xml_to_dict', return_value=ADSRECORDS[u'2009AAS...21320006C.classic']):
            results = read_records.readRecordsFromADSExports([(u'2009AAS...21320006C', 'fingerprint')])
            self.assertDictContainsSubset({'JSON_fingerprint': 'fingerprint',
                              'bibcode': u'2009AAS...21320006C',
                              'entry_date': u'2009-01-03',
                              'metadata': [{'abstracts': [{'lang': u'en',
                                  'origin': u'AAS',
                                  'text': u'The hobby of astronomy in America was restricted largely to a relatively few well-off persons prior to the 1920\'s in part due to the difficulty in acquiring adequate instruments. Even modest telescopes were quite expensive and very few in number. The standard "beginner\'s\u201d instrument was a three-inch diameter refracting telescope, precision crafted by expert manufacturers. Early Twentieth-century astronomy popularizers recognized the problem of availability of instruments and saw that this hindered growth of the hobby. The idea of making one\'s own telescope was limited to a hardy few with the time, equipment, machining skills, and information required and very few attempted the task. This situation changed dramatically by the late 1920\'s due to the publication of a series of articles in Scientific American that provided detailed, practical instructions for a six-inch Newtonian reflecting telescope, a project well within the means and skills of the average "handyman". Publication of these articles initiated a profound change in perception for amateur astronomers, who quickly became amateur telescope makers as well, creating precision instruments for themselves and in part leading to a widening of the amateur astronomy hobby and interest in astronomy generally. This paper forms a portion of a doctoral dissertation being written by the author.'}],
                                'arxivcategories': [],
                                'authors': [{'affiliations': [u'Iowa State University'],
                                  'emails': [],
                                  'name': {'native': None,
                                   'normalized': u'Cameron, G',
                                   'western': u'Cameron, Gary L.'},
                                  'number': u'1',
                                  'orcid': None,
                                  'type': u'regular'}],
                                'comment': [],
                                'conf_metadata': {'content': None, 'origin': u'AAS'},
                                'copyright': [],
                                'doi': [],
                                'isbns': [],
                                'issns': [],
                                'keywords': [],
                                'language': '',
                                'publication': {'altbibcode': u'2009AAS...21320006C',
                                 'dates': [{'content': u'2009-01-00', 'type': u'date-published'},
                                  {'content': u'2009', 'type': 'publication_year'}],
                                 'electronic_id': u'200',
                                 'issue': None,
                                 'name': {'canonical': u'American Astronomical Society Meeting Abstracts #213',
                                  'raw': u'American Astronomical Society, AAS Meeting #213, id.200.06; <ALTJOURNAL>Bulletin of the American Astronomical Society, Vol. 41, p.187</ALTJOURNAL>'},
                                 'origin': u'AAS',
                                 'page': None,
                                 'page_count': None,
                                 'page_last': None,
                                 'page_range': None,
                                 'volume': u'213'},
                                'pubnote': [],
                                'tempdata': {'alternate_journal': False,
                                 'modtime': u'2016-01-21T23:19:13Z',
                                 'origin': u'AAS',
                                 'primary': True,
                                 'type': u'general'},
                                'titles': [{'lang': u'en',
                                  'text': u"A New Way of Looking: the Amateur Telescope Making Movement in 1920's America"}]},
                               {'abstracts': [],
                                'arxivcategories': [],
                                'authors': [{'affiliations': [u'Iowa State University'],
                                  'emails': [],
                                  'name': {'native': None,
                                   'normalized': u'Cameron, G',
                                   'western': u'Cameron, Gary L.'},
                                  'number': u'1',
                                  'orcid': None,
                                  'type': u'regular'}],
                                'comment': [],
                                'conf_metadata': {'content': None, 'origin': u'AAS'},
                                'copyright': [],
                                'doi': [],
                                'isbns': [],
                                'issns': [],
                                'keywords': [],
                                'language': '',
                                'publication': {'altbibcode': u'2009BAAS...41..187C',
                                 'dates': [{'content': u'2009-01-00', 'type': u'date-published'},
                                  {'content': u'2009', 'type': 'publication_year'}],
                                 'electronic_id': None,
                                 'issue': None,
                                 'name': {'canonical': u'Bulletin of the American Astronomical Society',
                                  'raw': u'<ALTJOURNAL>American Astronomical Society, AAS Meeting #213, id.200.06</ALTJOURNAL>; Bulletin of the American Astronomical Society, Vol. 41, p.187'},
                                 'origin': u'AAS',
                                 'page': u'187',
                                 'page_count': None,
                                 'page_last': None,
                                 'page_range': u'187',
                                 'volume': u'41'},
                                'pubnote': [],
                                'tempdata': {'alternate_journal': True,
                                 'modtime': u'2016-01-21T23:20:41Z',
                                 'origin': u'AAS',
                                 'primary': False,
                                 'type': u'general'},
                                'titles': [{'lang': u'en',
                                  'text': u"A New Way of Looking: the Amateur Telescope Making Movement in 1920's America"}]},
                               {'ads_openaccess': False,
                                'associates': [],
                                'bibgroups': [],
                                'data_sources': [],
                                'databases': [{'content': u'AST', 'origin': u'ADS metadata'}],
                                'doctype': {'content': u'abstract', 'origin': u'ADS metadata'},
                                'eprint_openaccess': False,
                                'ocrabstract': False,
                                'openaccess': False,
                                'private': False,
                                'pub_openaccess': False,
                                'refereed': False,
                                'tempdata': {'alternate_journal': False,
                                 'modtime': None,
                                 'origin': u'ADS metadata',
                                 'primary': False,
                                 'type': u'properties'},
                                'vizier_tables': []},
                               {'alternates': [{'content': u'2009BAAS...41..187C',
                                  'origin': None,
                                  'type': u'alternate'}],
                                'identifiers': [{'content': u'2009AAS...21320006C',
                                  'origin': None,
                                  'type': u'identifier'}],
                                'links': [],
                                'preprints': [],
                                'tempdata': {'alternate_journal': False,
                                 'modtime': None,
                                 'origin': u'ADS metadata',
                                 'primary': False,
                                 'type': u'relations'}}],
                              'text': {'acknowledgement': []}},
                        results[0])


if __name__ == '__main__':
    unittest.main()
