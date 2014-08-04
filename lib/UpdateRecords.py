import os,sys
import collections
import itertools
import datetime

from rules import merger
import EnforceSchema

def updateRecords(records):
  completeRecords = []
  for r in records:
    #Define top-level schema
    cr = {
      'bibcode': r['@bibcode'],
      'JSON_fingerprint': r['JSON_fingerprint'],
      'metadata' : {},
      'text': {},
      'modtime': '',
    }

    #Multiply defined blocks need merging.
    metadataCounter = collections.Counter([entry['@type'] for entry in r['metadata']])
    needsMerging = dict([(k,[]) for k,v in metadataCounter.iteritems() if v>1])

    #Iterate over metadata blocks; directly input single defined blocks
    #and build a 'needsMerging' list to merge in the next step
    for metadataBlock in r['metadata']: 
      for field,data in metadataBlock.iteritems():
        if field not in ['@origin','modification_time','creation_time','@type']:
          metadataBlock[field] = {
            '@origin':metadataBlock['@origin'].upper(),
            'content':EnforceSchema.NORMALIZE_SCHEMA[field](data) if field in EnforceSchema.NORMALIZE_SCHEMA else data,
            'modtime':metadataBlock.get('modification_time',metadataBlock.get('creation_time',0))
          }
      if metadataBlock['@type'] not in needsMerging:
        cr['metadata'].update({metadataBlock['@type']:metadataBlock})
      else: #If it shows up more than once, it needs merging.
        needsMerging[metadataBlock['@type']].append(metadataBlock)
    #Now merge the multiply defined metadataBlocks
    for entryType,data in needsMerging.iteritems():
      cr['metadata'].update({entryType:_merge(data,r['@bibcode'],entryType)})
    cr['modtime'] = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

    #Finally, we have a complete record
    completeRecords.append(EnforceSchema.enforceSchema(cr))

  return completeRecords

def _merge(metadataBlocks,bibcode,entryType):
  '''
  Merges multiply defined fields within a list of <metadata> blocks
  Returns a single (merged) <metadata> block
  '''
  fieldsHist = collections.Counter([i for i in list(itertools.chain(*metadataBlocks)) if not i.startswith('@')])
  singleDefinedFields = [k for k,v in fieldsHist.iteritems() if v==1]
  multipleDefinedFields = [k for k,v in fieldsHist.iteritems() if v>1]
  
  #Create intermediate data structure that lets us easily iterate over those fields that merging, and
  #store the necessary metadata for mergingfg
  fields = {}
  altpubs = []
  for block in metadataBlocks:
    primary = block.get('@primary',{}).get('content',"True")
    primary = False if primary.lower()=="false" else True
    if not primary:
      altpubs.append(block)
    for fieldName,data in block.iteritems():
      if fieldName not in multipleDefinedFields:
        continue
      if fieldName not in fields:
        fields[fieldName] = []
      fields[fieldName].append({
        '@origin':block['@origin'].upper(),
        'content':data['content'] if isinstance(data,dict) else data,
        'modtime':block.get('modification_time',block.get('creation_time',0)),
        '@primary': primary,
      })

  #Merge those fields that are multiply defined      
  mergedResults = {}
  for fieldName,data in fields.iteritems():
    result = None
    while len(data) > 0:
      f1 = data.pop()
      f2 = result if result else data.pop()
      result = merger.dispatcher(f1,f2,fieldName)
    mergedResults[fieldName] = result
  
  #Combine all the pieces into the complete <metadata> block
  completeBlock = {'@type':entryType,}
  singleDefined = dict([(k,v) for block in metadataBlocks for k,v in block.iteritems() if k in singleDefinedFields])
  completeBlock.update({'altpubs':altpubs})
  completeBlock.update(singleDefined)
  completeBlock.update(mergedResults)

  return completeBlock