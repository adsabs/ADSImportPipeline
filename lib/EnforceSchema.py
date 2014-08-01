import collections
import settings

NORMALIZE_SCHEMA = {
  'arxivcategories':  lambda d: ensureList(d),
  'author':           lambda d: ensureList(d),
  'keywords':         lambda d: ensureList(d),
  'title':            lambda d: ensureLanguageSchema(d),
  'abstract':         lambda d: ensureLanguageSchema(d),
  'dates':            lambda d: ensureList(d),
  'isbns':            lambda d: ensureList(d),
  'issns':            lambda d: ensureList(d),
  'databases':        lambda d: ensureList(d),
  'bibgroups':        lambda d: ensureList(d),
  'reference':        lambda d: ensureList(d),
  'alternates':       lambda d: ensureList(d),
  'associates':       lambda d: ensureList(d),
  'links':            lambda d: ensureList(d),
}

def ensureLanguageSchema(item):
  if isinstance(item,basestring):
    L = [{
      '@lang':'en',
      '#text': item
    }]
  else:
    L = ensureList(item)
    for i in L:
      if '@lang' not in i:
        i['@lang'] = 'en'
  return L

def ensureList(item):
  return item if isinstance(item,list) else [item]

def enforceSchema(record):
  '''
  translates schema from ADSRecords to alternative schema
  '''

  #1. Delete fields that we no longer want
  for deletion in settings.SCHEMA['deletions']:
    current_loc=record
    for key in deletion[:-1]:
      current_loc=current_loc[key]
    try:
      del current_loc[deletion[-1]]
    except KeyError:
       pass

  #Metadatablock "general"
  block='general'
  m='metadata'
  if 'electronic_id' in record[m][block]:
    for field in ['page','page_range']:
      if field in record[m][block]:
        del record[m][block][field]
  if 'page' in record[m][block] and 'page_range' in record[m][block] and record[m][block]['page'] == record[m][block]['page_range']:
    del record[m][block]['page_range']

  #  arxivcategories
  f = 'arxivcategories'
  record[m][block][f] = record[m][block].get(f,[])
  if record[m][block][f]:
    current = record[m][block][f]['content']
    res = []
    for i in current:
      content = i['arxivcategory']
      for j in ensureList(content):
        if isinstance(j,str):
          res.append(j)
        elif isinstance(j,dict):
          res.append(j['#text'])
    record[m][block][f] = res

  #  keywords
  f = 'keywords'
  record[m][block][f] = record[m][block].get(f,[])
  if record[m][block][f]:
    res = []
    for c in record[m][block][f].get('content',record[m][block][f]):
      content = c.get('content',c)
      origin = c['@origin'] if '@origin' in c else record[m][block][f]['@origin']
      type_ =  content['@type']
      for keyword in ensureList(content['keyword']):
        res.append({
          '@origin':origin,
          '@type': type_,
          'channel': keyword.get('channel',None),
          'original': keyword.get('original',None),
          'normalized': keyword.get('normalized',None),
          })
    record[m][block][f] = res

  f = 'title'
  record[m][block][f] = record[m][block].get(f,[])
  if record[m][block][f]:
    record[m][block][f] = record[m][block][f]['content']

  f = 'abstract'
  record[m][block][f] = record[m][block].get(f,[])
  if record[m][block][f]:
    res = []
    c = record[m][block][f]['content']
    origin = record[m][block][f].get('@origin',None)
    if 'content' in c:
      c = c['content']
      origin = c.get('@origin',origin)
    for a in c:
      res.append({
        '@origin' : origin,
        '@lang': a['@lang'],
        '#text': a['#text'],
        })
    record[m][block][f] = res

  # authors
  f = 'author'
  record[m][block][f] = record[m][block].get(f,[])
  if record[m][block][f]:
    record[m][block][f] = record[m][block][f]['content']
    res = []
    for a in record[m][block][f]:
      orcid = ensureList(a.get('author_ids',[]))
      assert len(orcid)==1 or len(orcid)==0
      orcid = orcid[0]['author_id'].replace('ORCID:','') if orcid else None
      res.append( {
        '@nr': a['@nr'],
        'type': a.get('type',None),
        'affiliations': [i.get('affiliation',None) for i in ensureList(a.get('affiliations',[]))],
        'emails': [i['email'] for i in ensureList(a.get('emails',[]))],
        'orcid': orcid,
        'name': {
          'native': a['name'].get('native',None),
          'western': a['name'].get('western',None),
          'normalized': a['name'].get('normalized',None),
        },
      })
    record[m][block][f] = res

  # language
  f = 'language'
  record[m][block][f] = record[m][block].get(f,[])

  #  pages
  f = 'pages'
  subfields = ['pagenumber','page_range',{'lastpage':'page_last'},'page']
  record[m][block][f] = {}
  origins = []
  for sf in subfields:
    translation = sf
    if isinstance(sf,dict):
      sf,translation = sf.items()[0]
    res = record[m][block].get(sf,{})
    record[m][block][f][translation] = res.get('content',None)
    origins.append(res.get('@origin',None))
    try:
      del record[m][block][sf]
    except KeyError:
      pass
  try:
    record[m][block][f]['@origin'] = max(collections.Counter([i for i in origins if i]))
  except ValueError:
    record[m][block][f]['@origin'] = None

  # dates
  f = 'dates'
  record[m][block][f] = record[m][block].get(f,{})
  if record[m][block][f]:
    res = {}
    if 'publication_year' in record[m][block]:
      res['publication_year'] = {
        '@origin': record[m][block]['publication_year']['@origin'],
        'content': record[m][block]['publication_year']['content'],
      }
      del record[m][block]['publication_year']
    for c in ensureList(record[m][block][f].get('content',[])):
      res[c['date']['@type']] = {
        '@origin': c.get('@origin',record[m][block][f]['@origin']),
        'content': c['date']['#text'],
      }
    record[m][block][f] = res

  #  journal
  f = 'journal'
  subfields = ['volume','issue']
  raw = record[m][block].get(f,{}).get('content',None)
  record[m][block][f] = {}
  record[m][block][f]['name'] = {
    'raw': raw,
    'canonical': record[m][block].get('canonical_journal',{}).get('content',None),
  }
  try:
    del record[m][block]['canonical_journal']
  except KeyError:
    pass
  origins = []
  for sf in subfields:
    res = record[m][block].get(sf,None)
    record[m][block][f][sf] = None
    if res:
      record[m][block][f][sf] = res['content']
      origins.append(res['@origin'])
    try:
      del record[m][block][sf]
    except KeyError:
      pass
  try:
    record[m][block][f]['@origin'] = max(collections.Counter([i for i in origins if i]))
  except ValueError:
    record[m][block][f]['@origin'] = None

  # electronic_id, conf_metadata, DOI, copyright
  fields = ['electronic_id','conf_metadata','DOI','copyright']
  for f in fields:
    record[m][block][f.lower()] = record[m][block].get(f,{})
    try:
      del record[m][block][f]['modtime']
    except KeyError:
      pass

  #comment, pubnote
  fields = ['comment','pubnote']
  for f in fields:
    record[m][block][f] = record[m][block].get(f,{})
    if record[m][block][f]:
      res = record[m][block][f]
      record[m][block][f] = {
        'content': res['content']['#text'],
        '@origin': res['@origin'],
      }


  # isbns, issns, objects
  fields = ['isbns','issns','objects']
  for f in fields:
    record[m][block][f] = record[m][block].get(f,[])
    if record[m][block][f]:
      res = []
      for c in ensureList(record[m][block][f].get('content',record[m][block][f])):
        res.append({
          '@origin':c.get('@origin',record[m][block][f]['@origin']),
          'content':c.get('content',c)[f[:-1]],
          })
      record[m][block][f] = res

  # instruments
  f = 'instruments'
  record[m][block][f] = record[m][block].get(f,[])
  if record[m][block][f]:
    res = []
    for c in ensureList(record[m][block][f]):
      res.append({
          '@origin':c.get('@origin',record[m][block][f]['@origin']),
          'content':c.get('content',c),
        })
    record[m][block][f] = res

  #Metadatablock "properties"
  block='properties'

  f = 'associates'
  record[m][block][f] = record[m][block].get(f,[])
  res = []
  if record[m][block][f]:
    for c in ensureList(record[m][block][f]['content']):
      origin = c.get('@origin',record[m][block][f]['@origin'])
      if 'content' in c: #This happens in the case of certain merged cases
        c = c['content']
        origin = c.get('@origin',origin)
      for a in c['associate']:
        res.append({
          '@origin': origin,
          'comment': a.get('@comment',None),
          'content': a.get('#text',None),
        })
  record[m][block][f] = res

  fields = ['databases','bibgroups']
  for f in fields:
    record[m][block][f] = record[m][block].get(f,[])
    if record[m][block][f]:
      res = []
      for c in record[m][block][f].get('content',record[m][block][f]):
        res.append({
          '@origin':c.get('@origin',record[m][block][f]['@origin']),
          'content':c.get('content',c)[f[:-1]],
          })
      record[m][block][f] = res

  f = 'pubtype'
  record[m][block][f] = record[m][block].get(f,{})
  if record[m][block][f]:
    record[m][block][f] = {
      '@origin':record[m][block][f]['@origin'],
      'content':record[m][block][f]['content'],
    }

  fields = ['openaccess','nonarticle','ocrabstract','private','refereed']
  for f in fields:
    record[m][block][f] = record[m][block].get(f,None)
    if record[m][block][f]:
      if record[m][block][f]['content']=="1":
        record[m][block][f] = True
      elif record[m][block][f]['content']=="0":
        record[m][block][f] = False
      else:
        record[m][block][f] = record[m][block][f]['content']

  block = 'references'
  record[m][block] = record[m].get(block,[])
  res = []
  if record[m][block]:
    for c in record[m][block]['reference']['content']:
      origin = c.get('@origin',record[m][block]['reference']['@origin'])
      if 'content' in c: #This happens in the case of certain merged cases
        c = c['content']
        origin = c.get('@origin',origin)
      res.append({
        '@origin':origin,
        'bibcode':c.get('@bibcode',None),
        'doi':c.get('@doi',None),
        'score':c.get('@score',None),
        'extension':c.get('@extension',None),
        'arxid': c.get('@arxid',None),
        'content': c.get('#text',None)
      })
    record[m][block] = res

  block='relations'
  f = 'preprintid'
  res = []
  record[m][block] = record[m].get(block,{})
  record[m][block][f] = record[m][block].get(f,[])
  if record[m][block][f]:
    c = []
    for i in ensureList(record[m][block][f]['content']):
      if i not in c:
        c.append(i)
    assert len(c) == 1
    c = c[0]
    origin = c.get('@origin',record[m][block][f]['@origin'])
    if 'content' in c: #This happens in the case of certain merged cases
      c = c['content']
      origin = c.get('@origin',origin)
    res = {
      '@origin':origin,
      '@ecode': c.get('@ecode',None),
      'content': c.get('#text',None)
    }
  record[m][block]['preprint'] = res
  del record[m][block][f]

  f = 'alternates'
  record[m][block][f] = record[m][block].get(f,[])
  res = []
  if record[m][block][f]:
    for c in ensureList(record[m][block][f]['content']):
      if not c:
        continue
      origin = c.get('@origin',record[m][block][f]['@origin'])
      if 'content' in c: #This happens in the case of certain merged cases
        c = c['content']
        origin = c.get('@origin',origin)
        for alt in ensureList(c['alternate']):
          res.append({
            '@origin':origin,
            '@type': alt.get('@type',None),
            'content': alt.get('#text',None)
          })
    record[m][block][f] = res

  f = 'links'
  record[m][block][f] = record[m][block].get(f,[])
  res = []
  if record[m][block][f]:
    for c in ensureList(record[m][block][f]['content']):
      if not c:
        continue
      origin = c.get('@origin',record[m][block][f]['@origin'])
      if 'content' in c: #This happens in the case of certain merged cases
        c = c['content']
        origin = c.get('@origin',origin)
      for ln in ensureList(c['link']):
        if ln.get('@type',None) == "ADSlink":
          continue
        res.append({
          '@origin':origin,
          '@type':ln.get('@type',None),
          'content': ln.get('@url',None)
        })
    record[m][block][f] = res


  #3. Unique based on key,value within lists of dicts:
  for block,fields in record[m].iteritems():
    if block=='references':
      continue
    for field,value in fields.iteritems():
      if not value:
        continue
      res = value
      if isinstance(value,list):
        if isinstance(value[0],list):
          res = list(set(value))
        elif isinstance(value[0],dict):
          res = []
          for c in value:
            if c not in res:
              res.append(c)
      record[m][block][field] = res

  return record
