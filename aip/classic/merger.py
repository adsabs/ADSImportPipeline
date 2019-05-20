import collections
import copy
import datetime
import itertools
import os
import sys
import types

from aip.classic import enforce_schema, author_match
import adsputils as utils

_config = utils.load_config()

def mergeRecords(records):
    completeRecords = []
    e = enforce_schema.Enforcer() # TODO: no need to create new instances?
    for r in copy.deepcopy(records):
        r['text'] = Merger().mergeText(r['text'])
        blocks = e.ensureList(r['metadata'])
        #Multiply defined blocks need merging.
        metadatablockCounter = collections.Counter([i['tempdata']['type'] for i in blocks])
        needsMerging = dict([(k,[]) for k,v in metadatablockCounter.iteritems() if v>1])
    
        completeMetadata = {}
        #First pass: Add the singly defined blocks to the complete record
        for b in blocks:
            _type = b['tempdata']['type']
            if _type not in needsMerging:
                completeMetadata[_type] = b
            else:
                needsMerging[_type].append(b)
    
    #Second pass: Merge the multiple defined blocks
    for _type,blocks in needsMerging.iteritems():
        m = Merger(blocks)
        m.merge()
        completeMetadata.update({
          _type: m.block,
        })
    
    #Finally, we have a complete record
    r['metadata'] = completeMetadata
    completeRecords.append(e.finalPassEnforceSchema(r))
    return completeRecords


