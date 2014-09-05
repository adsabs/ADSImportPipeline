import os, sys
import pymongo
import pika
import json
import logging
from settings import (BIBCODE_FILES, MONGO, BIBCODES_PER_JOB)

import time
import mmap
from collections import OrderedDict
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

def publish(records,max_queue_size=30,url=psettings.RABBITMQ_URL,exchange='MergerPipelineExchange',routing_key='FindNewRecordsRoute'):
  #Its ok that we create/tear down this connection many times within this script; it is not a bottleneck
  #and likely slightly increases stability of the workflow

  w = RabbitMQWorker()
  w.connect(psettings.RABBITMQ_URL)

  #Hold onto the message if publishing it would cause the number of queued messages to exceed max_queue_size
  responses = [w.channel.queue_declare(queue=i,passive=True) for i in ['UpdateRecordsQueue','ReadRecordsQueue']]
  while any([r.method.message_count >= max_queue_size for r in responses]):
    time.sleep(15)
    responses = [w.channel.queue_declare(queue=i,passive=True) for i in ['UpdateRecordsQueue','ReadRecordsQueue']]
  
  payload = json.dumps(records)
  w.channel.basic_publish(exchange,routing_key,payload)
  w.connection.close()


def readBibcodesFromFile(files,targets):
  start = time.time()
  with cd(PROJECT_HOME):
    records = OrderedDict()
    for f in files:
      with open(f) as fp:
        logger.debug("...loading %s" % f)
        # Size 0 will read the ENTIRE file into memory!
        m = mmap.mmap(fp.fileno(), 0, prot=mmap.PROT_READ) #File is open read-only

        # note the file is already in memory
        line = m.readline()
        while line:
          if line.startswith('#'):
            continue
 
          r = tuple(line.strip().split('\t'))
          if len(r) != 2:
            msg = "A bibcode entry should be \"bibcode<tab>JSON_fingerprint\". Skipping: %s" % r
            logger.warning(msg)
            continue
          if r[0] not in records:
            records[r[0]] = r[1]
          line = m.readline()
        m.close()
  logger.info("Loaded data in %0.1f seconds" % (time.time()-start))
  return ReadRecords.canonicalize_records(records,targets)


def main(MONGO=MONGO,*args):
  if args:
    sys.argv.extend(*args)

  parser = argparse.ArgumentParser()

  parser.add_argument(
    '--bibcode-files',
    nargs='*',
    default=BIBCODE_FILES,
    dest='updateTargets',
    help='full paths to bibcode files'
    )

  parser.add_argument(
    '--target-bibcodes',
    nargs='*',
    default=[],
    dest='targetBibcodes',
    help='Only analyze the specified bibcodes'
    )

  parser.add_argument(
    '--async',
    default=False,
    action='store_true',
    dest='async',
    help='start in async mode'
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

  args = parser.parse_args()

  records = readBibcodesFromFile(args.updateTargets, args.targetBibcodes)

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
    while records:
      payload = []
      while len(payload) < BIBCODES_PER_JOB:
        try:
          payload.append( records.pop(0) )
        except IndexError:
          break
      publish(payload)

    
if __name__ == '__main__':
  try:
    main()
  except SystemExit:
    pass #this exception is raised by argparse if -h or wrong args given; we will ignore.
  except:
    raise
