import requests
import json
import os
import sys
import re
import traceback


from aip.libs.utils import setup_logging
from aip.libs import enforce_schema

logger = setup_logging('solr_adapter.log', 'SolrAdapter')

ARTICLE_TYPES = set(['eprint', 'article', 'inproceedings', 'inbook'])
        

def get_date_by_datetype(ADS_record):
    """computes the standard pubdate by selecting the appropriate value
    from the ADS_record and formatting it as YYYY-MM-DD"""

    dates = ADS_record['metadata']['general']['publication']['dates']
    for datetype in [ 'date-published', 'date-thesis', 'date-preprint' ]:
        try:
            return next(i['content'] for i in dates if i['type'].lower() == datetype)
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
    'author_count': 0,
    'author_facet': [u'',],
    #'author_native': [u'',], Waiting for montysolr
    'author_facet_hier': [u'',],
    'author_norm': [u'',],
    'bibcode': u'',
    'bibgroup': [u'', ],
    'bibgroup_facet': [u'', ],
    'bibstem': [u'', ],
    'bibstem_facet': u'',
    'body': u'',
    'citation': [u'', ],
    'citation_count': 0,
    'cite_read_boost': 0.0,
    'classic_factor': 0,
    'comment': [u'',],
    'copyright': [u'',],
    'database': [u'',],
    'date': u'YYYY-MM[-DD]',
    'data':[u''],
    'data_facet': [u''],
    'doctype': u'',
    'doctype_facet_hier': [u''],
    'doi':[u'',],
    'eid':u'',
    'email': [u'', ],
    'facility': [u'', ],
    'first_author': u'',
    'first_author_facet_hier': [u'',],
    'first_author_norm':u'', 
    'grant': [u'',],
    'grant_facet_hier': [u'',],
    'id': 0,
    'identifier': [u'',],
    'isbn': [u'',],
    'issn': [u'',],
    'issue': u'',
    'keyword': [u'', ],
    'keyword_facet': [u'', ],
    'keyword_norm': [u'', ],
    'keyword_schema': [u'', ],
    'lang': u'',
    'links_data': [u'', ],
    'orcid': [u''],
    'orcid_pub': [u''],
    'orcid_user': [u''],
    'orcid_other': [u''],
    'page': [u''],
    'property': [u'', ],
    'pub': u'',
    'pubnote': [u'',],
    'pub_raw': u'',
    'pubdate': u'',
    'read_count': 0,
    'reader':[u'', ],
    'recid': 0,
    'reference': [u'', ],
    'simbid': [0, ],
    'simbtype': [u'', ],
    'simbad_object_facet_hier': [u'', ],
    'thesis': u'',
    'title': [u'', ],
    'vizier': [u'', ],
    'vizier_facet':[u'', ],
    'volume': u'',
    'year': u'',
  }


  #------------------------------------------------
  # Private methods; responsible for translating schema: ADS->Solr

  @staticmethod
  def _abstract(ADS_record):
    abstracts = ADS_record['metadata']['general'].get('abstracts', [])
    result = None
    for r in abstracts:
      if r['lang'] == "en":
        result = r['text']
    if not result and abstracts:  # attempt fallback to other language if en not present
      result = abstracts[0].get('text', '')
    return {'abstract': result}

  @staticmethod
  def _ack(ADS_record):
    result = ADS_record['text'].get('acknowledgement', {}).get('content')
    return {'ack': result}

  @staticmethod
  def _aff(ADS_record):
    authors = ADS_record['metadata']['general'].get('authors', [])
    authors = sorted(authors, key=lambda k: int(k['number']))
    result = ['; '.join([j for j in i['affiliations'] if j]) if i['affiliations'] else u'-' for i in authors]
    return {'aff': result}

  @staticmethod
  def _alternate_bibcode(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['relations'].get('alternates', [])]
    result = list(set(result))
    return {'alternate_bibcode': result}

  @staticmethod
  def _alternate_title(ADS_record):
    result = []
    for r in ADS_record['metadata']['general'].get('titles', []):
      if not r['lang'] or r['lang'] != "en":
        result.append(r['text'])
    return {'alternate_title': result}

  @staticmethod 
  def _arxiv_class(ADS_record):
    results = [i for i in ADS_record['metadata']['general'].get('arxivcategories', [])]
    return {'arxiv_class':results}

  @staticmethod
  def _author(ADS_record):
    authors = ADS_record['metadata']['general'].get('authors', [])
    authors = sorted(authors, key=lambda k: int(k['number']))
    result = [i['name']['western'] for i in authors if i['name']['western']]
    return {'author': result}  

  @staticmethod
  def _author_count(ADS_record):
    authors = ADS_record['metadata']['general'].get('authors',[])
    result = len([i['name']['western'] for i in authors if i['name']['western']])
    return {'author_count': result}

  @staticmethod
  def _author_norm(ADS_record):
    authors = ADS_record['metadata']['general'].get('authors', [])
    authors = sorted(authors, key=lambda k: int(k['number']))
    result = [i['name']['normalized'] for i in authors if i['name']['normalized']]
    return {'author_norm': result}

  @staticmethod
  def _author_facet(ADS_record):
    authors = ADS_record['metadata']['general'].get('authors', [])
    authors = sorted(authors, key=lambda k: int(k['number']))
    result = [i['name']['normalized'] for i in authors if i['name']['normalized']]
    return {'author_facet': result}    

  @staticmethod
  def _author_facet_hier(ADS_record):
    authors = ADS_record['metadata']['general'].get('authors', [])
    authors = sorted(authors, key=lambda k: int(k['number']))
    result = []
    for author in authors:
      r = u"0/%s" % (author['name']['normalized'],)
      result.append(r)
      r = u"1/%s/%s" % (author['name']['normalized'], author['name']['western'])
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
    result = [i['content'] for i in ADS_record['metadata']['properties'].get('bibgroups', [])]
    result = list(set(result))
    return {'bibgroup': result}

  @staticmethod
  def _bibgroup_facet(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['properties'].get('bibgroups', [])]
    result = list(set(result))
    return {'bibgroup_facet': result}   

  @staticmethod
  def _bibstem(ADS_record):
    b = ADS_record['bibcode']
    short, long = bibstem_mapper(b)
    # index both long and short bibstems
    result = map(unicode, [re.sub(r'\.+$', '', short), long])
    return {'bibstem':result}

  @staticmethod
  def _bibstem_facet(ADS_record):
    b = ADS_record['bibcode']
    short, long = bibstem_mapper(b)
    if re.match(r'^[\.\d]+$', long[5:9]):
      # is a serial publication, use short bibstem
      result = short.replace('.', '')
    else:
      # is book/conference/arxiv, use long bibstem
      result = re.sub(r'\.+$', '', long)
    return {'bibstem_facet':unicode(result)}

  @staticmethod
  def _body(ADS_record):
    result = ADS_record['text'].get('body', {}).get('content')
    return {'body': result}

  @staticmethod
  def _copyright(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['general'].get('copyright', [])]
    return {'copyright': result}

  @staticmethod
  def _citation(ADS_record):
    result = [i for i in ADS_record.get('adsdata', {}).get('citations', [])]
    return {'citation': result}

  @staticmethod
  def _citation_count(ADS_record):
    result = len([i for i in ADS_record.get('adsdata', {}).get('citations', [])])
    return {'citation_count': result}

  @staticmethod
  def _cite_read_boost(ADS_record):
    result = ADS_record.get('adsdata', {}).get('boost')
    if result:
      result = float(result)
    return {'cite_read_boost': result}

  @staticmethod
  def _classic_factor(ADS_record):
    result = ADS_record.get('adsdata', {}).get('norm_cites')
    if result:
      result = int(result)
    return {'classic_factor': result}

  @staticmethod
  def _comment(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['general'].get('comment', [])]
    result = list(set(result))
    # XXX - Hack to avoid a re-indexing because of non-multivalued field 'comment'
    if len(result) > 1:
      result = [ '\n'.join(result) ]
    return {'comment': result}

  @staticmethod
  def _database(ADS_record):
    translation = {
      'PHY': u'physics',
      'AST': u'astronomy',
      'GEN': u'general',
    }
    result = [translation[i['content'].upper()] for i in ADS_record['metadata']['properties'].get('databases', [])]
    result = list(set(result))
    return {'database': result}

  @staticmethod
  def _data(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['properties'].get('data_sources', [])]
    return {'data': result}

  @staticmethod
  def _data_facet(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['properties'].get('data_sources', [])]
    return {'data_facet': result}    

  @staticmethod
  def _year(ADS_record):
    dates = ADS_record['metadata']['general']['publication']['dates']
    try:
      result = next(i['content'] for i in dates if i['type'].lower() == 'publication_year')  # TODO: Catch StopIteration
    except StopIteration:
      result = None
    return {'year':result}

  @staticmethod
  def _date(ADS_record):
    result = get_date_by_datetype(ADS_record)
    if result:
      try:
        result = enforce_schema.Enforcer.parseDate(result)
      except ValueError:
        result = None
    # should we throw an exception if result is null?
    return {'date':result}

  @staticmethod
  def _doctype(ADS_record):
    result = ADS_record['metadata']['properties']\
        .get('doctype', {})\
        .get('content')\
        .lower()
    return {'doctype': result}

  @staticmethod
  def _doctype_facet_hier(ADS_record):
    doctype = ADS_record['metadata']['properties']\
        .get('doctype', {})\
        .get('content')\
        .lower()
    (top,type) = doctype_mapper(doctype)
    result = [ u"0/%s" % top, u"1/%s/%s" % (top, type) ]
    return {'doctype_facet_hier': result}

  @staticmethod
  def _doi(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['general'].get('doi', [])]
    return {'doi': result}

  @staticmethod
  def _eid(ADS_record):
    result = ADS_record['metadata']['general']['publication'].get('electronic_id')
    return {'eid': result}

  @staticmethod
  def _email(ADS_record):
    authors = ADS_record['metadata']['general'].get('authors', [])
    authors = sorted(authors, key=lambda k: int(k['number']))
    result = ['; '.join([j for j in i['emails'] if j]) if i['emails'] else u'-' for i in authors]
    return {'email': result}

  @staticmethod
  def _first_author(ADS_record):
    authors = ADS_record['metadata']['general'].get('authors', [])
    authors = sorted(authors, key=lambda k: int(k['number']))
    if not authors:
      result = None
    else:
      result = authors[0]['name']['western']
    return {'first_author': result}

  @staticmethod
  def _first_author_facet_hier(ADS_record):
    authors = ADS_record['metadata']['general'].get('authors', [])
    authors = sorted(authors, key=lambda k: int(k['number']))
    result = []
    if authors:
      r = u"0/%s" % (authors[0]['name']['normalized'],)
      result.append(r)
      r = u"1/%s/%s" % (authors[0]['name']['normalized'], authors[0]['name']['western'])
      result.append(r)
    return {'first_author_facet_hier':result}

  @staticmethod
  def _first_author_norm(ADS_record):
    authors = ADS_record['metadata']['general'].get('authors', [])
    authors = sorted(authors, key=lambda k: int(k['number']))   
    if authors:
      result = authors[0]['name']['normalized']
    else:
      result = None
    return {'first_author_norm': result}

  @staticmethod
  def _lang(ADS_record):
    return {'lang': ADS_record['text'].get('body', {}).get('language', '')}

  @staticmethod
  def _links_data(ADS_record):
    """rca: it is my understanding that this function is not producing a valid
    JSON; the 'null' gets turned into '' - and I can't tell whether that is
    by design"""
    result = [json.dumps({"title": i.get('title', "") or "", 
                          "type": i.get('type', "") or "", 
                          "instances": i.get('count', "") or "", 
                          "access": i.get('access', "") or "",
                          "url": i.get("url", "") or ""},
                         sort_keys=True) \
                for i in ADS_record['metadata']['relations'].get('links',[])]
    result = [unicode(i) for i in result]
    return {'links_data': result}

  @staticmethod
  def _grant(ADS_record):
    result = []

    grant_dicts = SolrAdapter.convert_grants(ADS_record.get('adsdata', {}).get('grants'))
    for grant in grant_dicts: # ADS_record.get('adsdata',{}).get('grants',{})
      result.append(grant['agency'])
      result.append(grant['grant'])
    return {'grant': result}

  @staticmethod
  def convert_grants(grants_string):
    "convert sql string to the dict mongo used so other code can remain unchanged"
    # first, check to see if conversion is needed
    # if passed an array of dicts, simply return it
    if (isinstance(grants_string, list) and len(grants_string) > 0
        and isinstance(grants_string[0], dict)):
        return grants_string

    # otherwise, process
    grant_dicts = []
    if grants_string is None:
      return grant_dicts
    for current in grants_string:
      current = current.strip()
      parts = current.split(' ')
      if len(parts) == 2:
        d = {'agency': unicode(parts[0]), 'grant': unicode(parts[1])}
        grant_dicts.append(d)
      else:
        print 'warning, band length to grant string {}'.format(current)
    return grant_dicts

  @staticmethod
  def _grant_facet_hier(ADS_record):
    grant_dicts = SolrAdapter.convert_grants(ADS_record.get('adsdata', {}).get('grants'))
    result = []
    for grant in grant_dicts:  # ADS_record.get('adsdata',{}).get('grants',[]):
      r = u"0/%s" % (grant['agency'],)
      result.append(r)
      r = u"1/%s/%s" % (grant['agency'], grant['grant'])
      result.append(r)
    return {'grant_facet_hier': result}

  @staticmethod
  def _id(ADS_record):
    return {'id': ADS_record['id']}

  @staticmethod
  def _identifier(ADS_record):
    result = []
    result.extend([i['content'] for i in ADS_record['metadata']['relations'].get('preprints', [])])
    result.extend([i['content'] for i in ADS_record['metadata']['general'].get('doi', [])])
    result.extend([i['content'] for i in ADS_record['metadata']['relations'].get('alternates', [])])
    return {'identifier': list(set(result))}

  @staticmethod
  def _issn(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['general'].get('issns', [])]
    result = unroll_unique_list(result)
    return {'issn': result}

  @staticmethod
  def _isbn(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['general'].get('isbns', [])]
    result = unroll_unique_list(result)
    return {'isbn': result}

  @staticmethod
  def _issue(ADS_record):
    result = ADS_record['metadata']['general'].get('publication', {}).get('issue')
    return {'issue': result}
      
  @staticmethod
  def _page(ADS_record):
    result = [ADS_record['metadata']['general']['publication'].get('page')]
    if ADS_record['metadata']['general']['publication'].get('electronic_id'):
      result.append(ADS_record['metadata']['general']['publication']['electronic_id'])
    return {'page': filter(None, result)}

  @staticmethod
  def _property(ADS_record):
    fields = ['openaccess', 'ocrabstract', 'private', 'refereed', 'ads_openaccess', 'eprint_openaccess', 'pub_openaccess']
    result = []
    for f in fields:
      if ADS_record['metadata']['properties'][f]:
        result.append(unicode(f.upper()))
    if ADS_record['metadata']['properties']['doctype']['content'] in ARTICLE_TYPES:
      result.append(u"ARTICLE")
    else:
      result.append(u"NONARTICLE")
    if u'REFEREED' not in result:
      result.append(u"NOT REFEREED")
    return {'property':result}

  @staticmethod
  def _pub(ADS_record):
    return {'pub': ADS_record['metadata']['general'].get('publication', {}).get('name', {}).get('canonical')}

  @staticmethod
  def _pub_raw(ADS_record):
    return {'pub_raw': ADS_record['metadata']['general'].get('publication', {}).get('name', {}).get('raw')}

  @staticmethod
  def _pubdate(ADS_record):
    result = get_date_by_datetype(ADS_record)
    return {'pubdate':result}

  @staticmethod
  def _pubnote(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['general'].get('pubnote',[])]
    return {'pubnote':result}

  @staticmethod
  def _keyword(ADS_record):
    """original keywords; must match one-to-one with _keyword_schema and _keyword_norm"""
    result = [i['original'] if i['original'] else u'-' for i in ADS_record['metadata']['general'].get('keywords', [])]
    return {'keyword': result}

  @staticmethod
  def _keyword_norm(ADS_record):
    """normalized keywords; must match one-to-one with _keyword and _keyword_schema"""
    result = [i['normalized'] if i['normalized'] else u'-' for i in ADS_record['metadata']['general'].get('keywords', [])]
    return {'keyword_norm': result}  

  @staticmethod
  def _keyword_schema(ADS_record):
    """keyword system; must match one-to-one with _keyword and _keyword_norm"""
    result = [i['type'] if i['type'] else u'-' for i in ADS_record['metadata']['general'].get('keywords', [])]
    return {'keyword_schema': result}    

  @staticmethod
  def _keyword_facet(ADS_record):
    # keep only non-empty normalized keywords
    result = filter(None, [i['normalized'] for i in ADS_record['metadata']['general'].get('keywords', [])])
    return {'keyword_facet':result}

  @staticmethod
  def _orcid(ADS_record):
    authors = ADS_record['metadata']['general'].get('authors', [])
    authors = sorted(authors, key=lambda k: int(k['number']))
    result = [i['orcid'] if i['orcid'] else u'-' for i in authors]
    out = {'orcid_pub': result}
    if 'orcid_claims' in ADS_record:
        for indexname, claimname in [('orcid_user', 'verified'), ('orcid_other', 'unverified')]:
            if claimname in ADS_record['orcid_claims']:
                claims = ADS_record['orcid_claims'][claimname]
                # basic check, the length should be equal
                if len(claims) != len(authors):
                    logger.warn("Potential problem with orcid claims for: {0} (len(authors) != len(claims))"
                                .format(ADS_record['bibcode']))
                    # TODO: in the grant scheme of things, we should trigger ADS orcid update (let the remote
                    # pipeline processes know, that something is out of sync); for now we'll just truncate the
                    # data
                    if len(claims) > len(authors):
                        claims = claims[0:len(authors)]
                    else:
                        claims = claims + [u'-'] * (len(authors) - len(claims)) 

                out[indexname] = claims
    return out

  @staticmethod
  def _read_count(ADS_record):
    readers = ADS_record.get('adsdata', {}).get('readers', [])
    return {'read_count': len(readers)}

  @staticmethod
  def _reader(ADS_record):
    result = ADS_record.get('adsdata', {}).get('readers', [])
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
    simbad = SolrAdapter.convert_simbad(ADS_record.get('adsdata',{}).get('simbad_objects',[]))
    result = [int(i['id']) for i in simbad] # ADS_record.get('adsdata',{}).get('simbad_objects',[])]
    return {'simbid': result}

  @staticmethod
  def convert_simbad(simbad_strings):
    """convert sql string to the dict mongo used so other code can remain unchanged
    sql version contains an array of strings: ['1010152 PN', '1010659 PN', '1011325 PN']"""
    # first, check to see if conversion is needed
    # if passed an array of dicts, simply return it
    if (isinstance(simbad_strings, list) and len(simbad_strings) > 0 
        and isinstance(simbad_strings[0], dict)):
        return simbad_strings

    #otherwise, process
    simbad_dicts = []
    if simbad_strings is None:
      return simbad_dicts
    for current in simbad_strings:
      current = current.strip()
      parts = current.split(' ')
      if len(parts) == 2:
        d = {'type': unicode(parts[1]), 'id': unicode(parts[0])}
        simbad_dicts.append(d)
      else:
        print 'warning, bad length to simbad string {}'.format(current)

    return simbad_dicts



  @staticmethod
  def _simbtype(ADS_record):
    simbad = SolrAdapter.convert_simbad(ADS_record.get('adsdata', {}).get('simbad_objects', []))
    result = []
    for object in simbad: # ADS_record.get('adsdata',{}).get('simbad_objects',[]):
      otype = simbad_type_mapper(object['type'])
      result.append(otype)
    result = list(set(result))
    return {'simbtype': result}

  @staticmethod
  def _simbad_object_facet_hier(ADS_record):
    simbad = SolrAdapter.convert_simbad(ADS_record.get('adsdata', {}).get('simbad_objects', []))
    result = []
    for object in simbad:  # ADS_record.get('adsdata',{}).get('simbad_objects',[]):
      otype = simbad_type_mapper(object['type'])
      r = u"0/%s" % (otype,)
      result.append(r)
      r = u"1/%s/%s" % (otype, object['id'])
      result.append(r)
    return {'simbad_object_facet_hier': result}

  @staticmethod
  def _title(ADS_record):
    result = [i['text'] for i in ADS_record['metadata']['general'].get('titles', [])]
    return {'title':result}

  @staticmethod
  def _volume(ADS_record):
    return {'volume': ADS_record['metadata']['general'].get('publication', {}).get('volume')}

  @staticmethod
  def _vizier(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['properties'].get('vizier_tables', [])]
    return {'vizier': result}

  @staticmethod
  def _vizier_facet(ADS_record):
    result = [i['content'] for i in ADS_record['metadata']['properties'].get('vizier_tables', [])]
    return {'vizier_facet': result}    

  #------------------------------------------------
  # Public Entrypoints
  @classmethod
  def adapt(cls, ADS_record):
    assert isinstance(ADS_record, dict)
    result = {}
    for k in cls.SCHEMA:
      try:
        D = getattr(cls, '_%s' % k)(ADS_record)
        v = D.values()
        if not v or (len(v) == 1 and not isinstance(v[0], int) and not isinstance(v[0], float) and not v[0]):
          D = {}
        result.update(D)
      except AttributeError, e:
        logger.debug("NotImplementedWarning: %s" % e)
        if "type object 'SolrAdapter'" not in e.message:
          raise
        # raise NotImplementedError
      except KeyError, e:
        if 'id' in e.message:
          logger.debug('in adapt, ignoring key error for id field')
        else:
          logger.info('in adapt, key error: {} {}'.format(e, e.message))
          raise e
    return result

  @classmethod
  def validate(cls, solr_record):
    '''
    Validates types and keys of `record` against self.schema.
    Raises AssertionError if types or keys do not match
    '''
    r = solr_record
    SCHEMA = cls.SCHEMA
    assert isinstance(r, dict)
    for k, v in r.iteritems():
      assert k in SCHEMA, '{0}: not in schema'.format(k)
      assert isinstance(v, type(SCHEMA[k])), '{0}: has an unexpected type ({1}!={2}): {3}'.format(k, type(v), SCHEMA[k], v)
      if isinstance(v, list) and v:  # No expectation of nested lists
        assert len(set([type(i) for i in v])) == 1, "{0}: multiple data-types in list: {1}".format(k, v)
        assert isinstance(v[0], type(SCHEMA[k][0])), "{0}: inner list element has unexpected type ({1}!={2}): {3}".format(k, type(v[0]), type(SCHEMA[k][0]), v)


