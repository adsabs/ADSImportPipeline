import sys,os
from settings import (MERGER_RULES,PRIORITIES,REFERENCES_ALWAYS_APPEND)
import types
import itertools
import logging
import collections

from lib import EnforceSchema

class Merger:
  def __init__(self,blocks=None,logger=None):
    self.blocks = blocks
    self.logger=logger
    self.block = {}
    self.altpublications = []
    self.eL = EnforceSchema.Enforcer().ensureList
    if blocks:
      #Assert that there is only block type being merged
      assert len(set([i['tempdata']['type'] for i in blocks]))==1
      self.blocktype = blocks[0]['tempdata']['type']
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
      self.logger.error("%s not in MERGER_RULES" % field)
      raise
    return eval('self. '+ MERGER_RULES[field])(field)


  def mergeText(self,blocks):
    mergedBlock = {}
    #Order matters here; we prioritize data coming from body over acknow.
    fields = ['acknowledgement','body']
    for f in fields:
      mergedBlock[f] = {}
      if len(blocks[f])<2:
        result = blocks[f][0] if blocks[f] else {}
        blocks[f] = result
      else:
        result = None
        data = [ (i,i['tempdata']) for i in blocks[f]]
        while len(data) > 0:
          f1 = data.pop()
          f2 = result if result else data.pop()
          result = self._getBestOrigin(f1,f2,'default')
        result = result[0]
      mergedBlock[f]['content'] = result.get('content')
      mergedBlock[f]['provider'] = result.get('provider')
      mergedBlock[f]['modtime'] = result.get('modtime')

    return mergedBlock


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
      except Exception, err:
        self.logger.error('Error with merger dispatcher on %s: %s' % (field,err))
    self.block = r
    if self.altpublications:
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
    return result[0]

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
      result = self._getBestOrigin(f1,f2,'references')
    result = list(result[0])
    #Second pass: append if the origin is in REFERENCES_ALWAYS_APPEND
    data = [ (i[field],i['tempdata']) for i in self.blocks if field in i]
    for f in data:
      if f[1]['origin'] in REFERENCES_ALWAYS_APPEND:
        result.append(f[0])
    return result

  def publicationMerger(self,field):
    primaries = [({
        'origin':         i['publication']['origin'],
        'issue':          i['publication']['issue'],
        'page':           i['publication']['page'],
        'page_last':      i['publication']['page_last'],
        'page_range':     i['publication']['page_range'],
        'page_count':     i['publication']['page_count'],
        'electronic_id':  i['publication']['electronic_id'],
        'name':           i['publication']['name'],
        'dates':           i['publication']['dates'],
      },i['tempdata']) for i in self.blocks if not i['tempdata']['alternate_journal'] ]    

    altpublications = [{
        'origin':         i['publication']['origin'],
        'issue':          i['publication']['issue'],
        'page':           i['publication']['page'],
        'page_last':      i['publication']['page_last'],
        'page_range':     i['publication']['page_range'],
        'page_count':     i['publication']['page_count'],
        'electronic_id':  i['publication']['electronic_id'],
        'name':           i['publication']['name'],
        'dates':           i['publication']['dates'],
    } for i in self.blocks if i['tempdata']['alternate_journal'] ]

    self.altpublications = altpublications

    assert len(primaries)+len(altpublications) == len(self.blocks)

    if len(primaries) == 1:
      return primaries[0][0]

    result = None
    while len(primaries) > 0:
      f1 = primaries.pop()
      f2 = result if result else primaries.pop()
      result = self._getBestOrigin(f1,f2,'journals')

    return result[0]


  def takeAll(self,field):
    r = []
    for i in [j for j in self.blocks if field in j]:
      r.extend(i[field])
    r = [i for i in r if i]
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