class Merger:
  def __init__(self, 
               blocks=None, 
               logger=None, 
               merger_rules= _config['MERGER_RULES'],
               priorities = _config['PRIORITIES'],
               references_always_append = _config['REFERENCES_ALWAYS_APPEND']
               ):
    self.blocks = blocks
    self.logger=logger
    self.block = {}
    self.altpublications = []
    self.eL = enforce_schema.Enforcer().ensureList
    self.merger_rules = merger_rules
    self.priorities = priorities
    self.references_always_append = references_always_append
    
    if blocks:
      #Assert that there is only block type being merged
      assert len(set([i['tempdata']['type'] for i in blocks]))==1
      self.blocktype = blocks[0]['tempdata']['type']
    if not self.logger:
      self.logger = utils.setup_logging('merger')


  def _dispatcher(self, field):
    if field not in self.merger_rules:
        self.logger.error("%s not in MERGER_RULES" % field)
        raise Exception("%s not in MERGER_RULES" % field)
    return eval('self. '+ self.merger_rules[field])(field) #rca: eeeek!


  def mergeText(self,blocks):
    mergedBlock = {}
    #Order matters here; we prioritize data coming from body over acknow.
    fields = ['acknowledgement']
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
    fieldsHist = {}
    for fieldName in [i for i in list(itertools.chain(*self.blocks)) if i != 'tempdata']:
      fieldsHist[fieldName] = 0
      for block in self.blocks:
        if fieldName in block:
          fieldsHist[fieldName] += 1
    singleDefinedFields = [k for k,v in fieldsHist.iteritems() if v==1]
    multipleDefinedFields = [k for k,v in fieldsHist.iteritems() if v>1]
    r = {}
    # First pass: construct the record from singly defined fields
    for field in singleDefinedFields:
      for block in self.blocks:
        if block[field]:
          r[field] = block[field]
    # Second pass: merge the multiply defined fields
    for field in multipleDefinedFields:
      try:
        r[field] = self._dispatcher(field)
      except Exception, err:
        self.logger.error('Error with merger dispatcher on %s: %s' % (field,err))
        raise
    self.block = r
    if self.blocktype == 'general':
      self.block['altpublications'] = self.altpublications

  def authorMerger(self,field='authors'):
    data = [ [i[field],i['tempdata']] for i in self.blocks if field in i]
    result = None
    while len(data) > 0:
      f1 = data.pop()
      f2 = result if result else data.pop()
      result = self._getBestOrigin(f1,f2,'authors')
      other = f2 if result == f1 else f1

      #Only do the matching if at least one of the the bestOrigin authors lacks an affiliation
      #AND the other author field has at least one
      if not all( [i['affiliations'] for i in result[0]] ) and\
            any( [i['affiliations'] for i in other[0]] ):
        best_matches = author_match.match_ads_author_fields(result[0],other[0])
        for match in best_matches:
          if not author_match.is_suitable_match(*match):
            continue
          if not match[0]['affiliations'] and match[1]['affiliations']:
            match[0]['affiliations'] = match[1]['affiliations']
        result = [[i[0] for i in best_matches],result[1]]
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
      if f[1]['origin'] in self.references_always_append:
        for reference in f[0]:
          if reference not in result:
            result.append(reference)
    return result

  def publicationMerger(self,field):
    primaries = [({
        'origin':         i['publication']['origin'],
        'volume':         i['publication']['volume'],
        'issue':          i['publication']['issue'],
        'page':           i['publication']['page'],
        'page_last':      i['publication']['page_last'],
        'page_range':     i['publication']['page_range'],
        'page_count':     i['publication']['page_count'],
        'series':         i['publication'].get('series', None),
        'altbibcode':     i['publication']['altbibcode'],
        'electronic_id':  i['publication']['electronic_id'],
        'name':           i['publication']['name'],
        'dates':          i['publication']['dates'],
      },i['tempdata']) for i in self.blocks if not i['tempdata']['alternate_journal'] ]    

    altpublications = [{
        'origin':         i['publication']['origin'],
        'volume':         i['publication']['volume'],
        'issue':          i['publication']['issue'],
        'page':           i['publication']['page'],
        'page_last':      i['publication']['page_last'],
        'page_range':     i['publication']['page_range'],
        'page_count':     i['publication']['page_count'],
        'series':         i['publication'].get('series', None),
        'altbibcode':     i['publication']['altbibcode'],
        'electronic_id':  i['publication']['electronic_id'],
        'name':           i['publication']['name'],
        'dates':          i['publication']['dates'],
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
    def deDuplicated(L):
      #This will still consider 'origin' in the comparison
      result = []
      for i in L:
        if i not in result:
          result.append(i)
      return result

    r = []
    for i in [j for j in self.blocks if field in j]:
      if i[field] and i[field] not in r:
        r.extend(i[field])

    return deDuplicated(r)

  def _getBestOrigin(self,f1,f2,field):
    #If one of the two fields has empty content, return the one with content
    if not all([f1[0],f2[0]]) and any([f1[0],f2[0]]):
      return f1 if f1[0] else f2

    if field not in self.priorities:
      p = self.priorities['default']
    else:
      p = self.priorities[field]
    # pick the origin with the highest priority for each record
    origins = f1[1]['origin'].split('; ')
    o1 = origins.pop()
    for i in origins:
      o1 = i if p.get(i.upper(),0) >= p.get(o1.upper(),0) else o1
    origins = f2[1]['origin'].split('; ')
    o2 = origins.pop()
    for i in origins:
      o2 = i if p.get(i.upper(),0) >= p.get(o2.upper(),0) else o2
    # if origin not defined, default to 'PUBLISHER'
    P1 = p.get(o1.upper(),p.get('PUBLISHER'))
    P2 = p.get(o2.upper(),p.get('PUBLISHER'))
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

    dt_1 = self.want_datetime(f1[1]['modtime'])
    dt_2 = self.want_datetime(f2[1]['modtime'])
    #2. Same origin, diff modtime -> latest modtime
    if f1[1]['origin']==f2[1]['origin'] and dt_1 != dt_2:
      return f1 if dt_1 > dt_2 else f2
    #3. Length of content
    if len(f1[0]) != len(f2[0]):
      return f1 if len(f1[0]) > len(f2[0]) else f2
    #4. latest modtime (regardless of origins)
    if dt_1 != dt_2:
      return f1 if dt_1 > dt_2 else f2
    #5. Doesn't matter anymore. Return one of them.
    return f1

  def want_datetime(self,obj):
    if isinstance(obj,datetime.date):
      return obj
    date_format = '%Y-%m-%dT%H:%M:%SZ'
    obj_str = str(obj) 
    if obj_str[-1] != 'Z':  # hack, Z seems is often missing
      date_format = '%Y-%m-%dT%H:%M:%S'
    elif '.' in obj_str:
      date_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    try:
      try:
        return datetime.datetime.fromtimestamp(int(obj))
      except ValueError:
        return datetime.datetime.strptime(obj, date_format)
    except Exception as e:
      self.logger.warning('Error coercing {0} to a datetime. Returning datetime.now(): {1}'.format(obj,e))
      return datetime.datetime.now() # Should return something that has __cmp__ defined
