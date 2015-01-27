import os, sys
import pymongo
import pika
import json
import logging
from settings import (BIBCODE_FILES, MONGO, BIBCODES_PER_JOB)

import time
import mmap
from collections import OrderedDict, deque
from lib import xmltodict
from lib import MongoConnection
from lib import ReadRecords
from lib import UpdateRecords
from lib import SolrUpdater
from pipeline import psettings
from pipeline.workers import RabbitMQWorker

try:
  import argparse
except ImportError: #argparse not in python2.6, careful!
  from lib import argparse

logfmt = '%(levelname)s\t%(process)d [%(asctime)s]:\t%(message)s'
datefmt= '%m/%d/%Y %H:%M:%S'
formatter = logging.Formatter(fmt=logfmt,datefmt=datefmt)
LOGGER = logging.getLogger(__file__)
fn = os.path.join(os.path.dirname(__file__),'logs','%s.log' % 'run')   
rfh = logging.handlers.RotatingFileHandler(filename=fn,maxBytes=2097152,backupCount=3,mode='a') #2MB file
rfh.setFormatter(formatter)
ch = logging.StreamHandler() #console handler
ch.setFormatter(formatter)
LOGGER.addHandler(ch)
LOGGER.addHandler(rfh)
LOGGER.setLevel(logging.DEBUG)
logger = LOGGER

PROJECT_HOME = os.path.abspath(os.path.dirname(__file__))

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = newPath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def publish(w,records,sleep=5,max_queue_size=100000,url=psettings.RABBITMQ_URL,exchange='MergerPipelineExchange',routing_key='FindNewRecordsRoute'):

  #Treat FindNewRecordsQueue a bit differently, since it can consume messages at a much higher rate
  response = w.channel.queue_declare(queue='FindNewRecordsQueue', passive=True)
  while response.method.message_count >= max_queue_size:
    time.sleep(sleep)
    response = w.channel.queue_declare(queue='FindNewRecordsQueue', passive=True)


  #Hold onto the message if publishing it would cause the number of queued messages to exceed max_queue_size
  responses = [w.channel.queue_declare(queue=i,passive=True) for i in ['UpdateRecordsQueue','ReadRecordsQueue']]
  while any([r.method.message_count >= max_queue_size for r in responses]):
    time.sleep(sleep)
    responses = [w.channel.queue_declare(queue=i,passive=True) for i in ['UpdateRecordsQueue','ReadRecordsQueue']]
  
  payload = json.dumps(records)
  w.channel.basic_publish(exchange,routing_key,payload)


def readBibcodesFromFile(files):
  start = time.time()
  with cd(PROJECT_HOME):
    records = OrderedDict()
    for f in files:
      with open(f) as fp:
        logger.debug("...loading %s" % f)
        # Size 0 will read the ENTIRE file into memory!
        m = mmap.mmap(fp.fileno(), 0, prot=mmap.PROT_READ) #File is open read-only
        if m.size() < 1 or os.path.getsize(f) < 1:
          logger.error("%s is seemingly an empty file; Exit!")
          sys.exit(1)
        # note the file is already in memory
        line = 'init'
        while line:
          line = m.readline()
          if not line or line.startswith('#'):
            continue
          r = tuple(line.strip().split('\t'))
          if len(r) != 2:
            msg = "A bibcode entry should be \"bibcode<tab>JSON_fingerprint\". Skipping: %s" % r
            logger.warning(msg)
            continue
          if r[0] not in records:
            records[r[0]] = r[1]
        m.close()
  logger.info("Loaded data in %0.1f seconds" % (time.time()-start))
  return records


