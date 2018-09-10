# -*- coding: utf-8 -*-

import unittest
from aip.classic import author_match

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
            self.assertEqual(matches, [(self.A1,self.A2),(self.C1,self.C2),(self.M1,self.M2)])
            matches = author_match.match_ads_author_fields(f1, f2, impl='np')
            self.assertEqual(matches, [(self.A1,self.A2),(self.C1,self.C2),(self.M1,self.M2)])

    def test_match_ads_author02(self):
        for f1,f2 in (([self.A2,self.C2,self.M2], [self.C1,self.M1,self.A1]), 
                      ([self.A2,self.C2,self.M2], [self.M1,self.A1,self.C1]),
                      ([self.A2,self.C2,self.M2], [self.A1,self.M1,self.C1]),
                      ([self.A2,self.C2,self.M2], [self.M1,self.C1,self.A1]),
                      ([self.A2,self.C2,self.M2], [self.C1,self.A1,self.M1])):
            matches = author_match.match_ads_author_fields(f1, f2)
            self.assertEqual(matches, [(self.A2,self.A1),(self.C2,self.C1),(self.M2,self.M1)])
            matches = author_match.match_ads_author_fields(f1, f2, impl='np')
            self.assertEqual(matches, [(self.A2,self.A1),(self.C2,self.C1),(self.M2,self.M1)])

    def test_match_ads_author03(self):
        matches = author_match.match_ads_author_fields([self.A1,self.C1],[self.M2,self.C2,self.A2])
        self.assertEqual(matches, [(self.A1,self.A2),(self.C1,self.C2)])
        matches = author_match.match_ads_author_fields([self.A1,self.C1],[self.M2,self.C2,self.A2], impl='np')
        self.assertEqual(matches, [(self.A1,self.A2),(self.C1,self.C2)])
        matches = author_match.match_ads_author_fields([self.M1,self.C1],[self.M2,self.C2,self.A2])
        self.assertEqual(matches, [(self.M1,self.M2),(self.C1,self.C2)])
        matches = author_match.match_ads_author_fields([self.M1,self.C1],[self.M2,self.C2,self.A2], impl='np')
        self.assertEqual(matches, [(self.M1,self.M2),(self.C1,self.C2)])
        matches = author_match.match_ads_author_fields([self.M1,self.A1],[self.M2,self.C2,self.A2])
        self.assertEqual(matches, [(self.M1,self.M2),(self.A1,self.A2)])
        matches = author_match.match_ads_author_fields([self.M1,self.A1],[self.M2,self.C2,self.A2], impl='np')
        self.assertEqual(matches, [(self.M1,self.M2),(self.A1,self.A2)])
        matches = author_match.match_ads_author_fields([self.A1],[self.M2,self.C2,self.A2])
        self.assertEqual(matches, [(self.A1,self.A2)])
        matches = author_match.match_ads_author_fields([self.A1],[self.M2,self.C2,self.A2], impl='np')
        self.assertEqual(matches, [(self.A1,self.A2)])
        matches = author_match.match_ads_author_fields([self.C1],[self.M2,self.C2,self.A2])
        self.assertEqual(matches, [(self.C1,self.C2)])
        matches = author_match.match_ads_author_fields([self.C1],[self.M2,self.C2,self.A2], impl='np')
        self.assertEqual(matches, [(self.C1,self.C2)])
        matches = author_match.match_ads_author_fields([self.M1],[self.M2,self.C2,self.A2])
        self.assertEqual(matches, [(self.M1,self.M2)])
        matches = author_match.match_ads_author_fields([self.M1],[self.M2,self.C2,self.A2], impl='np')
        self.assertEqual(matches, [(self.M1,self.M2)])
        matches = author_match.match_ads_author_fields([self.A1,self.C1,self.M1],[self.A2])
        self.assertEqual(matches, [(self.A1,self.A2),(self.C1,None),(self.M1,None)])
        matches = author_match.match_ads_author_fields([self.A1,self.C1,self.M1],[self.A2], impl='np')
        self.assertEqual(matches, [(self.A1,self.A2),(self.C1,None),(self.M1,None)])
        matches = author_match.match_ads_author_fields([self.A1,self.C1,self.M1],[self.C2])
        self.assertEqual(matches, [(self.A1,None),(self.C1,self.C2),(self.M1,None)])
        matches = author_match.match_ads_author_fields([self.A1,self.C1,self.M1],[self.C2], impl='np')
        self.assertEqual(matches, [(self.A1,None),(self.C1,self.C2),(self.M1,None)])
        matches = author_match.match_ads_author_fields([self.A1,self.C1,self.M1],[self.M2])
        self.assertEqual(matches, [(self.A1,None),(self.C1,None),(self.M1,self.M2)])
        matches = author_match.match_ads_author_fields([self.A1,self.C1,self.M1],[self.M2], impl='np')
        self.assertEqual(matches, [(self.A1,None),(self.C1,None),(self.M1,self.M2)])


    def test_match_ads_author04(self):
        # 1993AIAAJ..31..447M (crossref vs. sti)
        [c1,c2,c3,c4,c5] = [{'affiliations': [], 'name': {'western': 'Miles, Richard B.'}}, 
                            {'affiliations': [], 'name': {'western': 'Lempert, Walter R.'}}, 
                            {'affiliations': [], 'name': {'western': 'She, Zhen-Su'}}, 
                            {'affiliations': [], 'name': {'western': 'Zhang, Boying'}}, 
                            {'affiliations': [], 'name': {'western': 'Zhou, Deyu'}}]
        [s1,s2,s3,s4,s5] = [{'affiliations': ['Princeton Univ., NJ'], 'name': {'western': 'Miles, Richard B.'}}, 
                            {'affiliations': ['Princeton Univ., NJ'], 'name': {'western': 'Zhou, Deyu'}}, 
                            {'affiliations': ['Princeton Univ., NJ'], 'name': {'western': 'Zhang, Boying'}}, 
                            {'affiliations': ['Princeton Univ., NJ'], 'name': {'western': 'Lempert, Walter R.'}}, 
                            {'affiliations': ['Arizona Univ., Tucson, AZ'], 'name': {'western': 'She, Zhen-Su'}}]
        crossref = [c1,c2,c3,c4,c5]
        sti = [s1,s2,s3,s4,s5]
        res = [(c1,s1), (c2,s4), (c3,s5), (c4,s3), (c5,s2)]
        matches = author_match.match_ads_author_fields(crossref, sti)
        self.assertEqual(matches, res)
        matches = author_match.match_ads_author_fields(crossref, sti, impl='np')
        self.assertEqual(matches, res)

    def test_match_ads_author05(self):
        matches = author_match.match_ads_author_fields([self.A1,self.C1,self.M1],[])
        self.assertEqual(matches, [(self.A1,None),(self.C1,None),(self.M1,None)])
        matches = author_match.match_ads_author_fields([self.A1,self.C1,self.M1],[], impl='np')
        self.assertEqual(matches, [(self.A1,None),(self.C1,None),(self.M1,None)])
        matches = author_match.match_ads_author_fields([],[self.A1,self.C1,self.M1])
        self.assertEqual(matches, [])
        matches = author_match.match_ads_author_fields([],[self.A1,self.C1,self.M1], impl='np')
        self.assertEqual(matches, [])

    def test_match_ads_author06(self):
        # case where 1987Ap&SS.138...61H was incorrectly matched to 1986tnra.book.....D
        # (no match should be take place here)
        a1 = {"name": {"western": "Hadrava, P."}, "affiliations": ["Astronomical Institute of the Czechoslovak Academy of Sciences"]}
        a2 = {"name": {'western': 'de Waard, Gerrit Jan'}, "affiliations": []}
        matches = author_match.match_ads_author_fields([a1],[a2])
        self.assertEqual(matches,[(a1,None)])
        self.assertFalse(author_match.is_suitable_match(a1,a2))


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
