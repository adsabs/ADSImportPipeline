import sys, os
PROJECT_HOME = os.path.abspath(os.path.join(os.path.dirname(__file__),'../'))
sys.path.append(PROJECT_HOME)

import argparse
import json
import time

from pipeline import psettings
from pipeline.workers import RabbitMQWorker

def publish(bibcodes,url=psettings.RABBITMQ_URL,exchange='MergerPipelineExchange',routing_key='SolrUpdateRoute'):
  w = RabbitMQWorker()
  w.connect(psettings.RABBITMQ_URL)
  
  payload = json.dumps(bibcodes)
  w.channel.basic_publish(exchange,routing_key,payload)
  w.connection.close()

def getAllBibcodesFromMongo():
  from lib import MongoConnection
  from settings import MONGO

  m = MongoConnection.PipelineMongoConnection(**MONGO)
  return m.db[m.collection].find({},{'bibcode':1,'_id':0})


def main():
  parser = argparse.ArgumentParser()

  parser.add_argument(
    'bibcodes',
    nargs='*',
    help='bibcodes to publish'
  )

  parser.add_argument(
    '--from-file',
    nargs=1,
    default=None,
    dest='bibcode_file',
    type=str,
    help='Load bibcodes from file, one bibcode per line'
  )

  parser.add_argument(
    '--whole-database',
    default=False,
    dest='whole_database',
    action='store_true',
  )

  parser.add_argument(
    '--bibcodes-per-message',
    nargs=1,
    default=100,
    dest='bibcodes_per_message',
    type=int,
    help='Publish N bibcodes at a time'
  )

  args = parser.parse_args()
  if args.whole_database:
    bibcodes = getAllBibcodesFromMongo()
    bibcodes.batch_size(100)
    print "the cursor has returned",type(bibcodes)
    bibcodes.pop = bibcodes.next

  if args.bibcode_file:
    with open(args.bibcode_file) as fp:
      bibcodes = [L.strip() for L in fp.readlines() if L and not L.startswith('#')]
  else:
    if not args.bibcodes and not args.whole_database:
      raise Exception("Not enough arguments given")
    if not args.whole_database:
      bibcodes = [i for i in args.bibcodes]

  while bibcodes:
    payload = []
    while len(payload) < args.bibcodes_per_message:
      try:
        b = bibcodes.pop()
        if isinstance(b,dict):
          b = b['bibcode']
        payload.append(b)
      except (IndexError, StopIteration):
        break
    publish(payload)




if __name__ == '__main__':
  main()

