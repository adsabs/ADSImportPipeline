import os,sys
import pymongo
import logging
import logging.handlers

class PipelineMongoConnection:

  def __init__(self,**kwargs):
    self.logger = kwargs.get('logger',None)
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
    self.uri = 'mongodb://%s%s:%s' % (auth,self.host,self.port)

    self.conn = pymongo.MongoClient(host=self.uri)
    self.db = self.conn[self.database]

    if self.collection not in self.db.collection_names():
      self.initializeCollection()


  def initializeLogging(self,**kwargs):
    if self.logger:
      return
    logfmt = '%(levelname)s\t%(process)d [%(asctime)s]:\t%(message)s'
    datefmt= '%m/%d/%Y %H:%M:%S'
    formatter = logging.Formatter(fmt=logfmt,datefmt=datefmt)
    LOGGER = logging.getLogger(__file__)
    default_fn = os.path.join(os.path.dirname(__file__),'..','logs','%s.log' % self.__class__.__name__)   
    fn = kwargs.get('filename',default_fn)
    rfh = logging.handlers.RotatingFileHandler(filename=fn,maxBytes=2097152,backupCount=3,mode='a') #2MB file
    rfh.setFormatter(formatter)
    ch = logging.StreamHandler() #console handler
    ch.setFormatter(formatter)
    LOGGER.addHandler(ch)
    LOGGER.addHandler(rfh)
    LOGGER.setLevel(logging.DEBUG)
    self.logger = LOGGER

  def close(self):
    self.conn.close()

  def initializeCollection(self,_index='bibcode',**kwargs):
    self.logger.info('Initialize index %s for %s/%s' % (_index,self.database,self.collection))
    self.db[self.collection].ensure_index(_index,unique=True)

  def upsertRecords(self,records,querykey='bibcode',**kwargs):
    '''
    Upserts records(@type dict) to mongo
    '''
    if not records:
      self.logger.debug('upsertRecords: No records given')
    for r in records:
      #query = {"bibcode": {"$in": [r['bibcode'] for r in records]}}
      query = {querykey: r[querykey]}
      self.db[self.collection].update(query,r,upsert=True,w=kwargs.get('w',1),multi=kwargs.get('multi',False)) #w=1 means block all write requests until it has written to the primary

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
    results = list(set([(r[0],r[1]) for r in records]).difference(currentRecords))
    self.logger.info('findChangedRecords: %s results' % len(results))
    return results