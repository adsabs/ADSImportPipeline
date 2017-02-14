#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import sys
import os
import requests
import argparse
import json
import cPickle as pickle
import logging
import logging.handlers

# python compare_solrs.py --solr-endpoints http://adsqb.cfa.harvard.edu:9983/solr/BumblebeeETL/select http://adsqb.cfa.harvard.edu:9983/solr/collection1/select --bibcode stdin fields < testBibcodes.txt


# set up logging
logfmt = '%(levelname)s\t%(process)d [%(asctime)s]:\t%(message)s'
datefmt= '%m/%d/%Y %H:%M:%S'
formatter = logging.Formatter(fmt=logfmt,datefmt=datefmt)
LOGGER = logging.getLogger(__file__)
fn = os.path.join(os.path.dirname(__file__),'../logs','%s.log' % 'compare_solrs')   
rfh = logging.handlers.RotatingFileHandler(filename=fn,maxBytes=2097152,backupCount=3,mode='a') #2MB file
rfh.setFormatter(formatter)
ch = logging.StreamHandler() #console handler
ch.setFormatter(formatter)
LOGGER.addHandler(ch)
LOGGER.addHandler(rfh)
LOGGER.setLevel(logging.DEBUG)
logger = LOGGER


SOLR1_PATH = 'http://localhost:9000/solr/select/'
SOLR2_PATH = 'http://localhost:8900/solr/select/'


def query_solr(
    endpoint,
    query,
    start=0,
    rows=200,
    sort='date desc',
    fl=None,
    ):
    d = {
        'q': query,
        'sort': sort,
        'start': start,
        'rows': rows,
        'wt': 'json',
        'indent': 'true',
        'hl': 'true',
        'hl.fl': 'abstract,ack,body',
        }
    if fl:
        d['fl'] = fl
    if fl:
        d['fl'] = fl
    response = requests.get(endpoint, params=d)
    if response.status_code == 200:
        results = response.json()
        return results
    sys.exit('There was a network problem: {0}\n'.format(response))


def parseDocs(result):

  # route: result[endpoint]['response']['docs'] @type list

    assert len(result) == 2
    data = {}
    for endpoint in result:
        docs = result[endpoint]['response']['docs']
        for doc in docs:
            b = doc['bibcode']
            if b not in data:
                data[b] = {}
            data[b][endpoint] = doc
            print b, endpoint, data.keys()

    with open('pickle', 'w') as fp:
        pickle.dump(data, fp)
    return data



def compare_fields(result1, result2):
  mismatches = []
  if not ('response' in result1 and 'docs' in result1['response'] and len(result1['response']['docs']) > 0):
    message = 'invalid response first solr' + str(result1)
    print message
    logger.error(message)
    mismatches.append('invalid response first solr')
    return mismatches
  if not ('response' in result2 and 'docs' in result2['response'] and len(result1['response']['docs']) > 0):
    message = 'invalid response second solr' + str(result2)
    print message
    logger.error(message)
    mismatches.append('invalid response second solr')
    return mismatches
  
  doc1 = result1['response']['docs'][0]
  doc2 = result2['response']['docs'][0]
  bibcode = doc1['bibcode']  # needed for log messages
  
  # the following fields can't be expected to match so should not be compared
  skip = ['id', 'recid', '_version_', 'indexstamp', 'classic_factor']
  error_count = 0
  for key in doc1.keys():
    if key not in skip:
      if key not in doc2:
        message = 'bibcode {} has no value for key {}, value from first solr {}'.format(bibcode, key, doc1[key])
        print message
        logger.warn(message)
        continue
      if doc1[key] != doc2[key]:
        if isnumber(doc1[key]) and isnumber(doc2[key]):
          # allow numeric values to only almost match
          value1 = float(doc1[key])
          value2 = float(doc2[key])
          delta = abs(value1 - value2)
          if delta > (value1 * .1) and delta > .15:
            error_count += 1
            message = u'bibcode = {}, key mismatch {} on values {}, {}'.format(bibcode, key, doc1[key], doc2[key])
            print message
            mismatches.append(key)
            logger.warn(message)
          else:
            message = u'bibcode = {}, key {} delta within threshold on values {}, {}'.format(bibcode, key, unicode(value1).encode('unicode-escape'), unicode(value2).encode('unicode-escape'))
            print message
            logger.warn(message)
        elif isinstance(doc1[key], list) and isinstance(doc2[key], list):
          # do not require arrays to have elements in the same order?
          if doc1[key].sort() != doc2[key].sort():
            message = u'bibcode = {} array values mismatch, {}, {}'.format(bibcode, doc1[key], doc2[key])
            mismatches.append(key)
        else:
          error_count += 1
          message = u'bibcode = {}, key mismatch {} on values {}, {}'.format(bibcode, key, unicode(doc1[key]).encode('unicode-escape'), unicode(doc2[key]).encode('unicode-escape'))
          print message
          mismatches.append(key)
          logger.warn(message)
  
  return mismatches

def isnumber(arg):
  try:
    val = float(arg)
    return True
  except TypeError:
    return False
  except ValueError:
    return False
  
def query_and_compare(bibcode, endpoint1, endpoint2):
  the_filter = 'bibcode:{}'.format(bibcode)
  query = "*"
  result = {}
  result1 = query_solr(endpoint1, query, the_filter=the_filter, fl='*')
  result2 = query_solr(endpoint2, query, the_filter=the_filter, fl='*')
  failure = compare_fields(result1, result2)
  if len(failure) > 0:
    message = 'bibcode {} failed with {} errors: {}'.format(bibcode, len(failure), failure)
    logger.error(message)
    print message
  else:
    message = 'bibcode {} success'.format(bibcode)
    logger.info(message)
    print message

  return failure

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', help='bibcodes | fields')
    
    parser.add_argument(
        '--solr-endpoints',
        nargs=2,
        dest='solr_endpoints',
        default = [SOLR1_PATH,SOLR2_PATH],
        help="define two solr endpoints"
        )

    parser.add_argument(
        '--query',
        nargs=1,
        default='star',
        type=str,
        dest='query',
        help='"q=" parameter'
        )

    parser.add_argument(
        '--bibcode',
        nargs=1,
        default='2003ASPC..295..361M',
        type=str,
        dest='bibcode',
        help='compare fields of two solr instances for this bibcode'
        )

    args = parser.parse_args()

    if args.command == 'bibcodes':
        # do the two solrs have the same bibcodes
        result = {}
        for endpoint in args.solr_endpoints:
            result[endpoint]=query_solr(endpoint,args.query)

        data = parseDocs(result)
        for bibcode in data:
            print data[bibcode].keys()
            print "Difference in keys:\n",'\n'.join(set(data[bibcode][args.solr_endpoints[0]].keys()).difference(data[bibcode][args.solr_endpoints[1]].keys()))
        
    elif args.command == 'fields':
        # for the passed bibcode, do the two solrs contain the same values
        if args.bibcode[0] == 'stdin':
            while True:
                line = sys.stdin.readline()
            if len(line) == 0: break
            bibcode = line.strip()
            mismatch = query_and_compare(bibcode, args.solr_endpoints[0], args.solr_endpoints[1])
            if mismatch:
                print 'mismatch on bibcode {}'.format(bibcode)
            else:
                failure = query_and_compare(args.bibcode, args.solr_endpoints[0], args.solr_endpoints[1])
    else:
        print 'no command supplied'
        print 'use "bibcoces" to see if two solrs have the same bibcodes'
        print 'use "fields" to compare fields for the passed bibcodes match between solrs'

if __name__ == '__main__':    
  main()
