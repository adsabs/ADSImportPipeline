import os,sys
import pymongo
import time
import itertools
import json
import copy

import settings
from rules import merger
from lib import xmltodict
from lib import collections
try:
  from ads.ADSExports import ADSRecords
except ImportError:
  sys.path.append('/proj/ads/soft/python/lib/site-packages')
  from ads.ADSExports import ADSRecords


#This is not in settings because it normalizes the XML schema coming directly from ADSExports;
#Changing this will break the merger logic, as it expects a consistent schema.
NORMALIZE_SCHEMA = {
  'arxivcategories':  lambda d: ensureList(d),
  'keywords':         lambda d: ensureList(d),
  'title':            lambda d: ensureLanguageSchema(d),
  'abstract':         lambda d: ensureLanguageSchema(d),
  'dates':            lambda d: ensureList(d),
  'isbns':            lambda d: ensureList(d),
  'issns':            lambda d: ensureList(d),
  'databases':        lambda d: ensureList(d),
  'bibgroups':        lambda d: ensureList(d),
  'reference':        lambda d: ensureList(d),
  'alternatives':     lambda d: ensureList(d),
  'associates':       lambda d: ensureList(d),
  'links':            lambda d: ensureList(d),
}

def ensureLanguageSchema(item):
  if isinstance(item,basestring):
    L = [{
      '@lang':'en',
      '#text': item
    }]
  else:
    L = ensureList(item)
    for i in L:
      if '@lang' not in i:
        i['@lang'] = 'en'
  return L

def ensureList(item):
  return item if isinstance(item,list) else [item]

def init_db(db,LOGGER,MONGO):
  db[MONGO['COLLECTION']].ensure_index('bibcode',unique=True)

def mongoCommit(records,LOGGER=settings.LOGGER,MONGO=settings.MONGO):
  '''
  Commits records(@type dict) to a mongo
  '''
  if not records:
    return False
  conn = pymongo.MongoClient(host=MONGO['MONGO_URI'])
  db = conn[MONGO['DATABASE']]
  if MONGO['COLLECTION'] not in db.collection_names():
    init_db(db,LOGGER,MONGO)
  collection = db[MONGO['COLLECTION']]
  for r in records:
    assert(r['bibcode'])
    assert(r['JSON_fingerprint'])
    assert(r['metadata'])
    #query = {"bibcode": {"$in": [r['bibcode'] for r in records]}}
    query = {"bibcode": r['bibcode']}
    collection.update(query,r,upsert=True,w=1,multi=False) #w=1 means block all write requests until it has written to the primary
  conn.close()

def findChangedRecords(records,LOGGER=settings.LOGGER,MONGO=settings.MONGO):
  '''
  Finds records in mongodb that need updating.
  Update criteria: JSON_fingerprint field different from the input records
  '''
  if not records:
    LOGGER.debug("No records given")
    return []

  conn = pymongo.MongoClient(host=MONGO['MONGO_URI'])
  db = conn[MONGO['DATABASE']]

  if MONGO['COLLECTION'] not in db.collection_names():
    init_db(db,LOGGER,MONGO)
  collection = db[MONGO['COLLECTION']]
  currentRecords = [(r['bibcode'],r['JSON_fingerprint']) for r in collection.find({"bibcode": {"$in": [rec[0] for rec in records]}})]
  conn.close()
  return list(set([(r[0],r[1]) for r in records]).difference(currentRecords))

