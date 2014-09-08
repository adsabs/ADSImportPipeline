import sys, os
PROJECT_HOME = os.path.abspath(os.path.join(os.path.dirname(__file__),'../'))
sys.path.append(PROJECT_HOME)

import argparse
import json

from pipeline import psettings
from pipeline.workers import RabbitMQWorker

def publish(bibcodes,url=psettings.RABBITMQ_URL,exchange='MergerPipelineExchange',routing_key='SolrUpdateRoute'):
  w = RabbitMQWorker()
  w.connect(psettings.RABBITMQ_URL)
  
  payload = json.dumps(bibcodes)
  w.channel.basic_publish(exchange,routing_key,payload)
  w.connection.close()

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
    '--bibcodes-per-message',
    nargs=1,
    default=30,
    dest='bibcodes_per_message',
    type=int,
    help='Publish N bibcodes at a time'
    )

  args = parser.parse_args()
  
  if args.bibcode_file:
    with open(args.bibcode_file) as fp:
      bibcodes = [L.strip() for L in fp.readlines() if L and not L.startswith('#')]
  else:
    if not args.bibcodes:
      raise Exception("Not enough arguments given")
    bibcodes = args.bibcodes
  
  while bibcodes:
    payload = []
    while payload < args.bibcodes_per_message:
      try:
        payload.append( bibcodes.pop(0) )
      except IndexError:
        break
    publish(payload)




if __name__ == '__main__':
  main()