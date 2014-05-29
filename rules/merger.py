import sys,os
from rules.rsettings import (MERGER_RULES,PRIORITIES,REFERENCES_ALWAYS_APPEND)
from settings import LOGGER
import datetime
import settings
import types
import itertools
#Maybe re-write this as a class since we need access to f1,f2 etc everywhere

def dispatcher(f1,f2,fieldName,*args,**kwargs):
  '''
  Provides a first order security for string mappings via eval()
  '''

  if fieldName not in MERGER_RULES:
    fieldName = 'default'


  if type(MERGER_RULES[fieldName])==types.FunctionType:
    return MERGER_RULES[fieldName](f1,f2,fieldName, *args, **kwargs)
  else:
    #Assert that the string maps to function defined within this module
    assert type(eval(MERGER_RULES[fieldName]))==types.FunctionType
    assert MERGER_RULES[fieldName] in dir(sys.modules[__name__])
    return eval(MERGER_RULES[fieldName])(f1,f2,fieldName,*args,**kwargs)

def booleanMerger(f1,f2,*args,**kwargs):
  f = stringConcatenateMerger(f1,f2) #use stringConcatMerger to ensure formatting even though @origin isn't very useful in this content
  f['content'] = False
  if any([  i for i in [int(f1['content']),int(f2['content'])]  ]):
    f['content'] = True
  return f


def takeAll(f1,f2,*args,**kwargs):
  c1,c2 = f1['content'],f2['content']

  # Assert:
  # 1. Content is a list
  # 2. There is only one type of element in each list
  assert type(c1)==type(c2)==list
  assert len(set([type(i) for i in c1]))==len(set([type(i) for i in c1]))==1

  #If the elements aren't dicts, simply return the union
  if not isinstance(c1[0], dict):
    return list( set(c1).union(c2) ) 

  #If the elements are dicts, we need to deconstruct each dict, compare if it is duplicated, and then re-constuct
  #We won't go deeper than the k,v pair: ie, we will ignore if v is a nested structure
  elif isinstance(c1[0], dict):
    result = {}
    for L in [c1,c2]:
      L = L if isinstance(L,list) else [L]
      for D in L:
        for k,v in D.iteritems():
          v = v if isinstance(v,list) else [v]
          if k not in result:
            result[k] = []
          if v not in result[k]:
            result[k].append(v)
    for k,v in result.iteritems():
      #Flatten the values of the dict
      result[k] = list(itertools.chain(*v))
    return {'content':[result], '@origin': '%s; %s' % (f1['@origin'],f2['@origin'])}

  #If elements are neither, we have a problem!
  LOGGER.critical('takeAll merger didnt get normalized data')
  raise TypeError (c1,c2)

def stringConcatenateMerger(f1,f2,*args,**kwargs):
  f1['content'] = "%s,%s" % (f1['content'],f2['content'])
  f1['@origin'] = "%s; %s" % (f1['@origin'],f2['@origin'])
  return f1

def authorMerger(f1,f2,*args,**kwargs):
  assert isinstance(f1['content'],list)
  assert isinstance(f2['content'],list)

  best = originTrustMerger(f1,f2,'author')
  for author in best['content']:
    if 'affiliations' not in author:
      _all = f1['content']+f2['content']
      matches = [i for i in _all if i['name']['normalized']==author['name']['normalized'] and 'affiliations' in i]
      #In the case that a there are multiple authors with the same normalized name in the list, matches will have len>1.
      #This will blindly pick the first one that matched, which isn't necessarily correct.
      if matches:
        author['affiliations'] = matches[0]['affiliations']
  return best

def referencesMerger(f1,f2,*args,**kwargs):
  assert type(f1['content'])==type(f2['content'])==list
  if f1['@origin'] in REFERENCES_ALWAYS_APPEND or f2['@origin'] in REFERENCES_ALWAYS_APPEND:
    result = takeAll(f1,f2)
    result['@origin'] = '%s; %s' % (f1['@origin'],f2['@origin'])
    return result
  return originTrustMerger(f1,f2,'reference')


def originTrustMerger(f1,f2,fieldName,*args,**kwargs):
  assert(f1['@origin'])
  assert(f2['@origin'])
  
  if fieldName not in PRIORITIES:
    fieldName = 'default'
  
  #Maybe we should pick the one with the highest origin instead of the first one...
  f1['@origin'] = f1['@origin'] if f1['@origin'] in PRIORITIES[fieldName] else f1['@origin'].split(';')[0]
  f2['@origin'] = f2['@origin'] if f2['@origin'] in PRIORITIES[fieldName] else f2['@origin'].split(';')[0]

  P1 = PRIORITIES[fieldName][f1['@origin']]
  P2 = PRIORITIES[fieldName][f2['@origin']]
  
  if P1 == P2:
    return equalTrustFallback(f1,f2)

  return f1 if P1 > P2 else f2

def equalTrustFallback(f1,f2,*args,**kwargs):
  # Return priority:
  # 1. field with most content
  # 2. field with most recent modtime
  # 3. f1
  dateformat = '%Y-%m-%dT%H:%M:%S'
  f1['modtime'] = datetime.datetime.strptime(f1['modtime'],dateformat) if f1['modtime'] else 0
  f2['modtime'] = datetime.datetime.strptime(f2['modtime'],dateformat) if f2['modtime'] else 0

  if len(f1['content']) != len(f2['content']):
    return f1 if len(f1['content']) > len(f2['content']) else f2
  
  elif f1['modtime'] != f2['modtime']:
    return f1 if f1['modtime'] > f2['modtime'] else f2
  
  else:
    return f1