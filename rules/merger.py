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
  return result

  #If elements are neither, we have a problem!
  LOGGER.critical('takeAll merger didnt get normalized data')
  raise TypeError (c1,c2)



def stringConcatenateMerger(f1,f2,*args,**kwargs):
  return "<%s><%s>" % (f1['content'],f2['content'])


# def authorMerger(f1,f2,*args,**kwargs):
#   #originTrustMerger used instead
#   pass

# def pubdateMerger(f1,f2,*args,**kwargs):
#   #originTrustMerger used instead
#   pass

def referencesMerger(f1,f2,*args,**kwargs):
  assert type(f1['content'])==type(f2['content'])==list
  if f1['@origin'] in REFERENCES_ALWAYS_APPEND or f2['@origin'] in REFERENCES_ALWAYS_APPEND:
    return takeAll(f1,f2)
  return originTrustMerger(f1,f2,'reference')



def originTrustMerger(f1,f2,fieldName,*args,**kwargs):
  assert(f1['@origin'])
  assert(f2['@origin'])
  
  if fieldName not in PRIORITIES:
    fieldName = 'default'
  
  #Maybe we should pick the one with the highest origin instead of the first one...
  f1['@origin'] = f1['@origin'] if f1['@origin'] in PRIORITIES[fieldName] else f1['@origin'].split(';')[0]
  f2['@origin'] = f2['@origin'] if f2['@origin'] in PRIORITIES[fieldName] else f2['@origin'].split(';')[0]

  if PRIORITIES[fieldName][f1['@origin']] == PRIORITIES[fieldName][f2['@origin']]:
    return equalTrustFallback(f1,f2)

  return f1['content'] if PRIORITIES[fieldName][f1['@origin']] >  PRIORITIES[fieldName][f2['@origin']] else f2['content']
  


def equalTrustFallback(f1,f2,*args,**kwargs):
  # Return priority:
  # 1. field with most content
  # 2. field with most recent modtime
  # 3. f1
  dateformat = '%Y-%m-%dT%H:%M:%S'
  f1['modtime'] = datetime.datetime.strptime(f1['modtime'],dateformat) if f1['modtime'] else 0
  f2['modtime'] = datetime.datetime.strptime(f2['modtime'],dateformat) if f2['modtime'] else 0

  if len(f1['content']) != len(f2['content']):
    return f1['content'] if len(f1['content']) > len(f2['content']) else f2['content']
  
  elif f1['modtime'] != f2['modtime']:
    return f1['content'] if f1['modtime'] > f2['modtime'] else f2['content']
  
  else:
    return f1['content']