import collections
import settings

class Enforcer:
  '''
  translates schema from ADSRecords to alternative schema
  '''
  def __init__(self):
    self.dispatcher = {
      'general': self._generalEnforcer,
      'properties':self._propertiesEnforcer,
      'references':self._referencesEnforcer,
      'relations':self._relationsEnforcer,
    }

  def ensureLanguageSchema(self,item):
    if isinstance(item,basestring):
      L = [{
        'lang':'en',
        'text': item
      }]
    else:
      L = ensureList(item)
      for i in L:
        if '@lang' not in i:
          i['lang'] = 'en'
        if '#text' in i:
          i['text'] = i['#text']
          del i['#text']
    return L

  def ensureList(self,item):
    return item if isinstance(item,list) else [item]

  def parseBool(self,item):
    return False if item in ['false','False',False,'FALSE','f'] else True

  def enforceSchema(self,blocks):
    results = []
    for block in blocks:
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
      'bibcode':            g('bibcode'),
    }

    r['arxivcategories'] = eL(g('arxivcategories',[]))
    
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
        'number': int(i['@nr']),
        'type': i.get('type'),
        'affiliations': [j.get('affiliation') for j in eL(i.get('affiliations',[]))],
        'emails': [j['email'] for j in eL(i.get('emails',[]))],
        'orcid': orcid,
        'name': {
          'native':     i['name'].get('native'),
          'western':    i['name'].get('western'),
          'normalized': i['name'].get('normalized'),
        },
      })

    r['pagination'] = {}
    r['pagination']['origin'] =         g('@origin')
    r['pagination']['page'] =           g('page')
    r['pagination']['page_last'] =      g('lastpage')
    r['pagination']['page_range'] =     g('page_range')
    r['pagination']['page_count'] =     g('pagenumber')
    r['pagination']['electronic_id'] =  g('electronic_id')

    r['publication'] = {}
    r['publication']['origin'] =  g('@origin')
    r['publication']['volume'] =  g('volume')
    r['publication']['issue'] =   g('issue')
    r['publication']['name'] = {
      'raw':        g('journal'),
      'canonical':  g('canonical_journal'),
    }

    r['dates'] = []
    for i in eL(g('dates',[])):
      r['dates'].append({
        i['date'].get('@type'): {
            'origin': g('@origin'),
            'content': i['date'].get('#text'),
          }
        })
    if 'publication_year' in block:
      r['dates'].append({
        'publication_year': {
          'origin': g('@origin'),
          'content': g('publication_year'),
          }
        })

    r['conf_metadata'] = {
      'origin': g('@origin'),
      'content': g('conf_metadata')
    }


    keys = ['pubnote','comment','copyright','isbns','issns','DOI']
    for k in keys:
      r[k.lower()] = [{'origin': g('@origin'), 'content': i} for i in eL(g(k,[]))]
    
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
    }

    r['associates'] = []
    for i in eL(g('associates',[])):
      for j in eL(i.get('associate',[])):
        r['associates'].append({
          'origin': g('@origin'),
          'comment': j.get('@comment'),
          'content': j.get('#text'),
        })

    r['pubtype'] = {
      'origin':   g('@origin'),
      'content':  g('pubtype'),
    }

    r['databases'] = []
    for i in eL(g('databases',[])):
      r['databases'].append({
        'origin': g('@origin'),
        'conent': i.get('database'),
      })

    for k in ['openaccess','nonarticle','ocrabstract','private','refereed']:
      r[k] = self.parseBool(g(k,False))

    return r



  def _referencesEnforcer(self,block):
    print "_referencesEnforcer NotYetImplemented"
  def _relationsEnforcer(self,block):
    print "_relationsEnforcer NotYetImplemented"
