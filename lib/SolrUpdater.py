import requests
import argparse
import json
import requests
import logging
from cloghandler import ConcurrentRotatingFileHandler
import logging.handlers
import os, sys
import re

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))
from lib import MongoConnection
from lib import EnforceSchema
from settings import MONGO, MONGO_ADSDATA, SOLR_URL

logfmt = '%(levelname)s\t%(process)d [%(asctime)s]:\t%(message)s'
datefmt= '%m/%d/%Y %H:%M:%S'
formatter = logging.Formatter(fmt=logfmt,datefmt=datefmt)
LOGGER = logging.getLogger(__file__)
if not LOGGER.handlers:
  fn = os.path.join(os.path.dirname(__file__),'..','logs','SolrUpdater.log')   
  rfh = ConcurrentRotatingFileHandler(filename=fn,maxBytes=2097152,backupCount=10,mode='a') #2MB file
  rfh.setFormatter(formatter)
  ch = logging.StreamHandler() #console handler
  ch.setFormatter(formatter)
#  LOGGER.addHandler(ch)
  LOGGER.addHandler(rfh)
LOGGER.setLevel(logging.INFO)
logger = LOGGER


def get_date_by_datetype(ADS_record):
  
  """computes the standard pubdate by selecting the appropriate value
  from the ADS_record and formatting it as YYYY-MM-DD"""

  dates = ADS_record['metadata']['general']['publication']['dates']
  for datetype in [ 'date-published', 'date-thesis', 'date-preprint' ]:
    try:
      return next(i['content'] for i in dates if i['type'].lower()==datetype)
    except StopIteration:
      pass
  return None