def updateRecords(records,LOGGER=settings.LOGGER):

  if not records:
    LOGGER.debug("No records given")
    return []

  targets = dict(records)


  s = time.time()
  records = ADSRecords('full','XML')
  failures = []
  for bibcode in targets.keys():
    try:
      records.addCompleteRecord(bibcode)
    except KeyboardInterrupt:
      raise
    except:
      failures.append(bibcode)
      LOGGER.warning("[%s] ADSRecords failed" % bibcode)
  records = records.export()
  if not records.content:
    return []
  ttc = time.time()-s
  rate = len(targets)/ttc
  if failures:
    LOGGER.warning('ADSRecords failed to retrieve %s records' % len(failures))
  LOGGER.info('ADSRecords took %0.1fs to query %s records (%0.1f rec/s)' % (ttc,len(targets),rate))

  records = ensureList(xmltodict.parse(records.__str__())['records']['record'])
  assert(len(records)==len(targets)-len(failures))

  #Could send these tasks out on a queue
  completeRecords = []
  for r in records:
    #Define top-level schema that will go in mongo
    cr = {
      'bibcode': r['@bibcode'],
      'JSON_fingerprint': targets[r['@bibcode']],
      'metadata' : {},
    }

    #Find metadata blocks that need merging
    metadataCounter = collections.Counter([entry['@type'] for entry in r['metadata']])
    needsMerging = dict([(k,[]) for k,v in metadataCounter.iteritems() if v>1])

    #Iterate over metadata blocks; directly input single defined blocks
    #and build a 'needsMerging' list to merge in the next step
    for metadataBlock in r['metadata']: 
      for field,data in metadataBlock.iteritems():
        if field in NORMALIZE_SCHEMA:
          metadataBlock[field] = NORMALIZE_SCHEMA[field](data)
      if metadataBlock['@type'] not in needsMerging:
        cr['metadata'].update({metadataBlock['@type']:metadataBlock})
      else: #If it shows up more than once, it needs merging.
        needsMerging[metadataBlock['@type']].append(metadataBlock)
    #Now merge the multiply defined metadataBlocks
    for entryType,data in needsMerging.iteritems():
      cr['metadata'].update({entryType:merge(data,r['@bibcode'],entryType,LOGGER)})
    
    #Finally, we have a complete record
    completeRecords.append(cr)

  LOGGER.info('Added %s complete records' % len(completeRecords))
  return completeRecords

def enforceSchema(records,LOGGER=settings.LOGGER):
  '''
  translates schema from ADSRecords to alternative schema
  '''

  return records

def merge(metadataBlocks,bibcode,entryType,LOGGER=settings.LOGGER):
  '''
  Merges multiply defined fields within a list of <metadata> blocks
  Returns a single (merged) <metadata> block
  '''
  fieldsHist = collections.Counter([i for i in list(itertools.chain(*metadataBlocks)) if not i.startswith('@')])
  singleDefinedFields = [k for k,v in fieldsHist.iteritems() if v==1]
  multipleDefinedFields = [k for k,v in fieldsHist.iteritems() if v>1]
  #LOGGER.debug('%s entries in [%s] (type: %s) need merging' % (len(multipleDefinedFields),bibcode,entryType))
  
  #Create intermediate data structure that lets us easily iterate over those fields that merging, and
  #store the necessary metadata for mergingfg
  fields = {}
  for block in metadataBlocks:
    for fieldName,content in block.iteritems():
      if fieldName not in multipleDefinedFields:
        continue
      if fieldName not in fields:
        fields[fieldName] = []
      fields[fieldName].append({
        '@origin':block['@origin'].upper(),
        'content':content,
        'modtime':block.get('modification_time',block.get('creation_time',0))
      })

  #Merge those fields that are multiply defined      
  mergedResults = {}
  for fieldName,data in fields.iteritems():
    result = None
    while len(data) > 1:
      f1 = data.pop()
      f2 = result if result else data.pop()

      result = merger.dispatcher(f1,f2,fieldName) if f1['content'] != f2['content'] else f1['content']
    mergedResults[fieldName] = result

  #Combine all the pieces into the complete <metadata> block
  completeBlock = {
    '@type':entryType,
    '@origin': 'merged',
  }
  singleDefined = dict([(k,v) for block in metadataBlocks for k,v in block.iteritems() if k in singleDefinedFields])
  completeBlock.update(singleDefined)
  completeBlock.update(mergedResults)

  return completeBlock
