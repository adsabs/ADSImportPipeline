import requests
import argparse
import json
import requests
import logging
import logging.handlers
import os

from lib import MongoConnection
from settings import MONGO

logfmt = '%(levelname)s\t%(process)d [%(asctime)s]:\t%(message)s'
datefmt= '%m/%d/%Y %H:%M:%S'
formatter = logging.Formatter(fmt=logfmt,datefmt=datefmt)
LOGGER = logging.getLogger(__file__)
fn = os.path.join(os.path.dirname(__file__),'..','logs','SolrUpdater.log')   
rfh = logging.handlers.RotatingFileHandler(filename=fn,maxBytes=2097152,backupCount=3,mode='a') #2MB file
rfh.setFormatter(formatter)
ch = logging.StreamHandler() #console handler
ch.setFormatter(formatter)
LOGGER.addHandler(ch)
LOGGER.addHandler(rfh)
LOGGER.setLevel(logging.DEBUG)
logger = LOGGER

class SolrAdapter(object):
  SCHEMA = {
    'abstract': u'',
    'ack': u'',
    'aff': [u'',],
    'alternate_bibcode': [u'',],
    'alternate_title': [u'',],
    'arxiv_class': [u'',],
    'author': [u'',],
    #'author_native': [u'',], Waiting for montysolr
    'author_facet_hier': [u'',], #???
    'author_norm': [u'',],
    'bibcode': u'',
    'bibgroup': [u'',],
    'bibstem': [u'',],
    'citation': [u'',],
    'citation_count': 0,
    'cite_read_boost': 0.0,
    'classic_factor': 0,
    'comment': [u'',],
    'copyright': [u'',],
    'database': [u'',],
    'date': u'YYYY-MM[-DD]',
    'doi':[u'',], 
    'email': [u'',],
    'facility': [u'',],
    'first_author': u'',
    'first_author_facet_hier': [u'',], #???
    'full': u'',
    'grant': [u'',],
    'grant_facet_hier': [u'',],
    'id': 0,
    'identifier': [u'',],
    'isbn': [u'',],
    'issn': [u'',],
    'issue': u'',
    'keyword': [u'',],
    'keyword_facet': [u'',],
    'keyword_norm': [u'',],
    'keyword_schema': [u'',],
    'lang': u'',
    'links_data': [u'',],
    'page': u'',
    'property': [u'',],
    'pub': u'',
    'pub_raw': u'',
    'pubdate': u'',
    'read_count': 0,
    'reader':u'',
    'recid': 0,
    'reference': [u'',],
    'simbid': [0,],
    'thesis': u'',
    'title': [u'',],
    'vizier': [u'',],
    'vizier_facet':[u'',],
    'volume': u'',
    'year': u'',
  }

  #------------------------------------------------
  #Private methods; responsible for translating schema: ADS->Solr

  @staticmethod
  def _abstract(ADS_record):
    abstracts = ADS_record['metadata']['general'].get('abstracts',[])
    result = None
    for r in abstracts:
      if r['lang'] == "en":
        result = r['text']
    if not result and abstracts: #attempt fallback to other language if en not present
      result = abstracts[0].get('text','')
    return {'abstract': result}

  @staticmethod
  def _ack(ADS_record):
    result = ADS_record['text'].get('acknowledgements')
    return {'ack': result}

  @staticmethod
  def _aff(ADS_record):
    authors = ADS_record['metadata']['general'].get('authors',[])
    authors = sorted(authors,key=lambda k: int(k['number']))
    result = ['; '.join([j for j in i['affiliations'] if j]) if i['affiliations'] else u'-' for i in authors]
    return {'aff': result}

  @staticmethod
  def _alternate_bibcode(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['relations'].get('alternates',[])]
    return {'alternate_bibcode': result}

  @staticmethod
  def _alternate_title(ADS_record):
    result = []
    for r in ADS_record['metadata']['general'].get('titles',[]):
      if r['lang'] != "en":
        result.append( r['text'] )
    return {'alternate_title': result}

  @staticmethod 
  def _arxiv_class(ADS_record):
    results = [i for i in ADS_record['metadata']['general'].get('arxivcategories',[])]
    return {'arxiv_class':results}

  @staticmethod
  def _author(ADS_record):
    authors = ADS_record['metadata']['general'].get('authors',[])
    authors = sorted(authors,key=lambda k: int(k['number']))
    result = [i['name']['western'] for i in authors if i]
    return {'author': result}  

  # waiting for montysolr
  # @staticmethod
  # def _author_native(ADS_record):
  #   authors = ADS_record['metadata']['general'].get('authors',[])
  #   authors = sorted(authors,key=lambda k: int(k['number']))
  #   result = [i['name']['native'] if i['name']['native'] else u"-" for i in authors]
  #   return {'author_native': result}  

  @staticmethod
  def _bibcode(ADS_record):
    return {'bibcode': ADS_record['bibcode']}

  @staticmethod
  def _bibgroup(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['properties'].get('bibgroups',[])]
    return {'bibgroup': result}

  @staticmethod
  def _body(ADS_record):
    result = ADS_record['text'].get('body')
    return {'body': result}

  @staticmethod
  def _copyright(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['general'].get('copyright',[])]
    return {'copyright': result}

  @staticmethod
  def _comment(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['general'].get('comment',[])]
    return {'comment': result}

  @staticmethod
  def _database(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['properties'].get('databases',[])]
    result = list(set(result))
    return {'database': result}

  @staticmethod
  def _doi(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['general'].get('doi',[])]
    return {'doi': result}

  @staticmethod
  def _email(ADS_record):
    authors = ADS_record['metadata']['general'].get('authors',[])
    authors = sorted(authors,key=lambda k: int(k['number']))
    result = ['; '.join([j for j in i['emails'] if j]) if i['emails'] else u'-' for i in authors]
    return {'email': result}

  @staticmethod
  def _first_author(ADS_record):
    authors = ADS_record['metadata']['general'].get('authors',[])
    authors = sorted(authors,key=lambda k: int(k['number']))   
    return {'first_author': authors[0]['name']['western']}

  @staticmethod
  def _id(ADS_record):
    return {'id': ADS_record['_id']}

  @staticmethod
  def _identifier(ADS_record):
    result = []
    result.extend( [i['content'] for i in ADS_record['metadata']['relations'].get('preprints',[])] )
    result.extend( [i['content'] for i in ADS_record['metadata']['general'].get('doi',[])] )
    result.extend( [i['content'] for i in ADS_record['metadata']['relations'].get('alternates',[])] )
    return {'identifier': result}

  @staticmethod
  def _issn(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['general'].get('issns',[])]
    return {'issn': result}

  @staticmethod
  def _isbn(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['general'].get('isbns',[])]
    return {'isbn': result}

  @staticmethod
  def _issue(ADS_record):
    return {'issue': ADS_record['metadata']['general'].get('publication',{}).get('issue')}
      
  @staticmethod
  def _page(ADS_record):
    return {'page': ADS_record['metadata']['general'].get('publication',{}).get('page')}

  @staticmethod
  def _volume(ADS_record):
    return {'volume': ADS_record['metadata']['general'].get('publication',{}).get('volume')}

  @staticmethod
  def _keyword(ADS_record):
    result = [i['original'] for i in ADS_record['metadata']['general'].get('keywords',[]) if i['original']]
    return {'keyword': result}

  @staticmethod
  def _reference(ADS_record):
    result = [i['bibcode'] for i in ADS_record['metadata']['references'] if i]
    return {'reference': result}


  #------------------------------------------------
  #Public Entrypoints
  @classmethod
  def adapt(cls,ADS_record):
    assert isinstance(ADS_record,dict)
    result = {}
    for k in cls.SCHEMA:
      try:
        D = eval('cls._%s' % k)(ADS_record)
        v = D.values()
        if not v or (len(v)==1 and not isinstance(v[0],int) and not isinstance(v[0],float) and not v[0]):
          D = {}
        result.update(D)
      except AttributeError, e:
        print "NotImplementedWarning:", e
        if "type object 'SolrAdapter'" not in e.message:
          raise
        #raise NotImplementedError
    return result

  @classmethod
  def validate(cls,solr_record):
    '''
    Validates types and keys of `record` against self.schema.
    Raises AssertionError if types or keys do not match
    '''
    r = solr_record
    SCHEMA = cls.SCHEMA
    assert isinstance(r,dict)
    for k,v in r.iteritems():
      try:
        assert k in SCHEMA
        assert isinstance(v,type(SCHEMA[k]))
        if isinstance(v,list) and v: #No expectation of nested lists
          assert len(set([type(i) for i in v])) == 1
          assert isinstance(v[0],type(SCHEMA[k][0]))
      except AssertionError, err:
        print "%s: %s does not have the expected form %s (%s)" % (k,v,SCHEMA[k],r['bibcode'])
        raise


def solrUpdate(bibcodes,url='http://localhost:8983/solr/update?commit=true'):
  solrRecords = []
  if not bibcodes:
    logger.warning("solrUpdate did not recieve any bibcodes")
    return

  m = MongoConnection.PipelineMongoConnection(**MONGO)
  records = m.getRecordsFromBibcodes(bibcodes)

  for record in records:
    r = SolrAdapter.adapt(record)
    SolrAdapter.validate(r) #Raises AssertionError if not validated
    solrRecords.append(r)
  payload = json.dumps(solrRecords)
  #logger.debug(payload)
  headers = {'content-type': 'application/json'}
  r = requests.post(url,data=payload,headers=headers)

def main():
  parser = argparse.ArgumentParser()

  #todo; make this into bibcodes, connect to mongo to get those records
  parser.add_argument(
    '--records',
    nargs='*',
    default=None,
    dest='records',
    help='Records'
    )

  parser.add_argument(
    '--solr_url',
    default='http://localhost:8983/solr/update?commit=true',
    dest='url',
    help='solr update endpoint'
    )

  args = parser.parse_args()
  solrUpdate(args.records,url=args.url)

if __name__ == '__main__':
  main()