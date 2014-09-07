"""
This code was found in the github repository of Martin-Louis Bright (mlbright@gmail.com):
https://github.com/mlbright/Assignment-Problem/blob/master/kuhn_munkres.py

"""

#!/usr/bin/python
#------------------------------------------------------------------------------#

# The Kuhn-Munkres or Hungarian algorithm.
# Complexity: O(n^3)
# Computes a max weight perfect matching in a bipartite graph

# Modified from:
# http://www.enseignement.polytechnique.fr/informatique/INF441/INF441b/code/kuhnMunkres.py

# Very good explanations at:
# http://www.topcoder.com/tc?module=Static&d1=tutorials&d2=hungarianAlgorithm
# http://www.cse.ust.hk/~golin/COMP572/Notes/Matching.pdf
# http://www.math.uwo.ca/~mdawes/courses/344/kuhn-munkres.pdf

"""
    For min weight perfect matching, simply negate the weights.

    Global variables:
       n = number of vertices on each side
       U,V vertex sets
       lu,lv are the labels of U and V resp.
       the matching is encoded as 
       - a mapping Mu from U to V, 
       - and Mv from V to U.
    
    The algorithm repeatedly builds an alternating tree, rooted in a
    free vertex u0. S is the set of vertices in U covered by the tree.
    For every vertex v, T[v] is the parent in the tree and Mv[v] the
    child.

    The algorithm maintains min_slack, s.t. for every vertex v not in
    T, min_slack[v]=(val,u1), where val is the minimum slack
    lu[u]+lv[v]-w[u][v] over u in S, and u1 is the vertex that
    realizes this minimum.

    Complexity is O(n^3), because there are n iterations in
    assign, and each call to augment costs O(n^2). This is
    because augment() makes at most n iterations itself, and each
    updating of min_slack costs O(n).
"""

import Levenshtein
import sys
import re


class HungarianGraph(object):

    def __init__(self, weights):
        self.weights = weights
        self.N  = len(self.weights)

        self.lu = [max([self.weights[u][v] for v in xrange(self.N)]) for u in xrange(self.N)]  # start with trivial labels
        self.lv = [0 for v in xrange(self.N)]

        self.Mu = {}  # start with empty matching
        self.Mv = {}
        self.S = None
        self.T = None
        self.min_slack = None


    def improve_labels(self,val):
        """ change the labels, and maintain min_slack. """
        for u in self.S:
            self.lu[u] -= val
        for v in xrange(self.N):
            if v in self.T:
                self.lv[v] += val
            else:
                self.min_slack[v][0] -= val


    def improve_matching(self,v):
        """ apply the alternating path from v to the root in the tree. """
        u = self.T[v]
        if u in self.Mu:
            self.improve_matching(self.Mu[u])
        self.Mu[u] = v
        self.Mv[v] = u


    def slack(self,u,v):
        return self.lu[u] + self.lv[v] - self.weights[u][v]


    def augment(self):
        """ augment the matching, possibly improving the labels on the way. """
        while True:
            # select edge (u,v) with u in S, v not in T and min slack
            ((val, u), v) = min([(self.min_slack[v], v) for v in xrange(self.N) if v not in self.T])
            assert u in self.S
            if val > 0:        
                self.improve_labels(val)
            # now we are sure that (u,v) is saturated
            # XXX
            # if slack(u,v):
            #    print "U: ", u, " V: ", v, " slack: ", slack(u,v)
            # XXX
            # assert slack(u,v)==0
            assert self.slack(u,v) < 1e-10
            self.T[v] = u                            # add (u,v) to the tree
            if v in self.Mv:
                u1 = self.Mv[v]                      # matched edge, 
                assert not u1 in self.S
                self.S.add(u1)
                for v in xrange(self.N): # maintain min_slack
                    if v not in self.T and self.min_slack[v][0] > self.slack(u1,v):
                        self.min_slack[v] = [self.slack(u1,v), u1]
            else:
                self.improve_matching(v) # v is a free vertex
                return


    def assign(self):
        """
        given w, the weight matrix of a complete bipartite graph,
        returns the mappings Mu : U -> V, Mv : V -> U,
        encoding the matching as well as the value of it.
        """

        while len(self.Mu) < self.N:
            u0 = [u for u in xrange(self.N) if u not in self.Mu][0] # choose free vertex u0
            self.S = set([u0])
            self.T = {}
            self.min_slack = [[self.slack(u0,v), u0] for v in xrange(self.N)]
            self.augment()
        # val. of matching is total edge weight
        val = sum(self.lu) + sum(self.lv)
        return self.Mv, self.Mu, val


def parse_ads_authors (name):
    """
    Utility function to normalize ADS author names to allow
    meaningful comparisons.  
    Input name is expected to be a standard ADS author name in 
    the format: "Lastname, F[irst] [M[iddle]...]"
    """
    parts = name.split(', ')
    last = parts.pop(0) if parts else ''
    rest = parts.pop(0) if parts else ''
    parts = rest.split(' ')
    # now remove dots from initials
    parts = [p.replace('.','') if p.endswith('.') else p for p in parts]
    # prepend last name
    parts.insert(0,last)

    return parts


# We don't want to blindly strip
# all names down to first initial unless we have to, so we
# instead analyze their structure and output the name which 
# maximally match the precision of both author names.

def normalize_authors (a1, a2):
    """
    Modify author names so that we return the longest versions
    of compatible name strings.  We do this so that we will
    never compare a full first name with its initial, for instance
    """
    # only worry about non-empty strings
    if not a1 or not a2:
        return a1, a2

    pa1 = parse_ads_authors(a1.lower())
    pa2 = parse_ads_authors(a2.lower())
    author1 = pa1.pop(0)
    author2 = pa2.pop(0)

    author1 += ','
    author2 += ','
    # now append segments from first and middle names
    ntokens = min(len(pa1),len(pa2))
    for i in range(ntokens):
        tlen = min(len(pa1[i]), len(pa2[i]))
        author1 += ' ' + pa1[i][:tlen]
        author2 += ' ' + pa2[i][:tlen]
    
    return author1, author2