def unroll_unique_list(array):
  """
  Takes a list in input, unpacks nested elements, uniques them,
  and returns a list.  Used to normalize some fields such as
  isbns and issns for which different data structures may be
  created by the json import due to XML element multiplicity
  (or lack thereof).  Yes, it's a hack that could be avoided if
  we tightened the Enforcer code.
  """
  result = []
  for i in array:
    if isinstance(i, list):
      result += i
    else:
      result.append(i)
  return list(set(result))

doctype_dict = {
  'article':       'Journal Article',
  'proceedings':   'Proceedings',
  'inproceedings': 'Proceedings Article',
  'book':          'Book',
  'inbook':        'Book Chapter',
  'techreport':    'Tech Report',
  'intechreport':  'In Tech Report',
  'eprint':        'e-print',
  'abstract':      'Abstract',
  'mastersthesis': 'Masters Thesis',
  'phdthesis':     'PhD Thesis',
  'talk':          'Talk',
  'software':      'Software',
  'proposal':      'Proposal',
  'pressrelease':  'Press Release',
  'circular':      'Circular',
  'newsletter':    'Newsletter',
  'catalog':       'Catalog',
  'misc':          'Other'
}

def doctype_mapper(doctype):
  """
  Maps a document type to pair of hierarchical entries
  which include the top-level type and the type used for
  facets
  """
  htype = 'Article' if doctype in ARTICLE_TYPES else 'Non-Article'
  stype = doctype_dict.get(doctype, 'Other')
  return (htype, stype)
    