def main(MONGO=MONGO,*args):
  if args:
    sys.argv.extend(*args)

  parser = argparse.ArgumentParser()

  parser.add_argument(
    '--target-bibcodes',
    nargs='*',
    default=[],
    dest='targetBibcodes',
    help='Only analyze the specified bibcodes, and ignore their JSON fingerprints. Only works when --async=False. Use the syntax @filename.txt to read these from file (1 bibcode per file)'
    )

  parser.add_argument(
    '--async',
    default=False,
    action='store_true',
    dest='async',
    help='start in async mode'
    )

  parser.add_argument(
    '--dont-init-lookers-cache',
    default=False,
    action='store_true',
    dest='dont_init_lookers_cache',
    help='dont call ADSExports2.init_lookers_cache()'
    )

  parser.add_argument(
    '--load-records-from-pickle',
    nargs='*',
    default=None,
    dest='load_records_from_pickle',
    help='Load XML records from a pickle instead of ADSExports',
    )

  parser.add_argument(
    '--dump-output-to-file',
    nargs=1,
    type=str,
    default=None,
    dest='outfile',
    help='Output records to a file'
    )

  parser.add_argument(
    '--ignore-json-fingerprints',
    default=False,
    action='store_true',
    dest='ignore_json_fingerprints',
    help='ignore json fingerprints when finding new records to update (ie, force update)',
    )

  parser.add_argument(
    '--process-deletions',
    default=False,
    action='store_true',
    dest='process_deletions',
    help='Find orphaned bibcodes in the mongodb, then send these bibcodes to delete via rabbitMQ. No updates will be processed with this flag is set.',
    )

  args = parser.parse_args()

  if not args.dont_init_lookers_cache:
    start = time.time()
    logger.info("Calling init_lookers_cache()")
    ReadRecords.INIT_LOOKERS_CACHE()
    logger.info("init_lookers_cache() returned in %0.1f sec" % (time.time()-start))

  records = readBibcodesFromFile(BIBCODE_FILES)
  targets = None
  if args.targetBibcodes and args.targetBibcodes[0].startswith('@'):
    with open(args.targetBibcodes[0].replace('@','')) as fp:
      targetBibcodes = deque([L.strip() for L in fp.readlines() if L and not L.startswith('#')])
    targets = {bibcode:records[bibcode] for bibcode in args.targetBibcodes}
  
  records = deque(ReadRecords.canonicalize_records(records,targets))
  total = float(len(records)) #Save to print later

  if args.ignore_json_fingerprints:
    records = deque([(r[0],'ignore') for r in records])

  if args.process_deletions:
    start = time.time()
    logger.info("Processing deletions. This will block for several hours until the database is compared, then exit.")
    logger.warning("No updates will be processed when --process-deletions is set")
    mongo = MongoConnection.PipelineMongoConnection(**MONGO)
    mongo.close()
    results = mongo.getAllBibcodes()
    if len(results) != mongo.db[mongo.collection].count():
      logger.warning("len getAllBibcodes (%s) != len count (%s). Continue anyways." % (len(results),mongo.db[mongo.collection].count()))
    records = [i[0] for i in records]
    payload = list(set(results).difference(set(records)))
    w = RabbitMQWorker()   
    w.connect(psettings.RABBITMQ_URL)
    publish(w,payload,routing_key='DeletionRoute')
    logger.info("Found %s orphaned bibcodes in %0.1f seconds." % (len(payload),time.time()-start))
    sys.exit(0)


  if not args.async:
    mongo = MongoConnection.PipelineMongoConnection(**MONGO)
    records = mongo.findNewRecords(records)
    if args.load_records_from_pickle:
      records = ReadRecords.readRecordsFromPickles(records,args.load_records_from_pickle)
    else:
      records = ReadRecords.readRecordsFromADSExports(records)
    merged = UpdateRecords.mergeRecords(records)
    if args.outfile:
      with open(args.outfile[0],'w') as fp:
        r = {'merged': merged, 'nonmerged': records}
        json.dump(r,fp,indent=1)
    else:
      bibcodes = mongo.upsertRecords(merged)
      #SolrUpdater.solrUpdate(bibcodes)
  elif args.async:
    w = RabbitMQWorker()   
    w.connect(psettings.RABBITMQ_URL)
    lastLogged = None
    while records:
      payload = []
      while len(payload) < BIBCODES_PER_JOB:
        try:
          payload.append( records.popleft() )
        except IndexError:
          break
      percent = round((1-len(records)/total)*100.0)
      if not percent % 5 and percent!=lastLogged:
        lastLogged=percent
        logger.info("There are %s records left (%0.1f%% completed)" % (len(records),percent))
      publish(w,payload)

    
if __name__ == '__main__':
  try:
    main()
  except SystemExit:
    pass #this exception is raised by argparse if -h or wrong args given; we will ignore.
  except:
    raise
