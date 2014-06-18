import requests
import argparse
import json

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
      'ciration_count': 0,
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

  @staticmethod
  def _ack(ADS_record):
    result = ADS_record['metadata'].get('acknowledgements',None)
    return {'ack': result}

  @staticmethod
  def _aff(ADS_record):
    authors = sorted(ADS_record['metadata']['general']['author'],key=lambda k: int(k['@nr']))
    result = ['; '.join([j for j in i['affiliations']]) for i in authors]
    return {'aff': result}

  @staticmethod
  def _alternate_bibcode(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['relations']['alternates']]
    return {'alternate_bibcode': result}

  @staticmethod
  def _author(ADS_record):
    authors = sorted(ADS_record['metadata']['general']['author'],key=lambda k: int(k['@nr']))
    result = [i['name']['western'] for i in authors]
    return {'author': result}  

  @staticmethod
  def _bibcode(ADS_record):
    return {'bibcode': ADS_record['bibcode']}

  @staticmethod
  def _bibgroup(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['properties']['bibgroups']]
    return {'bibgroup': result}

  @staticmethod
  def _copyright(ADS_record):
    result = ADS_record['metadata']['general']['copyright'].get('content',None)
    return {'copyright': result}


  #------------------------------------------------
  #Public Entrypoints  

  @classmethod
  def adapt(cls,ADS_record):
    assert isinstance(ADS_record,dict)
    result = {}
    for k in cls.SCHEMA:
      try:
        result.update(eval('cls._%s' % k)(ADS_record))
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


def solrUpdate(ADSrecords,url='http://localhost:9001/solr/update/json'):
  solrRecords = []
  for r in ADSrecords:
    r = SolrAdapter.adapt(r)
    print r
    SolrAdapter.validate(r)
    solrRecords.append(r)
    #Raises AssertionError if not validated

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
    default='http://localhost:9001/solr/update/json',
    dest='url',
    help='solr update endpoint'
    )

  args = parser.parse_args()
  solrUpdate(args.records,url=args.url)

if __name__ == '__main__':
  main()