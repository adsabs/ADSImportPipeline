import os, sys
import pymongo
import pika
import json
from settings import (CLASSIC_BIBCODES, MONGO, BIBCODES_PER_JOB)

import time
from lib import xmltodict
from lib import MongoConnection
from lib import ReadRecords
from lib import UpdateRecords
from pipeline import psettings
from pipeline.workers import RabbitMQWorker

try:
  import argparse
except ImportError: #argparse not in python2.6, careful!
  from lib import argparse

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
  w.channel.basic_publish('MergerPipelineExchange','FindNewRecordsRoute',payload)
  w.connection.close()


def main(MONGO=MONGO,*args):
  PROJECT_HOME = os.path.abspath(os.path.dirname(__file__))
  if args:
    sys.argv.extend(*args)

  parser = argparse.ArgumentParser()

  parser.add_argument(
    '--bibcode-files',
    nargs='*',
    default=CLASSIC_BIBCODES.values(),
    dest='updateTargets',
    help='full paths to bibcode files'
    )

  parser.add_argument(
    '--bibcodes',
    nargs='*',
    default=None,
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
    '--load-records-from-files',
    nargs='*',
    default=None,
    dest='load_from_files',
    help='Load XML records from files via pickle instead of ADSExports',
    )

  args = parser.parse_args()
  for target in args.updateTargets:
    targetRecords = []
    
    with cd(PROJECT_HOME):
      with open(target) as fp:
        records = []
        for line in fp:
          if not line or line.startswith("#"):
            continue
          r = tuple(line.strip().split('\t'))
          if args.targetBibcodes:
            if r[0] in args.targetBibcodes:
              records.append(r)
          else:
            records.append(r)
          if args.async and len(records) >= BIBCODES_PER_JOB:
            #We will miss the last batch of records unless it the total is evenly divisible by BIBCODES_PER_JOB
            publish(records)
            records = []
            #TODO: Throttling?

    #Publish any leftovers in case the total was not evenly divisibly
    if args.async:
      if records:
        publish(records)
    else:
      mongo = MongoConnection.PipelineMongoConnection(**MONGO)
      records = mongo.findNewRecords(records)

      if args.load_from_files:
        records = ReadRecords.readRecordsFromPickles(records,args.load_from_files)
      else:
        records = ReadRecords.readRecordsFromADSExports(records)

      records = UpdateRecords.mergeRecords(records)
      mongo.upsertRecords(records)
      
if __name__ == '__main__':
  try:
    main()
  except SystemExit:
    pass #this exception is raised by argparse if -h or wrong args given; we will ignore.
  except:
    raise
