import collections
import settings
import datetime

class Enforcer:
  '''
  translates schema from ADSRecords to alternative schema
  '''
  def __init__(self,datefmt='%Y-%m-%dT%H:%M:%S.%fZ',solrTimeoffset={'minutes':30}):
    '''
    datefmt and solrTimeoffset should be synchronized with what solr expects.
    If they are not, solr will return incorrect dates in some cases.
    '''

    self.dispatcher = {
      'general': self._generalEnforcer,
      'properties':self._propertiesEnforcer,
      'references':self._referencesEnforcer,
      'relations':self._relationsEnforcer,
    }
    self.datefmt=datefmt
    self.solrTimeoffset=solrTimeoffset

  def ensureLanguageSchema(self,item):
    if isinstance(item,basestring):
      L = [{
        'lang':'en',
        'text': item
      }]
    else:
      L = self.ensureList(item)
      for i in L:
        if '@lang' not in i:
          i['lang'] = 'en'
        if '#text' in i:
          i['text'] = i['#text']
          del i['#text']
    return L

  def ensureList(self,item):
    if item is None:
      return []
    return item if isinstance(item,list) else [item]

  def parseBool(self,item):
    if item is None:
      return item
    return False if item in ['false','False',False,'FALSE','f',0,'0'] else True

  def parseDate(self,datestr):
    formats = [
      self.datefmt,
      '%Y-%m-%d',
      '%Y-%m',
      '%Y',
    ]
    
    fullDate = True
    if '-00' in datestr:
      datestr = datestr.replace('-00','-01')
      fullDate = False
    if len(datestr)<10:
      fullDate = False

    for f in formats:
      try:
        date = datetime.datetime.strptime(datestr,f)
        if fullDate:
          date += datetime.timedelta(**self.solrTimeoffset)
        date = date.strftime(self.datefmt)
      except ValueError:
        pass
    return date

  def finalPassEnforceSchema(self,record):
    '''
    Responsible for final cleanup of data before writing to mongo
    . Removes unnecessary fields
    . ensures metadata elements are defined
    '''
    blocklevel_removals = ['tempdata']
    toplevel_removals = ['@bibcode']
    for i in toplevel_removals:
      if i in record:
        del record[i]

    for blocks in [record['metadata'],record['text']]:
      for key,block in blocks.iteritems():
        for i in blocklevel_removals:
          if i in block:
            del block[i]
    
    for k in self.dispatcher.keys():
      if k not in record['metadata']:
        record['metadata'][k] = {} if k != 'references' else []

    if record['metadata']['references']:
      record['metadata']['references'] = record['metadata']['references']['references']

    if record['metadata']['general']:
      del record['metadata']['general']['publication']['altbibcode']

    #Coerce to correct type
    return record

  def enforceTextSchema(self,block):
    g = block.get
    eL = self.ensureList
    eLS = self.ensureLanguageSchema
    
    r = {}
    r['body'] = g('body')
    r['acknowledgments'] = g('acknowledgments')
    r['creation'] = g('creation')

  def enforceTopLevelSchema(self,record,JSON_fingerprint):
    r = {}
    r['JSON_fingerprint'] = JSON_fingerprint
    r['bibcode'] = record['@bibcode']
    r['modtime'] = datetime.datetime.now().strftime(self.datefmt)
    r['text'] = {}
    r['text']['body'] = []
    r['text']['acknowledgement'] = []
    fields = ['body','acknowledgement']
    for f in fields:
      t = record.get('text') if record.get('text') else {}
      blocks = self.ensureList(t.get(f))
      for b in blocks:
        r['text'][f].append({
          'content':b['#text'],
          'provider': b['@origin'],
          'modtime': datetime.datetime.fromtimestamp(float(b['@time_stamp'])).strftime(self.datefmt),
          'tempdata': {
            'origin': b['@origin'],
            'primary': True,
            'modtime': datetime.datetime.fromtimestamp(float(b['@time_stamp'])).strftime(self.datefmt),
            },
        })

    r['metadata'] = record['metadata']
    return r

  def enforceMetadataSchema(self,blocks):
    results = []
    for block in self.ensureList(blocks):
      b = self.dispatcher[block['@type']](block)
      results.append(b)
    return results

  def _generalEnforcer(self,block):
    #Shorthands
    g = block.get
    eL = self.ensureList
    eLS = self.ensureLanguageSchema

    r = {}

    #tempdata necessary for some merger rules; will be deleted before commiting to mongo
    r['tempdata'] = {
      'primary':            self.parseBool(g('@primary',True)) ,
      'alternate_journal':  self.parseBool(g('@alternate_journal',False)),
      'type':               g('@type'),
      'origin':             g('@origin'),
      'modtime':            g('modification_time'),
    }

    r['arxivcategories'] = [i['#text'] if isinstance(i,dict) else i for i in eL(g('arxivcategories',{}).get('arxivcategory',[]))]

    r['keywords'] = []
    for i in eL(g('keywords',[])):
      for j in eL(i.get('keyword',[])):
        r['keywords'].append({
          'origin':     g('@origin'),
          'type':       i.get('@type'),
          'channel':    j.get('@channel'),
          'original':   j.get('original'),
          'normalized': j.get('normalized'),
          })
    
    r['titles'] = []
    for i in eLS(g('title',[])):
      r['titles'].append(i)

    r['abstracts'] = []
    for i in eLS(g('abstract',[])):
      i['origin'] = g('@origin')
      r['abstracts'].append(i)

    r['authors'] = []
    for i in eL(g('author',[])):
      orcid = eL(i.get('author_ids',[]))
      assert len(orcid)==1 or len(orcid)==0
      orcid = orcid[0]['author_id'].replace('ORCID:','') if orcid else None
      r['authors'].append({
        'number':         i.get('@nr'),
        'type':           i.get('type'),
        'affiliations':   [j.get('affiliation') for j in eL(i.get('affiliations',[]))],
        'emails':         [j['email'] for j in eL(i.get('emails',[]))],
        'orcid':          orcid,
        'name': {
          'native':     i['name'].get('native'),
          'western':    i['name'].get('western'),
          'normalized': i['name'].get('normalized'),
        },
      })

    r['publication'] = {}
    r['publication']['origin'] =        g('@origin')
    r['publication']['volume'] =        g('volume')
    r['publication']['issue'] =         g('issue')
    r['publication']['page'] =          g('page')
    r['publication']['page_last'] =     g('lastpage')
    r['publication']['page_range'] =    g('page_range')
    r['publication']['page_count'] =    g('pagenumber')
    r['publication']['electronic_id'] = g('electronic_id')
    r['publication']['altbibcode'] =    g('bibcode')
    r['publication']['name'] = {
      'raw':        g('journal'),
      'canonical':  g('canonical_journal'),
    }

    r['publication']['dates'] = []
    for i in eL(g('dates',[])):
      r['publication']['dates'].append({
        'type':     i['date'].get('@type'),
        'content':  self.parseDate(i['date'].get('#text')),
      })
    if 'publication_year' in block:
      r['publication']['dates'].append({
        'type': 'publication_year',
        'content':  self.parseDate(g('publication_year')),
      })


    r['conf_metadata'] = {
      'origin': g('@origin'),
      'content': g('conf_metadata')
    }

    keys = ['pubnote','comment','copyright','DOI']
    for k in keys:
      r[k.lower()] = [{'origin': g('@origin'), 'content': i} for i in eL(g(k,[]))]

    keys = ['isbns','issns']
    for k in keys:
      r[k.lower()] = [{'origin': g('@origin'), 'content': i[k[:-1]]} for i in eL(g(k,[]))]
      
    return r

  def _propertiesEnforcer(self,block):
    r = {}
    g = block.get
    eL = self.ensureList

    #tempdata necessary for some merger rules; will be deleted before commiting to mongo
    r['tempdata'] = {
      'primary':            self.parseBool(g('@primary',True)) ,
      'alternate_journal':  self.parseBool(g('@alternate_journal',False)),
      'type':               g('@type'),
      'origin':             g('@origin'),
      'modtime':            g('modification_time'),
    }

    r['associates'] = []
    for i in eL(g('associates',[])):
      for j in eL(i.get('associate',[])):
        r['associates'].append({
          'origin': g('@origin'),
          'comment': j.get('@comment'),
          'content': j.get('#text'),
        })

    r['doctype'] = {
      'origin':   g('@origin'),
      'content':  g('pubtype'),
    }

    r['databases'] = []
    for i in eL(g('databases',[])):
      for j in eL(i.get('database',[])):
        r['databases'].append({
          'origin': g('@origin'),
          'content': j,
        })

    r['bibgroups'] = []
    for i in eL(g('bibgroups',[])):
      r['bibgroups'].append({
        'origin': g('@origin'),
        'content': i.get('bibgroup'),
      })
    


    for k in ['openaccess','ocrabstract','private','refereed']:
      r[k] = self.parseBool(g(k))

    return r

  def _referencesEnforcer(self,block):
    r = {}
    g = block.get
    eL = self.ensureList

    r['tempdata'] = {
      'primary':            self.parseBool(g('@primary',True)) ,
      'alternate_journal':  self.parseBool(g('@alternate_journal',False)),
      'type':               g('@type'),
      'modtime':            g('modification_time'),
      'origin':             g('@origin'),
    }

    r['references'] = []
    for i in eL(g('reference',[])):
      r['references'].append({
        'origin':     g('@origin'),
        'bibcode':    i.get('@bibcode'),
        'doi':        i.get('@doi'),
        'score':      i.get('@score'),
        'extension':  i.get('@extension'),
        'arxid':      i.get('@arxiv'),
        'content':    i.get('#text'),
        })
    return r

  def _relationsEnforcer(self,block):
    r = {}
    g = block.get
    eL = self.ensureList

    r['tempdata'] = {
      'primary':            self.parseBool(g('@primary',True)) ,
      'alternate_journal':  self.parseBool(g('@alternate_journal',False)),
      'type':               g('@type'),
      'modtime':            g('modification_time'),
      'origin':             g('@origin'),
    }

    r['preprints'] = []
    for i in eL(g('preprintid',[])):
      r['preprints'].append({
        'origin':   g('origin'),
        'ecode':    i.get('@ecode'),
        'content':  i.get('#text'),
      })

    r['alternates'] = []
    for i in eL(g('alternates',[])):
      for j in eL(i.get('alternate',[])):
        r['alternates'].append({
          'origin':   g('origin'),
          'type':     j.get('@type'),
          'content':  j.get('#text'),
        })

    r['links'] = []
    for i in eL(g('links',[])):
      for j in eL(i.get('link',[])):
        if j.get('@type')=='ADSlink': continue
        r['links'].append({
          'origin':   g('origin'),
          'type':     j.get('@type'),
          'url':      j.get('@url'),
          'title':    j.get('@title'),
          'count':    j.get('@count'),
        })
    return r
