import os,sys
import logging
import logging.handlers
from cloghandler import ConcurrentRotatingFileHandler
from collections import deque
from sqlalchemy import *
from sqlalchemy.dialects.postgresql import ARRAY

class PipelineSqlConnection:

    def __init__(self,**kwargs):
        self.logger = kwargs.get('logger',None)
        if not self.logger:
            self.initializeLogging(**kwargs)

        self.host = kwargs.get('HOST','localhost')
        self.port = kwargs.get('PORT','5432')
        self.database = kwargs.get('DATABASE',None)
        self.user = kwargs.get('USER','SpacemanSteve')
        self.password = kwargs.get('PASSWD',None)
        self.collection = kwargs.get('SCHEMA',None)
        self.schema = ''
        self.meta = MetaData()

        auth = ''
        if self.user and self.password:
            auth =  '%s@' % (':'.join([self.user,self.password]))
        self.uri = 'postgres://%s%s:%s/%s' % (auth,self.host,self.port,self.database)

        #self.engine = create_engine('postgresql://SpacemanSteve@localhost:5432/unittests_', echo=False)
        self.engine = create_engine(self.uri, echo=False)
        self.conn = self.engine.connect()

        # sql row view table
    def get_row_view_table(self, meta=None):
        if meta is None:
            meta = self.meta
        return Table('rowviewm', meta,
                     Column('bibcode', String, primary_key=True),
                     Column('id', Integer),
                     Column('authors', ARRAY(String)),
                     Column('refereed', Boolean),
                     Column('simbad_objects', ARRAY(String)),
                     Column('grants', ARRAY(String)),
                     Column('citations', ARRAY(String)),
                     Column('boost', Float),
                     Column('citation_count', Integer),
                     Column('read_count', Integer),
                     Column('norm_cites', Integer),
                     Column('readers', ARRAY(String)),
                     Column('downloads', ARRAY(Integer)),
                     Column('reads', ARRAY(Integer)),
                     Column('reference', ARRAY(String)),
                     #                 schema=self.schema,
                     extend_existing=True)


    def getAllBibcodes(self):
        return_value = deque()
        row_view = self.get_row_view_table()
        s = select([row_view])
        rp = self.conn.execute(s)
        rows = rp.fetchall()

        return rows

    def getRecordsFromBibcodes(self, bibcodes, key='bibcode', op='$in'):

        if not isinstance(bibcodes, list):
            bibcodes = [bibcodes]
        row_view = self.get_row_view_table()

        if op == '$in':
            s = select([row_view]).where(row_view.c[key].in_(bibcodes))
        elif op == '$nin':
            s = select([row_view]).where(row_view.c[key].notin_(bibcodes))
        else:
            raise ValueError('invalid op parameter {}, must be $in or $nin'.format(op))

        rp = self.conn.execute(s)
        rows = rp.fetchall()

        return rows



    #  def getRecordsFromBibcodes(self,bibcodes,key="bibcode",op="$in",query_limiter=None,iterate=False):
    #    if not iterate:
    #      # do we need to generate a sql statement or use core api
    #      # op can be in or nin, does sql support nin?  do we need it for sql?
    #      results = self.db[self.collection].find({key: {op: bibcodes}},query_limiter)
    #      return list(results)
    #    cur = self.db[self.collection].find({key: {op: bibcodes}},query_limiter)
    #    results = deque()
    #    while 1:
    #      try:
    #        results.append(cur.next())
    #      except StopIteration:
    #        return list(results)

    # not needed for read only sql data
    #def formatRecordsforReingestion(self,bibcodes):


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

    # no need to remove from sql database?
    #def remove(self,spec_or_id=None,force=False):

    # not needed for sql
    #def initializeCollection(self,_index='bibcode',**kwargs):

    # I don't think this will be needed
    #def _getNextSequence(self,name='seq'):
    #    #Todo: Implement a collection that records deleted docs, enabling us to re-use those _ids.
    #    result = self.db['%s_seq' % self.collection].find_and_modify(
    #        query={'_id':name},
    #        update={'$inc': {'counter':1}},
    #        new=True
    #    )
    #    return result['counter']

    # this is read only for sql data
    #def upsertRecords(self,records,**kwargs):

    # need to understand fingerprinting
    # if fingerprint is in unified mongo record and passed arguments, sql connection can ignore it
    #def findNewRecords(self,records):
