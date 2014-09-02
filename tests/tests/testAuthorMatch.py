# -*- coding: utf-8 -*-

import sys, os
PROJECT_HOME = os.path.abspath(os.path.join(os.path.dirname(__file__),'../../'))
sys.path.append(PROJECT_HOME)
import unittest
from lib import author_match

class TestAuthorMatch(unittest.TestCase):

    A1  = {'name': {'western': u'Accomazzi, Alberto'},   'affiliations': [u'ADS']}
    A2  = {'name': {'western': u'Accomazzi, A.'},        'affiliations': [u'CfA', u'SAO']}
    C1  = {'name': {'western': u'Grant, Carolyn S.'},    'affiliations': []}
    C2  = {'name': {'western': u'Stern Grant, C.'},      'affiliations': [u'Harvard']}
    M1  = {'name': {'western': u'Kurtz, Michael'},       'affiliations': []} 
    M2  = {'name': {'western': u'Krüz, M. J.'},          'affiliations': [u'SAO']} 

    def test_match_ads_author01(self):
        for f1,f2 in ( \
            ([self.A1,self.C1,self.M1], [self.C2,self.M2,self.A2]),
            ([self.A1,self.C1,self.M1], [self.A2,self.C2,self.M2]),
            ([self.A1,self.C1,self.M1], [self.C2,self.A2,self.M2]),
            ([self.A1,self.C1,self.M1], [self.M2,self.A2,self.C2]),
            ([self.A1,self.C1,self.M1], [self.M2,self.C2,self.A2])):
            matches = author_match.match_ads_author_fields(f1, f2)
#            print "test01: f1:", f1
#            print "test01: f2:", f2
            self.assertEqual(matches, [(self.A1,self.A2),(self.C1,self.C2),(self.M1,self.M2)])

    def test_match_ads_author02(self):
        for f1,f2 in (([self.A2,self.C2,self.M2], [self.C1,self.M1,self.A1]), 
                      ([self.A2,self.C2,self.M2], [self.M1,self.A1,self.C1]),
                      ([self.A2,self.C2,self.M2], [self.A1,self.M1,self.C1]),
                      ([self.A2,self.C2,self.M2], [self.M1,self.C1,self.A1]),
                      ([self.A2,self.C2,self.M2], [self.C1,self.A1,self.M1])):
            matches = author_match.match_ads_author_fields(f1, f2)
#            print "test02: f1:", f1
#            print "test02: f2:", f2
            self.assertEqual(matches, [(self.A2,self.A1),(self.C2,self.C1),(self.M2,self.M1)])

    def test_match_ads_author03(self):
        matches = author_match.match_ads_author_fields([self.A1,self.C1],[self.M2,self.C2,self.A2])
        self.assertEqual(matches, [(self.A1,self.A2),(self.C1,self.C2)])
        matches = author_match.match_ads_author_fields([self.M1,self.C1],[self.M2,self.C2,self.A2])
        self.assertEqual(matches, [(self.M1,self.M2),(self.C1,self.C2)])
        matches = author_match.match_ads_author_fields([self.M1,self.A1],[self.M2,self.C2,self.A2])
        self.assertEqual(matches, [(self.M1,self.M2),(self.A1,self.A2)])
        matches = author_match.match_ads_author_fields([self.A1],[self.M2,self.C2,self.A2])
        self.assertEqual(matches, [(self.A1,self.A2)])
        matches = author_match.match_ads_author_fields([self.C1],[self.M2,self.C2,self.A2])
        self.assertEqual(matches, [(self.C1,self.C2)])
        matches = author_match.match_ads_author_fields([self.M1],[self.M2,self.C2,self.A2])
        self.assertEqual(matches, [(self.M1,self.M2)])
        matches = author_match.match_ads_author_fields([self.A1,self.C1,self.M1],[self.A2])
        self.assertEqual(matches, [(self.A1,self.A2),(self.C1,None),(self.M1,None)])
        matches = author_match.match_ads_author_fields([self.A1,self.C1,self.M1],[self.C2])
        self.assertEqual(matches, [(self.A1,None),(self.C1,self.C2),(self.M1,None)])
        matches = author_match.match_ads_author_fields([self.A1,self.C1,self.M1],[self.M2])
        self.assertEqual(matches, [(self.A1,None),(self.C1,None),(self.M1,self.M2)])

    def test_is_suitable_match(self):
        self.assertTrue(author_match.is_suitable_match(self.A1,self.A1))
        self.assertTrue(author_match.is_suitable_match(self.C1,self.C1))
        self.assertTrue(author_match.is_suitable_match(self.M1,self.M1))
        self.assertTrue(author_match.is_suitable_match(self.A1,self.A2))
        self.assertTrue(author_match.is_suitable_match(self.C1,self.C2))
        self.assertTrue(author_match.is_suitable_match(self.M1,self.M2))
        self.assertFalse(author_match.is_suitable_match(self.A1,self.C1))
        self.assertFalse(author_match.is_suitable_match(self.A1,self.M1))
        self.assertFalse(author_match.is_suitable_match(self.A1,self.C2))
        self.assertFalse(author_match.is_suitable_match(self.A1,self.M1))


if __name__ == '__main__':
    unittest.main()
