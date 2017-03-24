import os,sys
import pymongo
import logging
import logging.handlers
from cloghandler import ConcurrentRotatingFileHandler
from collections import deque

class PipelineMongoConnection:

  def __init__(self,**kwargs):
    self.logger = kwargs.get('logger',None)
    if not self.logger:
      self.initializeLogging(**kwargs)

    self.host = kwargs.get('HOST',None)
    self.port = kwargs.get('PORT',None)
    self.database = kwargs.get('DATABASE',None)
    self.user = kwargs.get('USER',None)
    self.password = kwargs.get('PASSWD',None)
    self.collection = kwargs.get('COLLECTION',None)

    auth = ''
    if self.user and self.password:
      auth =  '%s@' % (':'.join([self.user,self.password]))
    self.uri = 'mongodb://%s%s:%s/%s' % (auth,self.host,self.port,self.database)

    self.conn = pymongo.MongoClient(host=self.uri)
    self.db = self.conn[self.database]

    if self.collection not in self.db.collection_names():
      self.initializeCollection()

  def getAllBibcodes(self):
    cur = self.db[self.collection].find({},{'bibcode':1,'_id':0})
    results = deque()
    while 1:
      try:
        results.append(cur.next()['bibcode'])
      except StopIteration:
        return list(results)

  def getRecordsFromBibcodes(self,bibcodes,key="bibcode",op="$in",query_limiter=None,iterate=False):
    if not iterate:
      results = self.db[self.collection].find({key: {op: bibcodes}},query_limiter)
      return list(results)
    cur = self.db[self.collection].find({key: {op: bibcodes}},query_limiter)
    results = deque()
    while 1:
      try:
        results.append(cur.next())
      except StopIteration:
        return list(results)

  def formatRecordsforReingestion(self,bibcodes):
    records = self.getRecordsFromBibcodes(
      bibcodes,
      query_limiter={'bibcode':1,'JSON_fingerprint':1,'_id':0}
    )
    return [[i['bibcode'],i['JSON_fingerprint']]for i in records]

  def initializeLogging(self,**kwargs):
    logfmt = '%(levelname)s\t%(process)d [%(asctime)s]:\t%(message)s'
    datefmt= '%m/%d/%Y %H:%M:%S'
    formatter = logging.Formatter(fmt=logfmt,datefmt=datefmt)
    LOGGER = logging.getLogger('PipelineMongoConnection')
    if not LOGGER.handlers:
      default_fn = os.path.join(os.path.dirname(__file__),'..','logs','PipelineMongoConnection.log')   
      fn = kwargs.get('logfile',default_fn)
      rfh = ConcurrentRotatingFileHandler(filename=fn,maxBytes=2097152,backupCount=10,mode='a') #2MB file
      rfh.setFormatter(formatter)
      ch = logging.StreamHandler() #console handler
      ch.setFormatter(formatter)
      #LOGGER.addHandler(ch)
      LOGGER.addHandler(rfh)
      LOGGER.setLevel(logging.DEBUG)
    self.logger = LOGGER

  def close(self):
    self.conn.close()

  def remove(self,spec_or_id=None,force=False):
    if not spec_or_id and not force:
      self.logger.warning("Recieved id_or_spec=None without force=True. Normally, this would remove all documents! Returning no-op now.")
      return
    self.db[self.collection].remove(spec_or_id=spec_or_id,fsync=True,w=1)

  def initializeCollection(self,_index='bibcode',**kwargs):
    self.logger.info('Initialize index %s for %s/%s' % (_index,self.database,self.collection))
    self.db[self.collection].ensure_index(_index,unique=True)
    
    self.logger.info('Initialize sequence collection for %s/%s' % (self.database,self.collection))
    self.db['%s_seq' % self.collection].insert({
      "_id": "seq",
      "counter": 0,
    })

  def _getNextSequence(self,name='seq'):
    #Todo: Implement a collection that records deleted docs, enabling us to re-use those _ids.
    result = self.db['%s_seq' % self.collection].find_and_modify(
      query={'_id':name},
      update={'$inc': {'counter':1}},
      new=True
    )
    return result['counter']

  def upsertRecords(self,records,**kwargs):
    '''
    Upserts ADS bibliographic records to mongo
    '''

    updates = [] #Just to keep track for logging's sake
    inserts = []

    def update(query,r,current):
      try:
        r['_id'] = current['_id']
        mongo.update(query,r,w=kwargs.get('w',1)) # put in dict? ,multi=kwargs.get('multi',False)) #w=1 means block all write requests until it has written to the primary)
        updates.append(r['bibcode'])
      except Exception, err:
        self.logger.error("Failure to UPDATE record %s: %s" % (query,err))

    def insert(query,r):
      try:
        r['_id'] = self._getNextSequence()
        mongo.insert(r,w=kwargs.get('w',1)) # ,multi=kwargs.get('multi',False)) #w=1 means block all write requests until it has written to the primary)
        inserts.append(r['bibcode'])
      except Exception, err:
        self.logger.error("Failure to INSERT record %s: %s" % (query,err))
        raise

    mongo = self.db[self.collection]

    if not records:
      self.logger.warning('upsertRecords: No records given')

    for r in records:
      #1. Check if a record with this bibcode is already in mongo
      query = {'bibcode': r['bibcode']}
      current = mongo.find_one(query)
      if current:
        update(query,r,current)
        continue

      #2. Check if a mongo record with this record's alternate bibcode exists
      for alternate in r['metadata']['relations'].get('alternates',[]):
        query = {'bibcode': alternate['content']}
        current = mongo.find_one(query)
        if current:
          self.logger.info('Alternate record %s will be overwritten by %s' % (query,r['bibcode']))
          update(query,r,current)
          break

      if not current:
        insert(query,r)

    self.logger.info("Performed %s updates and %s inserts to mongo" % (len(updates),len(inserts)))
    return updates+inserts

  def findNewRecords(self,records):
    '''
    Finds records in mongodb that need updating.
    Update criteria: JSON_fingerprint field different from the input records

    records: [(bibcode,JSON_fingerprint),...]
    '''
    if not records:
      self.logger.debug("findChangedRecords: No records given")
      return []

    currentRecords = [(r['bibcode'],r['JSON_fingerprint']) for r in self.db[self.collection].find({"bibcode": {"$in": [rec[0] for rec in records]}})]

    #If the JSON fingerprint is the string 'ignore' and it isnt marked for updated,
    #Make sure it gets updated anyways.
    if any(r[1]=='ignore' for r in records):
      if any(r[1]!='ignore' for r in records):
        self.logger.warning("Unexpected of mixture of JSON ignore/unignore'd in this payload! Proceed with ignore strategy")
      results = []
      for r in records:
        if r[0] not in results:
          if r[0] in [i[0] for i in currentRecords]:
            results.append(filter(lambda t: t[0]==r[0], currentRecords)[0])
          else:
            results.append(r)
      return results

    results = list(set([(r[0],r[1]) for r in records]).difference(currentRecords))

    self.logger.info('findChangedRecords: %s results' % len(results))
    return results
