import json
import sys
import requests
import argparse
import json
import cPickle as pickle

SOLR1_PATH =  'http://localhost:9000/solr/select/'
SOLR2_PATH =  'http://localhost:8900/solr/select/'

def query_solr(endpoint, query, start=0, rows=200, sort="date desc", fl=None):
  d = {
    'q' : query,
    'sort': sort,
    'start' : start,
    'rows' : rows,
    'wt': 'json',
    'indent': 'true',
    'hl': 'true',
    'hl.fl':'abstract,ack,body',
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
  #route: result[endpoint]['response']['docs'] @type list
  assert len(result)==2
  data = {}
  for endpoint in result:
    docs = result[endpoint]['response']['docs']
    for doc in docs:
      b = doc['bibcode']
      if b not in data:
        data[b] = {}
      data[b][endpoint] = doc
      print b,endpoint,data.keys()

  with open('pickle','w') as fp:
    pickle.dump(data,fp)
  return data

def main():
  parser = argparse.ArgumentParser()
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

  args = parser.parse_args()

  result = {}
  for endpoint in args.solr_endpoints:
    result[endpoint]=query_solr(endpoint,args.query)

  data = parseDocs(result)
  for bibcode in data:
    print data[bibcode].keys()
    print "Difference in keys:\n",'\n'.join(set(data[bibcode][args.solr_endpoints[0]].keys()).difference(data[bibcode][args.solr_endpoints[1]].keys()))

if __name__ == '__main__':    
  main()