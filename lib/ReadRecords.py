import os,sys
import json
import time
import logging
import logging.handlers
#import hashlib

from lib import xmltodict
from lib import collections
from lib import EnforceSchema

try:
  import cPickle as pickle
except ImportError:
  import pickle
try:
  from ads.ADSCachedExports import ADSRecords, init_lookers_cache
  from lib import conversions
except ImportError:
  sys.path.append('/proj/ads/soft/python/lib/site-packages')
  try:
    from ads.ADSCachedExports import ADSRecords, init_lookers_cache
    from lib import conversions
  except ImportError:
    print "Unable to import ads.ADSExports.ADSRecords!"
    print "We will be unable to query ADS-classic for records!"

INIT_LOOKERS_CACHE = init_lookers_cache

logfmt = '%(levelname)s\t%(process)d [%(asctime)s]:\t%(message)s'
datefmt= '%m/%d/%Y %H:%M:%S'
formatter = logging.Formatter(fmt=logfmt,datefmt=datefmt)
logger = logging.getLogger('ReadRecords')
if not logger.handlers:
  fn = os.path.join(os.path.dirname(__file__),'..','logs','ReadRecords.log')
  rfh = logging.handlers.RotatingFileHandler(filename=fn,maxBytes=2097152,backupCount=10,mode='a') #2MB file
  rfh.setFormatter(formatter)
  ch = logging.StreamHandler() #console handler
  ch.setFormatter(formatter)
#  logger.addHandler(ch)
  logger.addHandler(rfh)
logger.setLevel(logging.INFO)

def canonicalize_records(records,targets=None):
  '''
  Takes a dict of {bibcode:fingerprint} and resolves each bibcode to its canonical.

  Finds all alternates associated with that bibcode and constructs the full JSON_fingerprint
  from all of these associated records

  Note: Pops from the input dict with no attempt to copy/deepcopy it.
  '''

  start = time.time()
  results = []

  if not targets:
    targets = records
  Converter = conversions.ConvertBibcodes()
  for bibcode,fingerprint in targets.iteritems():
    fingerprints = [fingerprint] #Start constructing the "full" fingerprint
    #Check if there is a canonical
    canonical=Converter.Canonicalize([bibcode])[0]
    #If we are operating on the canonical, aggregate all of its alternates to form the "full" fingerprint
    if canonical == bibcode:
      for b in Converter.getAlternates(canonical):
        if b in records:
          fingerprints.append( records.pop(b) )
      results.append( (canonical,';'.join(sorted(fingerprints))) )
  
  logger.info("Canonicalized/Resolved in %0.1f seconds" % (time.time()-start))
  return results


def readRecordsFromADSExports(records):
  '''
  records: [(bibcode,JSON_fingerprint),...]
  '''
  #h = hashlib.sha1(json.dumps(records)).hexdigest()
  if not records:
    return []

  targets = dict(records)

  s = time.time()
  failures = []
  adsrecords = ADSRecords('full','XML',cacheLooker=True)
  for bibcode in targets.keys():
    try:
      logger.debug('addCompleteRecord: %s (%s/%s)' % (bibcode,targets.keys().index(bibcode)+1,len(targets.keys())))
      adsrecords.addCompleteRecord(bibcode,fulltext=True)
      #adsrecords.addCompleteRecord(bibcode)
    except KeyboardInterrupt:
      raise
    except Exception, err:
      failures.append(bibcode)
      logger.warning('ADSExports failed: %s (%s)' % (bibcode,err))
  logger.debug("Calling ADSRecords.export()")
  adsrecords = adsrecords.export()
  logger.debug("...ADSRecords.export() returned.")
  if not adsrecords.content:
    logger.warning('Recieved %s records, but ADSExports didn\'t return anything!' % len(records))
    return []
  ttc = time.time()-s
  rate = len(targets)/ttc

  e = EnforceSchema.Enforcer()
  adsrecords = e.ensureList(xmltodict.parse(adsrecords.serialize())['records']['record'])
  logger.info("Read %(num_records)s records in %(duration)0.1f seconds (%(rate)0.1f rec/sec)" % 
    {
      'num_records': len(records),
      'duration': ttc,
      'rate': rate,
    })
  if failures:
    logger.warning("ADSExports failed to retrieve %s/%s records" % (len(failures),len(records)))

  results = []
  for r in adsrecords:
    r = e.enforceTopLevelSchema(record=r,JSON_fingerprint=targets[r['@bibcode']])
    r['metadata'] = e.enforceMetadataSchema(r['metadata'])
    results.append(r)
  return results

def readRecordsFromPickles(records,files):
  '''
  records: [(bibcode,JSON_fingerprint),...]
  '''
  if not records:
    return []
  targets = dict(records)
  records = []

  for file_ in files:
    with open(file_) as fp:
      recs = pickle.load(fp)

  records.extend( [r for r in recs if r['@bibcode'] in targets] )

  for r in records:
    r = e.enforceTopLevelSchema(record=r,JSON_fingerprint=targets[r['@bibcode']])
    r['metadata'] = e.enforceMetadataSchema(r['metadata'])
    #r['text'] = e.enforceTextSchema() TODO, once implemneted in ADSExports
  logger.info('readRecordsFromPickles: Read %s records from %s files' % (len(records),len(files)))
  return records
