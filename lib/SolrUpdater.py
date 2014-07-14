import requests
import argparse
import json
import requests

class SolrAdapter(object):
  SCHEMA = {
      'abstract': '',
      'ack': '',
      'aff': ['',],
      'alternate_bibcode': ['',],
      'arxiv_class': ['',],
      'author': ['',],
      'author_facet_hier': ['',], #???
      'author_norm': ['',],
      'bibcode': '',
      'bibgroup': ['',],
      'bibstem': ['',],
      'citation': ['',],
      'citation_count': 0,
      'cite_read_boost': 0.0,
      'classic_factor': 0,
      'copyright': '',
      'database': ['',],
      'date': 'YYYY-MM[-DD]',
      'doi':['',], #Why is this multiple value'd?
      'email': ['',],
      'facility': ['',],
      'first_author': '',
      'first_author_facet_hier': ['',], #???
      'full': '',
      'grant': ['',],
      'grant_facet_hier': ['',],
      'id': None, #invenio id, let's remove this???
      'identifier': ['',],
      'isbn': ['',],
      'issn': ['',],
      'issue': '',
      'keyword': ['',],
      'keyword_facet': ['',],
      'keyword_norm': ['',],
      'keyword_schema': ['',],
      'lang': '',
      'links_data': ['',],
      'page': ['',],
      'property': ['',],
      'pub': '',
      'pub_raw': '',
      'pubdate': '',
      'read_count': 0,
      'reader':'',
      'recid': 0,
      'reference': ['',],
      'simbid': [0,],
      'thesis': '',
      'title': ['',],
      'vizier': ['',],
      'vizier_facet':['',],
      'volume': '',
      'year': '',
    }

  #------------------------------------------------
  #Private methods; responsible for translating schema: ADS->Solr

  @staticmethod
  def _abstract(ADS_record):
    result = None
    for r in ADS_record['metadata']['general']['abstract']:
      if r['@lang'] == "en" or not result['abstract']:
        result = r['#text']
    return {'abstract': result}

  # @staticmethod
  # def _ack(ADS_record):
  #   result = ADS_record['metadata'].get('acknowledgements',None)
  #   return {'ack': result}

  @staticmethod
  def _aff(ADS_record):
    authors = sorted(ADS_record['metadata']['general']['author'],key=lambda k: int(k['@nr']))
    result = ['; '.join([j for j in i['affiliations'] if j]) for i in authors]
    return {'aff': result}

  @staticmethod
  def _alternate_bibcode(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['relations']['alternates'] if i]
    return {'alternate_bibcode': result}

  @staticmethod
  def _author(ADS_record):
    authors = sorted(ADS_record['metadata']['general']['author'],key=lambda k: int(k['@nr']))
    result = [i['name']['western'] for i in authors if i]
    return {'author': result}  

  @staticmethod
  def _bibcode(ADS_record):
    return {'bibcode': ADS_record['bibcode']}

  @staticmethod
  def _bibgroup(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['properties']['bibgroups'] if i]
    return {'bibgroup': result}

  @staticmethod
  def _copyright(ADS_record):
    result = ADS_record['metadata']['general']['copyright'].get('content',None)
    return {'copyright': result}

  @staticmethod
  def _database(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['properties']['databases'] if i]
    return {'database': result}

  @staticmethod
  def _doi(ADS_record):
    result = ADS_record['metadata']['general']['doi'].get('content',None) 
    return {'doi': result}

  @staticmethod
  def _email(ADS_record):
    authors = sorted(ADS_record['metadata']['general']['author'],key=lambda k: int(k['@nr']))
    result = ['; '.join([j for j in i['emails'] if j]) for i in authors if i]
    return {'email': result}

  @staticmethod
  def _first_author(ADS_record):
    authors = sorted(ADS_record['metadata']['general']['author'],key=lambda k: int(k['@nr']))   
    return {'first_author': authors[0]['name']['western']}

  @staticmethod
  def _issn(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['general']['issns'] if i]
    return {'issn': result}

  @staticmethod
  def _isbn(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['general']['isbns'] if i]
    return {'isbn': result}
      
  @staticmethod
  def _keyword(ADS_record):
    result = [i['original'] for i in ADS_record['metadata']['general']['keywords'] if i]
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
        if not v[0] or not v[0][0]:
          D = {}
        result.update(D)
      except AttributeError as e:
        print "NotImplementedWarning:", e
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
      assert k in SCHEMA
      assert isinstance(v,type(SCHEMA[k]))
      if isinstance(v,list) and v: #No expectation of nested lists
        assert len(set([type(i) for i in v])) == 1
        assert isinstance(v[0],type(SCHEMA[k][0]))

def solrUpdate(ADSrecords,url='http://localhost:9001/solr/update/json?commit=true'):
  solrRecords = []
  for r in ADSrecords:
    r = SolrAdapter.adapt(r)
    #SolrAdapter.validate(r) #Raises AssertionError if not validated
    solrRecords.append(r)
  payload = json.dumps(solrRecords)
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
    default='http://localhost:9001/solr/update/json?commit=true',
    dest='url',
    help='solr update endpoint'
    )

  args = parser.parse_args()
  solrUpdate(args.records,url=args.url)

if __name__ == '__main__':
  main()