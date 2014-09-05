import sys, os
import unittest
import random
from collections import OrderedDict
PROJECT_HOME = os.path.abspath(os.path.join(os.path.dirname(__file__),'../../'))
sys.path.append(PROJECT_HOME)

class TestADSExports(unittest.TestCase):

  @unittest.skipIf(not os.path.exists('/proj/ads/soft/'),"Skipping because /proj/ads/soft/ is unavailable")
  def setUp(self):
    try:
      from ads.ADSExports import ADSRecords
    except ImportError:
      sys.path.append('/proj/ads/soft/python/lib/site-packages')
      from ads.ADSExports import ADSRecords
      print "Warning: Fallback to explicit path declaration for import"

  @unittest.skip("Skipping testing of ADSRecords instantiation")
  def test_ADSRecords_instantiation(self):
    self.adsRecords = ADSRecords('full','XML')
    self.assertIsInstance(self.adsRecords,ADSRecords)

  def test_canonicalize_records(self):
    from lib import ReadRecords

    records = OrderedDict([
      ('2014arXiv1401.2993T','b'), #This is an alternate to 'f'
      ('2014MNRAS.439.1884T','f'), #This is the canonical of 'b'

      ('2013MNRAS.434.1889H','d'), #This is the canonical of 'g'
      ('2013arXiv1306.3186H','g'), #This is the alternate of 'd'

      ('1978Nat...275..624M','c'), #No alternates, already canonical

      ('1988ESASP.281b.287G','x1'), #Canonical, the following are alternates
      ('1988IUE88...2..287G','a1'),
      ('1988IUES....1..287G','a2'),
      ('1988uvai....2..287G','a3'),
      
      ('2014PhRvD..90d4013F','h'), #This is the canonical of 'h'
      ('2013arXiv1311.6899F','k'), #This it the alternate of 'k'
    ])
    expected =  [
      ('2014MNRAS.439.1884T', 'b;f'),
      ('2013MNRAS.434.1889H', 'd;g'),
      ('1978Natur.275..624M', 'c'),
      ('1988ESASP.281b.287G','a1;a2;a3;x1'),
      ('2014PhRvD..90d4013F','h;k'),
    ]
    
    results = ReadRecords.canonicalize_records(OrderedDict((k,v) for k,v in records.iteritems()))
    self.assertEqual(results, expected)
