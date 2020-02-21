
#!/usr/bin/env python
import sys
sys.path.append('/proj/ads/soft/python/lib/site-packages')
import ads
from ads.Looker import Looker

class ConvertBibcodes:

    def __init__(self):
        self.bib2alt = Looker(ads.alternates).look
        self.bib2epr = Looker(ads.pub2arx).look
        self.alt2bib = Looker(ads.altlist).look
        self.epr2bib = Looker(ads.ematches).look

    def getAlternates(self,bbc):
        """
	Returns a list of alternate bibcodes for a record.
        """
        if isinstance(bbc, list):
            bibcode = bbc[0].strip()
        else:
            bibcode = bbc.strip()
        alternates = []
        res = self.bib2alt(bibcode).strip()
        rez = self.bib2epr(bibcode).strip()
        if res:
            for line in res.split('\n'):
                alternate = line.split('\t')[1]
                if alternate != bibcode:
                    alternates.append(alternate)
        if rez:
            alternates.append(rez.strip().split('\n')[0].split('\t')[1])

        return alternates

    def Canonicalize(self,biblist,remove_matches=False):
        """
	    Convert a list of bibcodes into a list of canonical
        bibcodes (canonical bibcodes remain unchanged).
        Setting 'remove_matches' to True will remove e-print
        bibcodes that have been matched
        """
        if isinstance(biblist, str):
            biblist = [biblist]
        newlist = []
        for bibcode in biblist:
            res = self.alt2bib(bibcode).strip()
            rez = self.epr2bib(bibcode).strip()
            if res:
                bibcode = res.strip().split('\n')[0].split('\t')[1]
            elif rez and remove_matches:
                bibcode = ''
            elif rez:
                bibcode = rez.strip().split('\n')[0].split('\t')[1]
            if bibcode:
                newlist.append(bibcode)
        return list(set(newlist))

