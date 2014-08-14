import os,sys
import time
import pika
import json

sys.path.append(os.path.join(os.path.dirname(__file__),'..'))
import settings

def date_handler(item):
    return item.isoformat() if hasattr(item, 'isoformat') else item

class RabbitMQWorker:
  '''
  Base worker class. Defines the plumbing to communicate with rabbitMQ
  '''
  def __init__(self,params=None):
    self.params = params

  def connect(self,url,confirm_delivery=False):
    self.connection = pika.BlockingConnection(pika.URLParameters(url))
    self.channel = self.connection.channel()
    if confirm_delivery:
      self.channel.confirm_delivery()
    self.channel.basic_qos(prefetch_count=1)

  def publish(self,message,**kwargs):
    for e in self.params['publish']:
      self.channel.basic_publish(e['exchange'],e['routing_key'],message,**kwargs)

  def subscribe(self,callback,**kwargs):
    #Note that the same callback will be called for every entry in subscribe.
    for e in self.params['subscribe']:
      self.channel.basic_consume(callback,queue=e['queue'],**kwargs)
    self.channel.start_consuming()

  def stop(self):
    self.channel.close()
    self.connection.close()

  def declare_all(self,exchanges,queues,bindings):
    [self.channel.exchange_declare(**e) for e in exchanges]
    [self.channel.queue_declare(**q) for q in queues]
    [self.channel.queue_bind(**b) for b in bindings]

class FindNewRecordsWorker(RabbitMQWorker):
  def __init__(self,params):
    self.params=params
    from lib.MongoConnection import PipelineMongoConnection
    self.mongo = PipelineMongoConnection(**settings.MONGO)
    self.f = self.mongo.findNewRecords

  def on_message(self, channel, method_frame, header_frame, body):
    records = json.loads(body)
    result = self.f(records)
    if result:
      self.publish(json.dumps(result,default=date_handler))
    self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)

  def run(self):
    self.connect(self.params['RABBITMQ_URL'])
    self.subscribe(self.on_message)


class ReadRecordsWorker(RabbitMQWorker):
  def __init__(self,params):
    self.params=params
    from lib import ReadRecords #Hack to avoid loading ADSRecords until it is necessary
    self.f = ReadRecords.readRecordsFromADSExports

  def on_message(self, channel, method_frame, header_frame, body):
    try:
      records = self.f(json.loads(body))
    except ValueError:
      records = []
    self.publish(json.dumps(records,default=date_handler))
    self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)

  def run(self):
    self.connect(self.params['RABBITMQ_URL'])
    self.subscribe(self.on_message)


class UpdateRecordsWorker(RabbitMQWorker):
  def __init__(self,params):
    self.params=params
    from lib import UpdateRecords #Hack to avoid loading ADSRecords until it is necessary
    self.f = UpdateRecords.mergeRecords

  def on_message(self, channel, method_frame, header_frame, body):
    results = json.loads(body)
    self.publish(json.dumps(self.f(results),default=date_handler))
    self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)

  def run(self):
    self.connect(self.params['RABBITMQ_URL'])
    self.subscribe(self.on_message)


class MongoWriteWorker(RabbitMQWorker):
  def __init__(self,params):
    self.params=params
    from lib.MongoConnection import PipelineMongoConnection
    self.mongo = PipelineMongoConnection(**settings.MONGO)
    self.f = self.mongo.upsertRecords
  
  def on_message(self, channel, method_frame, header_frame, body):
    records = json.loads(body)
    results = self.f(records)
    self.publish(json.dumps(results,default=date_handler))
    self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)

  def run(self):
    self.connect(self.params['RABBITMQ_URL'])
    self.subscribe(self.on_message)

class SolrUpdateWorker(RabbitMQWorker):
  def __init__(self,params):
    self.params=params
    from lib import SolrUpdater
    self.f = SolrUpdater.solrUpdate
  
  def on_message(self, channel, method_frame, header_frame, body):
    records = json.loads(body)
    self.f(records)
    self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)

  def run(self):
    self.connect(self.params['RABBITMQ_URL'])
    self.subscribe(self.on_message)   