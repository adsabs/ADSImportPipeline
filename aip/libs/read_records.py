import os,sys
import json
import time
import timeout_decorator

from aip.libs import xmltodict
from aip.libs import enforce_schema

import adsputils as utils

INIT_LOOKERS_CACHE = None

try:
    import cPickle as pickle
except ImportError:
    import pickle
try:
    from ads.ADSCachedExports import ADSRecords, init_lookers_cache
    from ads.ADSCachedExports import LOGGER as export_logger
    from aip.libs import conversions
except ImportError:
    sys.path.append('/proj/ads/soft/python/lib/site-packages') #TODO: make it configurable
    try:
        from ads.ADSCachedExports import ADSRecords, init_lookers_cache
        from ads.ADSCachedExports import LOGGER as export_logger
        from aip.libs import conversions
        INIT_LOOKERS_CACHE = init_lookers_cache
    except ImportError:
        print "Unable to import ads.ADSExports.ADSRecords!"
        print "We will be unable to query ADS-classic for records!"


logger = utils.setup_logging('read_records')


def canonicalize_records(records, targets=None, ignore_fingerprints=False):
    '''
    Takes a dict of {bibcode:fingerprint} and resolves each bibcode to its canonical.
    
    Finds all alternates associated with that bibcode and constructs the full JSON_fingerprint
    from all of these associated records
    
    Note: Pops from the input dict with no attempt to copy/deepcopy it.
    '''
    
    #TODO(rca): getAlternates is called multiple times unnecessarily
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
            # TODO(rca): decide what to do with canonical != bibcode
            if ignore_fingerprints:
                results.append((canonical, 'ignore'))
            else:
                for b in Converter.getAlternates(canonical):
                    if b in records:
                        fingerprints.append( records.pop(b) )
                results.append( (canonical,';'.join(sorted(fingerprints))) )

    logger.info("Canonicalized/Resolved in %0.1f seconds" % (time.time()-start))
    return results

@timeout_decorator.timeout(120)
def xml_to_dict(adsrecords):
  """
  wrapper for parsing XML
  :param adsrecords: adsrecords object
  """
  return xmltodict.parse(adsrecords.serialize())


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
    bibcodes = []
    for bibcode in targets.keys():
        try:
            logger.debug('addCompleteRecord: %s (%s/%s)' % (bibcode,targets.keys().index(bibcode)+1,len(targets.keys())))
            adsrecords.addCompleteRecord(bibcode,fulltext=True)
            bibcodes.append(bibcode)
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
    
    e = enforce_schema.Enforcer()
    logger.debug("Calling xml_to_dict")
    export = []
    try:
        json_dict = xml_to_dict(adsrecords)
        logger.debug("...xml_to_dict returned.")
        export = e.ensureList(json_dict['records']['record'])
    except timeout_decorator.timeout_decorator.TimeoutError:
        logger.warning("xml_to_dict timed while processing bibcodes: %s" % '|'.join(bibcodes))
        failures.extend(bibcodes)
    except xml.parsers.expat.ExpatError:
        logger.warning("XML parsing error while processing bibcodes: %s" % '|'.join(bibcodes))
        failures.extend(bibcodes)
    finally:
        adsrecords.freeDoc() #always release memory

    logger.info("Read %(num_records)s records in %(duration)0.1f seconds (%(rate)0.1f rec/sec)" % 
      {
        'num_records': len(records),
        'duration': ttc,
        'rate': rate,
      })
    if failures:
        logger.warning("ADSExports failed to retrieve %s/%s records" % (len(failures),len(records)))
    
    results = []
    for r in export:
        r = e.enforceTopLevelSchema(record=r, JSON_fingerprint=targets[r['@bibcode']])
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
    
    e = enforce_schema.Enforcer()
    for r in records:
        r = e.enforceTopLevelSchema(record=r,JSON_fingerprint=targets[r['@bibcode']])
        r['metadata'] = e.enforceMetadataSchema(r['metadata'])
        #r['text'] = e.enforceTextSchema() TODO, once implemneted in ADSExports
    logger.info('readRecordsFromPickles: Read %s records from %s files' % (len(records),len(files)))
    return records


def findNewRecords(records):
    '''
    Finds records that need updating.
    
    @param records: [(bibcode, json_fingeprints),...]
    
    Update criteria: JSON_fingerprint field different from the input records

    @return: [(bibcode,JSON_fingerprint),...]
    '''
    if not records:
        logger.debug("findChangedRecords: No records given")
        return []

    currentRecords = [(r['bibcode'],r['JSON_fingerprint']) for r in self.db[self.collection].find({"bibcode": {"$in": [rec[0] for rec in records]}})]

    #If the JSON fingerprint is the string 'ignore' and it isnt marked for updated,
    #Make sure it gets updated anyways.
    if any(r[1]=='ignore' for r in records):
      if any(r[1]!='ignore' for r in records):
        self.logger.warning("Unexpected of mixture of JSON ignore/unignore'd in this payload! Proceed with ignore strategy")
      results = []
      for r in records:
        if r[0] not in results:
          if r[0] in [i[0] for i in currentRecords]:
            results.append(filter(lambda t: t[0]==r[0], currentRecords)[0])
          else:
            results.append(r)
      return results

    results = list(set([(r[0],r[1]) for r in records]).difference(currentRecords))

    self.logger.info('findChangedRecords: %s results' % len(results))
    return results
