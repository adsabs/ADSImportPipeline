# -*- coding: utf-8 -*-
import unittest
from aip.classic import merger
import datetime
from tests.stubdata import ADSRECORDS

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


    def test_multipleOriginMerger(self):
        A1,A2,C1,C2,M1,M2 = self.A1,self.A2,self.C1,self.C2,self.M1,self.M2
        # priorities are: IOP > SIMBAD > STI
        B1 = {'tempdata':{'origin':'STI; IOP','type':'general'}}
        B2 = {'tempdata':{'origin':'SIMBAD','type':'general'}}
        
        B1['titles'] = [ 'Publisher title' ]
        B2['titles'] = [ 'SIMBAD title' ]
    
        blocks = [B1,B2]
        m = merger.Merger(blocks)
        m.merge()
        results = m.block
    
        expectedResults = { 'titles': [ 'Publisher title' ], 'altpublications': [] }
        self.assertEqual(results,expectedResults)


    def test_unknownOriginMerger(self):
        A1,A2,C1,C2,M1,M2 = self.A1,self.A2,self.C1,self.C2,self.M1,self.M2
        # 'foobar' in unknown origin, and will default to 'PUBLISHER' which is greater than SIMBAD in priorities
        B1 = {'tempdata':{'origin':'foobar','type':'general'}}
        B2 = {'tempdata':{'origin':'SIMBAD','type':'general'}}
        
        B1['titles'] = [ 'Publisher title' ]
        B2['titles'] = [ 'SIMBAD title' ]
    
        blocks = [B1,B2]
        m = merger.Merger(blocks)
        m.merge()
        results = m.block
    
        expectedResults = { 'titles': [ 'Publisher title' ], 'altpublications': [] }
        self.assertEqual(results,expectedResults)


    def test_want_datetime(self):
        m = merger.Merger([])
    
        # Test that inputting a datetime is noop
        dt = datetime.datetime.now()
        self.assertEqual(dt,m.want_datetime(dt))
    
        # Test that passing an integer is treated as a timestamp
        dt = 123
        self.assertEqual(datetime.datetime.fromtimestamp(dt),m.want_datetime(dt))
    
        # Passing a string that int() can operate on also should return a datetime
        dt = '123'
        self.assertEqual(datetime.datetime.fromtimestamp(int(dt)),m.want_datetime(dt))
    
        # Passing a properly ISO formatted string should return a datetime
        dt = '2015-03-26T06:28:56.424424Z'
        res = m.want_datetime(dt)
        self.assertTrue(isinstance(res,datetime.date))
        self.assertEqual(res.year,2015)
        self.assertEqual(res.month,3)
        self.assertEqual(res.day,26)
        self.assertEqual(res.hour,6)
    
        # Passing an unrecognizeable string returns datetime.datetime.now()
        dt = 'foo'
        res = m.want_datetime(dt)
        now = datetime.datetime.now()
        self.assertTrue(isinstance(res,datetime.date))
        self.assertEqual(res.minute,now.minute)

    
if __name__ == '__main__':
    unittest.main()