def simbad_type_mapper(otype):
  """
  Maps a native SIMBAD object type to a subset of basic classes
  used for searching and faceting.  Based on Thomas Boch's mappings
  used in AladinLite
  """
  if otype.startswith('G') or otype.endswith('G'):
    return u'Galaxy'
  elif otype == 'Star' or otype.find('*') >= 0:
    return u'Star'
  elif otype == 'Neb' or otype.startswith('PN') or otype.startswith('SNR'):
    return u'Nebula'
  elif otype == 'HII':
    return u'HII Region'
  elif otype == 'X':
    return u'X-ray'
  elif otype.startswith('Radio') or otype == 'Maser' or otype == 'HI':
    return u'Radio'
  elif otype == 'IR' or otype.startswith('Red'):
    return u'Infrared'
  elif otype == 'UV':
    return u'UV'
  else:
    return u'Other'

arxiv_categories = set(["acc.phys.",
                        "adap.org.",
                        "alg.geom.",
                        "ao.sci...",
                        "astro.ph.",
                        "atom.ph..",
                        "bayes.an.",
                        "chao.dyn.",
                        "chem.ph..",
                        "cmp.lg...",
                        "comp.gas.",
                        "cond.mat.",
                        "cs.......",
                        "dg.ga....",
                        "funct.an.",
                        "gr.qc....",
                        "hep.ex...",
                        "hep.lat..",
                        "hep.ph...",
                        "hep.th...",
                        "math.....",
                        "math.ph..",
                        "mtrl.th..",
                        "nlin.....",
                        "nucl.ex..",
                        "nucl.th..",
                        "patt.sol.",
                        "physics..",
                        "plasm.ph.",
                        "q.alg....",
                        "q.bio....",
                        "quant.ph.",
                        "solv.int.",
                        "supr.con."])


def bibstem_mapper(bibcode):
  short_stem = bibcode[4:9]
  long_stem = bibcode[4:13]
  vol_field = bibcode[9:13]
  # first take care of special cases
  # ApJL
  if short_stem == 'ApJ..' and bibcode[13:14] == 'L':
    short_stem = u'ApJL.'
  # MPECs have a letter in the journal field which should be ignored
  elif short_stem == 'MPEC.' and re.match(r'^[\.\w]+$', vol_field):
    vol_field = u'....'
  # map old arXiv bibcodes to arXiv only
  elif long_stem in arxiv_categories:
    short_stem = u'arXiv'
    vol_field = u'....'
  long_stem = short_stem + vol_field
  return (unicode(short_stem), unicode(long_stem))



def transform_json_record(db_record):
    out = {'bibcode': db_record['bibcode']}
    
    for f, t in [('id', 'id'), ('bib_data', ''), ('nonbib_data', 'adsdata'), ('orcid_claims', 'orcid_claims')]:
        if db_record.get(f, None):
            if t:
                out[t] = db_record.get(f)
            else:
                out.update(db_record.get(f))
    if db_record.get('fulltext', None):
        out['body'] = db_record['fulltext']
    
    return out