class SolrAdapter(object):
  SCHEMA = {
    'abstract': u'',
    'ack': u'',
    'aff': [u'',],
    'alternate_bibcode': [u'',],
    'alternate_title': [u'',],
    'arxiv_class': [u'',],
    'author': [u'',],
    'author_facet': [u'',],
    #'author_native': [u'',], Waiting for montysolr
    'author_facet_hier': [u'',], #???
    'author_norm': [u'',],
    'bibcode': u'',
    'bibgroup': [u'',],
    'bibgroup_facet': [u'',],
    'bibstem': [u'',],
    'bibstem_facet': u'',
    'body': u'',
    'citation': [u'',],
    'citation_count': 0,
    'cite_read_boost': 0.0,
    'classic_factor': 0,
    'comment': [u'',],
    'copyright': [u'',],
    'database': [u'',],
    'date': u'YYYY-MM[-DD]',
    'data':[u''],
    'data_facet': [u''],
    'doi':[u'',],
    'eid':u'',
    'email': [u'',],
    'facility': [u'',],
    'first_author': u'',
    'first_author_facet_hier': [u'',],
    'first_author_norm':u'', 
    #'full': u'', #non-populated field 
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
    'page': [u''],
    'property': [u'',],
    'pub': u'',
    'pub_raw': u'',
    'pubdate': u'',
    'read_count': 0,
    'reader':[u'',],
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
    result = ADS_record['text'].get('acknowledgement',{}).get('content')
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
    result = list(set(result))
    return {'alternate_bibcode': result}

  @staticmethod
  def _alternate_title(ADS_record):
    result = []
    for r in ADS_record['metadata']['general'].get('titles',[]):
      if not r['lang'] or r['lang'] != "en":
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
    result = [i['name']['western'] for i in authors if i['name']['western']]
    return {'author': result}  

  @staticmethod
  def _author_norm(ADS_record):
    authors = ADS_record['metadata']['general'].get('authors',[])
    authors = sorted(authors,key=lambda k: int(k['number']))
    result = [i['name']['normalized'] for i in authors if i['name']['normalized']]
    return {'author_norm': result}

  @staticmethod
  def _author_facet(ADS_record):
    authors = ADS_record['metadata']['general'].get('authors',[])
    authors = sorted(authors,key=lambda k: int(k['number']))
    result = [i['name']['normalized'] for i in authors if i['name']['normalized']]
    return {'author_facet': result}    

  @staticmethod
  def _author_facet_hier(ADS_record):
    authors = ADS_record['metadata']['general'].get('authors',[])
    authors = sorted(authors,key=lambda k: int(k['number']))
    result = []
    for author in authors:
      r = u"0/%s" % (author['name']['normalized'],)
      result.append(r)
      r = u"1/%s/%s" % (author['name']['normalized'],author['name']['western'])
      result.append(r)
    return {'author_facet_hier': result}


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
    result = list(set(result))
    return {'bibgroup': result}

  @staticmethod
  def _bibgroup_facet(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['properties'].get('bibgroups',[])]
    result = list(set(result))
    return {'bibgroup_facet': result}   

  @staticmethod
  def _bibstem(ADS_record):
    b = ADS_record['bibcode']
    # index both long and short bibstems
    result = map(unicode,[re.sub(r'\.+$','',b[4:9]),b[4:13]])
    return {'bibstem':result}

  @staticmethod
  def _bibstem_facet(ADS_record):
    b = ADS_record['bibcode']
    if re.match("^[\\.\\d]+$",b[9:13]):
      # is a serial publication, user short bibstem
      result = b[4:9].replace('.','')
    else:
      # is book/conference/arxiv, use long bibstem
      result = re.sub(r'\.+$','',b[4:13])
    return {'bibstem_facet':unicode(result)}

  @staticmethod
  def _body(ADS_record):
    result = ADS_record['text'].get('body',{}).get('content')
    return {'body': result}

  @staticmethod
  def _copyright(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['general'].get('copyright',[])]
    return {'copyright': result}

  @staticmethod
  def _citation(ADS_record):
    result = [i for i in ADS_record.get('adsdata',{}).get('citations',[])]
    return {'citation': result}

  @staticmethod
  def _citation_count(ADS_record):
    result = ADS_record.get('adsdata',{}).get('citation_count')
    return {'citation_count': result}

  @staticmethod
  def _cite_read_boost(ADS_record):
    result = ADS_record.get('adsdata',{}).get('boost')
    if result:
      result = float(result)
    return {'cite_read_boost': result}

  @staticmethod
  def _classic_factor(ADS_record):
    result = ADS_record.get('adsdata',{}).get('norm_cites')
    if result:
      result = int(result)
    return {'classic_factor': result}

  @staticmethod
  def _comment(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['general'].get('comment',[])]
    return {'comment': result}

  @staticmethod
  def _database(ADS_record):
    translation = {
      'PHY': u'physics',
      'AST': u'astronomy',
      'GEN': u'general',
    }
    result = [translation[i['content'].upper()] for i in ADS_record['metadata']['properties'].get('databases',[])]
    result = list(set(result))
    return {'database': result}

  @staticmethod
  def _data(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['properties'].get('data_sources',[])]
    return {'data': result}

  @staticmethod
  def _data_facet(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['properties'].get('data_sources',[])]
    return {'data_facet': result}    

  @staticmethod
  def _year(ADS_record):
    dates = ADS_record['metadata']['general']['publication']['dates']
    try:
      result = next(i['content'] for i in dates if i['type'].lower()=='publication_year') #TODO: Catch StopIteration
    except StopIteration:
      result = None
    return {'year':result}

  @staticmethod
  def _date(ADS_record):
    result = get_date_by_datetype(ADS_record)
    if result:
      try:
        result = EnforceSchema.Enforcer.parseDate(result)
      except ValueError:
        result = None
    # should we throw an exception if result is null?
    return {'date':result}

  @staticmethod
  def _doi(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['general'].get('doi',[])]
    return {'doi': result}

  @staticmethod
  def _eid(ADS_record):
    result = ADS_record['metadata']['general']['publication'].get('electronic_id')
    return {'eid': result}

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
    if not authors:
      result = None
    else:
      result = authors[0]['name']['western']
    return {'first_author': result}

  @staticmethod
  def _first_author_facet_hier(ADS_record):
    authors = ADS_record['metadata']['general'].get('authors',[])
    authors = sorted(authors,key=lambda k: int(k['number']))
    result = []
    if authors:
      r = u"0/%s" % (authors[0]['name']['normalized'],)
      result.append(r)
      r = u"1/%s/%s" % (authors[0]['name']['normalized'],authors[0]['name']['western'])
      result.append(r)
    return {'first_author_facet_hier':result}

  @staticmethod
  def _first_author_norm(ADS_record):
    authors = ADS_record['metadata']['general'].get('authors',[])
    authors = sorted(authors,key=lambda k: int(k['number']))   
    if authors:
      result = authors[0]['name']['normalized']
    else:
      result = None
    return {'first_author_norm': result}

  @staticmethod
  def _lang(ADS_record):
    return {'lang': ADS_record['text'].get('body',{}).get('language','')}

  @staticmethod
  def _links_data(ADS_record):
    result = ['''{"title":"%s", "type":"%s", "instances":"%s", "access":"%s"}''' % (i['title'],i['type'],i['count'],i['access']) for i in ADS_record['metadata']['relations'].get('links',[])]
    result = [unicode(r.replace('None','')) for r in result]
    return {'links_data':result}

  @staticmethod
  def _grant(ADS_record):
    result = []
    for grant in ADS_record.get('adsdata',{}).get('grants',{}):
      result.append(grant['agency'])
      result.append(grant['grant'])
    return {'grant': result}

  @staticmethod
  def _grant_facet_hier(ADS_record):
    result = []
    for grant in ADS_record.get('adsdata',{}).get('grants',[]):
      r = u"0/%s" % (grant['agency'],)
      result.append(r)
      r = u"1/%s/%s" % (grant['agency'],grant['grant'])
      result.append(r)
    return {'grant_facet_hier': result}

  @staticmethod
  def _id(ADS_record):
    return {'id': ADS_record['_id']}

  @staticmethod
  def _identifier(ADS_record):
    result = []
    result.extend( [i['content'] for i in ADS_record['metadata']['relations'].get('preprints',[])] )
    result.extend( [i['content'] for i in ADS_record['metadata']['general'].get('doi',[])] )
    result.extend( [i['content'] for i in ADS_record['metadata']['relations'].get('alternates',[])] )
    return {'identifier': list(set(result))}

  @staticmethod
  def _issn(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['general'].get('issns',[])]
    return {'issn': result}

  @staticmethod
  def _isbn(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['general'].get('isbns',[])]
    #Ugly hack, we should fix this in Enforcer properly.
    if result and isinstance(result[0],list):
      result = [i for i in result[0]]
    return {'isbn': result}

  @staticmethod
  def _issue(ADS_record):
    result = ADS_record['metadata']['general'].get('publication',{}).get('issue')
    return {'issue': result}
      
  @staticmethod
  def _page(ADS_record):
    result = [ADS_record['metadata']['general']['publication'].get('page')]
    if ADS_record['metadata']['general']['publication'].get('electronic_id'):
      result.append(ADS_record['metadata']['general']['publication']['electronic_id'])
    return {'page': filter(None,result)}

  @staticmethod
  def _property(ADS_record):
    fields = ['openaccess','ocrabstract','private','refereed']
    result = []
    for f in fields:
      if ADS_record['metadata']['properties'][f]:
        result.append(unicode(f.upper()))
    if ADS_record['metadata']['properties']['doctype']['content'] in ['eprint', 'article', 'inproceedings', 'inbook']:
      result.append(u"ARTICLE")
    else:
      result.append(u"NONARTICLE")
    if u'REFEREED' not in result:
      result.append(u"NOT REFEREED")
    return {'property':result}

  @staticmethod
  def _pub(ADS_record):
    return {'pub': ADS_record['metadata']['general'].get('publication',{}).get('name',{}).get('canonical')}

  @staticmethod
  def _pub_raw(ADS_record):
    return {'pub_raw': ADS_record['metadata']['general'].get('publication',{}).get('name',{}).get('raw')}

  @staticmethod
  def _pubdate(ADS_record):
    result = get_date_by_datetype(ADS_record)
    return {'pubdate':result}

  @staticmethod
  def _keyword(ADS_record):
    """original keywords; must match one-to-one with _keyword_schema and _keyword_norm"""
    result = [i['original'] if i['original'] else u'-' for i in ADS_record['metadata']['general'].get('keywords',[])]
    return {'keyword': result}

  @staticmethod
  def _keyword_norm(ADS_record):
    """normalized keywords; must match one-to-one with _keyword and _keyword_schema"""
    result = [i['normalized'] if i['normalized'] else u'-' for i in ADS_record['metadata']['general'].get('keywords',[])]
    return {'keyword_norm': result}  

  @staticmethod
  def _keyword_schema(ADS_record):
    """keyword system; must match one-to-one with _keyword and _keyword_norm"""
    result = [i['type'] if i['type'] else u'-' for i in ADS_record['metadata']['general'].get('keywords',[])]
    return {'keyword_schema': result}    

  @staticmethod
  def _keyword_facet(ADS_record):
    # keep only non-empty normalized keywords
    result = filter(None, [i['normalized'] for i in ADS_record['metadata']['general'].get('keywords',[])])
    return {'keyword_facet':result}

  @staticmethod
  def _read_count(ADS_record):
    readers = ADS_record.get('adsdata',{}).get('readers',[])
    return {'read_count': len(readers)}

  @staticmethod
  def _reader(ADS_record):
    result = ADS_record.get('adsdata',{}).get('readers',[])
    return {'reader': result}

  @staticmethod
  def _reference(ADS_record):
    # take only bibcodes for references which are resolved (score > 0) and verified (score < 5)
    result = [i['bibcode'] for i in ADS_record['metadata']['references'] if i['bibcode'] and i['score'] and int(i['score']) > 0 and int(i['score']) < 5]
    # there may be multiple references in the merged document, so unique the list and 
    # sort it so that it's easier to manage
    return {'reference': sorted(set(result))}

  @staticmethod
  def _simbid(ADS_record):
    result = [int(i['id']) for i in ADS_record.get('adsdata',{}).get('simbad_objects',[])]
    return {'simbid': result}

  @staticmethod
  def _title(ADS_record):
    result = [i['text'] for i in ADS_record['metadata']['general'].get('titles',[])]
    return {'title':result}

  @staticmethod
  def _volume(ADS_record):
    return {'volume': ADS_record['metadata']['general'].get('publication',{}).get('volume')}

  @staticmethod
  def _vizier(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['properties'].get('vizier_tables',[])]
    return {'vizier': result}

  @staticmethod
  def _vizier_facet(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['properties'].get('vizier_tables',[])]
    return {'vizier_facet': result}    

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
        logger.debug("NotImplementedWarning: %s" % e)
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
      assert k in SCHEMA, '%s: not in schema' % k
      assert isinstance(v,type(SCHEMA[k])), '%s: has an unexpected type (%s!=%s)' % (k,type(v),SCHEMA[k])
      if isinstance(v,list) and v: #No expectation of nested lists
        assert len(set([type(i) for i in v])) == 1, "%s: multiple data-types in a list" % k
        assert isinstance(v[0],type(SCHEMA[k][0])), "%s: inner list element has unexpected type (%s!=%s)" % (k,type(v[0]),SCHEMA[k][0])

def solrUpdate(bibcodes,url=SOLR_URL):
  solrRecords = []
  logger.debug("Recieved a payload of %s bibcodes" % len(bibcodes))
  if not bibcodes:
    logger.warning("solrUpdate did not recieve any bibcodes")
    return

  m = MongoConnection.PipelineMongoConnection(**MONGO)
  metadata = m.getRecordsFromBibcodes(bibcodes)
  m.close()

  #Until we have a proper union of mongos, we need to compile a full record from several DBs
  #This in-line configuration will be dumped when that happens.
  m = MongoConnection.PipelineMongoConnection(**MONGO_ADSDATA)
  adsdata = m.getRecordsFromBibcodes(bibcodes,key="_id")
  m.close()

  for r in metadata:
    try:
      r.update({'adsdata':next(doc for doc in adsdata if doc['_id']==r['bibcode'])})
    except StopIteration:
      r['adsdata'] = {}
  logger.debug("Combined payload has %s records" % len(metadata))

  for record in metadata:
    r = SolrAdapter.adapt(record)
    SolrAdapter.validate(r) #Raises AssertionError if not validated
    solrRecords.append(r)
  payload = json.dumps(solrRecords)
  headers = {'content-type': 'application/json'}
  logger.info("Posting payload of length %s to %s" % (len(solrRecords),url))
  logger.debug("Payload: %s" % payload)
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
    default=SOLR_URL,
    dest='url',
    help='solr update endpoint'
    )

  args = parser.parse_args()
  solrUpdate(args.records,url=args.url)

if __name__ == '__main__':
  main()
