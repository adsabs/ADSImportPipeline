import os, sys
import pymongo
import pika
import json
from settings import (CLASSIC_BIBCODES, ARXIV2PUB, MONGO, LOGGER, BIBCODES_PER_JOB)

import time
from lib import xmltodict
from lib import utils
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

def publish(records,url=psettings.RABBITMQ_URL,exchange='MergerPipelineExchange',routing_key='FindNewRecordsRoute'):
  #Its ok that we create/tear down this connection many times within this script; it is not a bottleneck
  #and likely slightly increases stability of the workflow
  w = RabbitMQWorker()
  w.connect(psettings.RABBITMQ_URL)
  w.channel.basic_publish('MergerPipelineExchange','FindNewRecordsRoute',json.dumps(records))
  w.connection.close()


def main(LOGGER=LOGGER,MONGO=MONGO,*args):
  PROJECT_HOME = os.path.abspath(os.path.dirname(__file__))
  start = time.time()
  LOGGER.debug('--Start--') 
  if args:
    sys.argv.extend(*args)

  parser = argparse.ArgumentParser()

  parser.add_argument(
    '--classic-databases',
    nargs='*',
    default=CLASSIC_BIBCODES.keys(),
    dest='updateTargets',
    help='Which datasources should be updated'
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

  args = parser.parse_args()
  LOGGER.debug('Recieved args (%s)' % (args))
  for target in args.updateTargets:
    targetRecords = []
    LOGGER.info('Working on bibcodes in %s' % target)
    
    s = time.time() #Let's eventually use statsd for these timers :)
    with cd(PROJECT_HOME):
      with open(CLASSIC_BIBCODES[target]) as fp:
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


    LOGGER.debug('[%s] Read took %0.1fs' % (target,(time.time()-s)))
    #Publish any leftovers in case the total was not evenly divisibly
    if args.async:
      if records:
        publish(records)
    else:
      s = time.time()
      records = utils.findChangedRecords(records,LOGGER,MONGO)
      LOGGER.info('[%s] Found %s records to be updated in %0.1fs' % (target,len(records),(time.time()-s)))

      s = time.time()
      records = utils.updateRecords(records,LOGGER)
      LOGGER.info('[%s] Updating %s records took %0.1fs' % (target,len(records),(time.time()-s)))

      s = time.time()
      utils.mongoCommit(records,LOGGER,MONGO)
      LOGGER.info('Wrote %s records to mongo in %0.1fs' % (len(records),(time.time()-s)))
      
      LOGGER.debug('--End-- (%0.1fs)' % (time.time()-start))

if __name__ == '__main__':
  try:
    main()
  except SystemExit:
    pass #this exception is raised by argparse if -h or wrong args given; we will ignore.
  except:
    LOGGER.exception('Traceback:')
    raise