def match_author_lists (al1, al2):
    """
    matches author names found in two lists of author names using
    an approximate distance measure (Levenshtein) and using the
    Kuhn-Munkres algorithm
    """
    # we work with a square matrix, so enforce same
    # dimension for both arrays
    n = max(len(al1), len(al2))
    m = [[-1 for i in range(n)] for j in range(n)]

    # now compute cost matrix
    for i in range(n):
        s1 = al1[i] if i < len(al1) else ''
        for j in range(n):
            s2 = al2[j] if j < len(al2) else ''
            # note: we can't cache the normalized versions
            # of author names because they are computed in pairs
            s1, s2 = normalize_authors(s1, s2)
            similarity = Levenshtein.ratio(unicode(s1), unicode(s2))
            # print "Similarity: %f\t%s; %s" % (similarity, s1, s2)
            m[i][j] = similarity

    # print m
    #map1, map2, score = assign(m)
    HGraph = HungarianGraph(m)
    map1, map2, score = HGraph.assign()
    
    # normalize score so that it is a number between 0 and 1
    # (and is therefore independent on the number of authors)
    # since some of the array elements may be empty strings,
    # we need to use the total number of actual mappings,
    # which is equal to the cardinality of the smaller array
    n = min(len(al1), len(al2))
    score /= n

    return map2, score


def match_ads_author_fields (f1, f2):
    """
    takes as input two lists of structured author names + affiliations, 
    and outputs a single list, where affiliation fields from the second list
    have been inserted to the appropriate elements from the first
    list (based on an approximate match on the author names)
    """
    a1 = [f['name']['western'] for f in f1]
    a2 = [f['name']['western'] for f in f2]

    # match two arrays based on name similarity
    mapping, score = match_author_lists(a1, a2)

    # is score high enough?
    if score < 0.5:
        # print "author match score too low (%f), ignoring matches" % score
        return []

    # print "author match score:", score
    # make sure there are enough elements in f2
    if len(f2) < len(f1):
        # print "Extending array2 with", len(f1) - len(f2), "additional elements"
        f2.extend([None for i in range(len(f1) - len(f2))])

    return [ (f1[i],f2[mapping[i]]) for i in range(len(f1)) ]


def is_suitable_match(a1, a2):
    """
    returns True iff the names of two authors in the input structures are
    close enough
    """
    if not a1 or not a2:
        return False
    name1 = a1['name']['western'] or ''
    name2 = a2['name']['western'] or ''
    name1, name2 = normalize_authors(name1, name2)
    similarity = Levenshtein.ratio(unicode(name1), unicode(name2))
    #print "score: ", similarity, " names: ", name1, name2
    return True if similarity > 0.6 else False
    

# AA - use the maximum weight matching algorithm to come up with best author string
# matching from two unordered lists (this is the bipartite graph assignment problem)
# and then assign the corresponding affiliations to ADS authors
#
# Example usage: 
# python author_match.py 'Accomazzi, Alberto (ADS); Grant, Carolyn S.; Kurtz, Michael' \
#   'Accomazzi, A. (CfA); Krutz, M. (SAO); Grant Stern, C (Harvard)'

if __name__ == "__main__":

    if len(sys.argv) != 3:
        sys.stderr.write("Usage: %s 'aut_string1' 'aut_string2'\n",
                         sys.argv[0]);
        sys.exit(1)

    # the two arrays of author names (in ADS format) may contain affiliations, e.g.
    # 'Accomazzi, Alberto (CfA); Grant, Carolyn S. (Harvard); Kurtz, Michael (SAO)'
    # parse them and map them to the format used by the ADS import pipeline
    p = re.compile(r'(?P<aut>.*?)\s+\((?P<aff>.*)\)')
    a1 = sys.argv[1].split('; ')
    a2 = sys.argv[2].split('; ')
    f1 = []
    f2 = []
    a1aff = a2aff = 0
    a1aut = len(a1)
    a2aut = len(a2)
    for a in a1:
        m = p.match(a)
        name, aff = m.group('aut','aff') if m else (a,'')
        f1.append({'name': {'western': name}, 'affiliations': [aff] if aff else []})
        a1aff += 1 if aff else 0
    for a in a2:
        m = p.match(a)
        name, aff = m.group('aut','aff') if m else (a,'')
        f2.append({'name': {'western': name}, 'affiliations': [aff] if aff else []})
        a2aff += 1 if aff else 0

    print "Aut1 struct:", f1
    print "Aut2 struct:", f2
    print "Number of names in aut1: ", a1aut
    print "Number of names in aut2: ", a2aut
    print "Number of affiliations in aut1: ", a1aff
    print "Number of affiliations in aut2: ", a2aff
    
    if a1aut == a1aff:
        print "all authors in aut1 have affiliations, we're done"
        exit(0)
    elif a2aff == 0:
        print "no affiliations present in aut2, we're done"
        exit(0)
    else:
        print "will try to pick from", a2aff, "affiliations to assign to", a1aut - a1aff, "author names"

    res = match_ads_author_fields(f1, f2)
    
    authors = []
    for author1, author2 in res:
        print "considering:", author1, author2
        if author1 and author2 and \
                not author1['affiliations'] and \
                author2['affiliations'] and \
                is_suitable_match(author1, author2):
            author1['affiliations'] = author2['affiliations']
            print "updated author affiliations:", author1
        authors.append(author1)
                
    print "Final author structure:", authors

