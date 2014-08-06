import os,sys
import collections
import itertools
import datetime

from lib import merger
from lib import EnforceSchema

def mergeRecords(records):
  completeRecords = []
  e = EnforceSchema.Enforcer()
  for r in e.ensureList(records):
    blocks = e.ensureList(r['metadata'])
    #Multiply defined blocks need merging.
    metadatablockCounter = collections.Counter([i['tempdata']['type'] for i in blocks])
    needsMerging = dict([(k,[]) for k,v in metadatablockCounter.iteritems() if v>1])

    completeMetadata = {}
    #First pass: Add the singly defined blocks to the complete record
    for b in blocks:
      _type = b['tempdata']['type']
      if _type not in needsMerging:
        completeMetadata[_type] = b
      else:
        needsMerging[_type].append(b)

    #Second pass: Merge the multiple defined blocks
    for _type,blocks in needsMerging.iteritems():
      m = merger.Merger(blocks)
      m.merge()
      completeMetadata.update({
        _type: m.block,
      })

    #Finally, we have a complete record
    r['metadata'] = completeMetadata
    completeRecords.append(e.finalPassEnforceSchema(r))


  return completeRecords