import sys,os
from settings import (MERGER_RULES,PRIORITIES,REFERENCES_ALWAYS_APPEND)
import types
import itertools
import logging
import collections

from lib import EnforceSchema

class Merger:
  def __init__(self,blocks,logger=None):
    self.blocks = blocks
    self.logger=logger
    self.block = {}
    self.altpublications = []
    #Assert that there is only block type being merged
    assert len(set([i['tempdata']['type'] for i in blocks]))==1
    self.blocktype = blocks[0]['tempdata']['type']
    self.eL = EnforceSchema.Enforcer().ensureList
    if not self.logger:
      self.initializeLogging()

  def initializeLogging(self,**kwargs):
    logfmt = '%(levelname)s\t%(process)d [%(asctime)s]:\t%(message)s'
    datefmt= '%m/%d/%Y %H:%M:%S'
    formatter = logging.Formatter(fmt=logfmt,datefmt=datefmt)
    LOGGER = logging.getLogger(__file__)
    default_fn = os.path.join(os.path.dirname(__file__),'..','logs','%s.log' % self.__class__.__name__)   
    fn = kwargs.get('filename',default_fn)
    rfh = logging.handlers.RotatingFileHandler(filename=fn,maxBytes=2097152,backupCount=3,mode='a') #2MB file
    rfh.setFormatter(formatter)
    ch = logging.StreamHandler() #console handler
    ch.setFormatter(formatter)
    LOGGER.addHandler(ch)
    LOGGER.addHandler(rfh)
    LOGGER.setLevel(logging.DEBUG)
    self.logger = LOGGER

  def _dispatcher(self,field):
    if field not in MERGER_RULES:
      field = 'default'
    return eval('self. '+ MERGER_RULES[field])(field)

  def merge(self):
    fieldsHist = collections.Counter([i for i in list(itertools.chain(*self.blocks)) if i!='tempdata'])
    singleDefinedFields = [k for k,v in fieldsHist.iteritems() if v==1]
    multipleDefinedFields = [k for k,v in fieldsHist.iteritems() if v>1]
    r = {}
    # First pass: construct the record from singly defined fields
    for field in singleDefinedFields:
      for block in self.blocks:
        if field in block:
          r[field] = block[field]
    # Second pass: merge the multiply defined fields
    for field in multipleDefinedFields:
      try:
        r[field] = self._dispatcher(field)
      except:
        self.logger.error('Merger: some error with dispatcher on %s' % field)
        raise
    self.block = r
    self.block['altpublications'] = self.altpublications

  def authorMerger(self,field='authors'):
    data = [ [i[field],i['tempdata']] for i in self.blocks if field in i]
    result = None
    while len(data) > 0:
      f1 = data.pop()
      f2 = result if result else data.pop()
      result = self._getBestOrigin(f1,f2,'authors')
      for author in result[0]:
        if 'affiliations' not in author:
          _all = f1[0]+f2[0]
          matches = [i for i in _all if i['name']['normalized']==author['name']['normalized'] and 'affiliations' in i]
          #TODO: levenstein word distance fallback if no matches
          #In the case that a there are multiple authors with the same normalized name in the list, matches will have len>1.
          #This will blindly pick the first one that matched, which isn't necessarily correct.
          if matches:
            author['affiliations'] = matches[0]['affiliations']
    return result

  def booleanMerger(self,field):
    if any([i[field] for i in self.blocks if field in i]):
      return True
    return False

  def referencesMerger(self,field='references'):
    data = [ (i[field],i['tempdata']) for i in self.blocks if field in i]
    result = None
    #First pass: OriginTrust
    while len(data) > 0:
      f1 = data.pop()
      f2 = result if result else data.pop()
      result = list(self._getBestOrigin(f1,f2,'references'))
    #Second pass: append if the origin is in REFERENCES_ALWAYS_APPEND
    data = [ (i[field],i['tempdata']) for i in self.blocks if field in i]
    for f in data:
      if f[1]['origin'] in REFERENCES_ALWAYS_APPEND:
        result.append(f[0])
    return result

  def publicationMerger(self,field):
    primaries = [ (i['publication'],i['tempdata']) for i in self.blocks if not i['tempdata']['alternate_journal'] ]
    alternates = [ i['publication'] for i in self.blocks if i['tempdata']['alternate_journal'] ]
    assert len(primaries)+len(alternates) == len(self.blocks)

    self.altpublications = alternates if alternates else []
    result = None
    while len(primaries) > 0:
      f1 = primaries.pop()
      f2 = result if result else primaries.pop()
      result = self._getBestOrigin(f1,f2,'journals')
    return result

  def takeAll(self,field):
    r = []
    r.extend( [i[field] for i in self.blocks if field in i] )
    return r

  def _getBestOrigin(self,f1,f2,field):
    if field not in PRIORITIES:
      p = PRIORITIES['default']
    else:
      p = PRIORITIES[field]
    #TODO: we should pick the one with the highest origin instead of the first one.
    o1 = f1[1]['origin'] if f1[1]['origin'] in p else f1[1]['origin'].split(';')[0]
    o2 = f2[1]['origin'] if f2[1]['origin'] in p else f2[1]['origin'].split(';')[0]
    P1 = p[o1.upper()]
    P2 = p[o2.upper()]
    if P1==P2:
      return self.equalTrustFallback(f1,f2)
    return f1 if P1 > P2 else f2

  def originTrustMerger(self,field):
    data = [ (i[field],i['tempdata']) for i in self.blocks if field in i]
    result = None
    while len(data) > 0:
      f1 = data.pop()
      f2 = result if result else data.pop()
      result = self._getBestOrigin(f1,f2,field)
    return result[0]

  def equalTrustFallback(self,f1,f2):
    #1. Priority
    if f1[1]['primary'] and not f2[1]['primary']:
      return f1
    if f2[1]['primary'] and not f1[1]['primary']:
      return f2
    #2. Same origin, diff modtime -> latest modtime
    if f1[1]['origin']==f2[1]['origin'] and f1[1]['modtime'] != f2[1]['modtime']:
      return f1 if f1[1]['modtime'] > f2[1]['modtime'] else f2
    #3. Length of content
    if len(f1[0]) != len(f2[0]):
      return f1 if len(f1[0]) > len(f2[0]) else f2
    #4. latest modtime (regardless of origins)
    if f1[1]['modtime'] != f2[1]['modtime']:
      return f1 if f1[1]['modtime'] > f2[1]['modtime'] else f2
    #5. Doesn't matter anymore. Return one of them.
    return f1