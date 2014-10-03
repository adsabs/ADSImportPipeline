import os,sys
import time
import pika
import json
import logging
from logging import handlers
from cloghandler import ConcurrentRotatingFileHandler
import traceback

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
  def setup_logging(self,level=logging.DEBUG):
    logfmt = '%(levelname)s\t%(process)d [%(asctime)s]:\t%(message)s'
    datefmt= '%m/%d/%Y %H:%M:%S'
    self.formatter = logging.Formatter(fmt=logfmt,datefmt=datefmt)
    LOGGER = logging.getLogger(self.__class__.__name__)
    fn = os.path.join(os.path.dirname(__file__),'..','logs','%s.log' % self.__class__.__name__)   
    rfh = ConcurrentRotatingFileHandler(filename=fn,maxBytes=2097152,backupCount=5,mode='a') #2MB file
    rfh.setFormatter(self.formatter)
    LOGGER.handlers = []
    LOGGER.addHandler(rfh)
    LOGGER.setLevel(level)
    return LOGGER
  def connect(self,url,confirm_delivery=False):
    self.connection = pika.BlockingConnection(pika.URLParameters(url))
    self.channel = self.connection.channel()
    if confirm_delivery:
      self.channel.confirm_delivery()
    self.channel.basic_qos(prefetch_count=1)
  def publish_to_error_queue(self,message,exchange=None,routing_key=None,**kwargs):
    if not exchange:
      exchange = self.params['ERROR_HANDLER']['exchange']
    if not routing_key:
      routing_key = self.params['ERROR_HANDLER']['routing_key']
    self.channel.basic_publish(exchange,routing_key,message,**kwargs)
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


class ErrorHandlerWorker(RabbitMQWorker):
  def __init__(self,params):
    self.params=params
    from lib.MongoConnection import PipelineMongoConnection
    self.mongo = PipelineMongoConnection(**settings.MONGO)
    self.logger = self.setup_logging()
    self.logger.debug("Initialized")
    from lib.MongoConnection import PipelineMongoConnection
    from lib import ReadRecords #Hack to avoid loading ADSRecords until it is necessary
    from lib import UpdateRecords #Hack to avoid loading ADSRecords until it is necessary
    from lib.MongoConnection import PipelineMongoConnection
    from lib import SolrUpdater

    self.mongo=PipelineMongoConnection(**settings.MONGO)

    self.strategies = {
      'FindNewRecordsWorker':   self.mongo.findNewRecords, #expects [('bibcode','fingerprint'),...]
      'ReadRecordsWorker':      ReadRecords.readRecordsFromADSExports, #expects [('bibcode','fingerprint'),...]
      'UpdateRecordsWorker':    UpdateRecords.mergeRecords, #expects [{record}, ...]
      'MongoWriteWorker':       self.mongo.upsertRecords, #expects [{records}, ...]
      'SolrUpdateWorker':       SolrUpdater.solrUpdate, #expects ['bibcode', ...]
    }

  def on_message(self, channel, method_frame, header_frame, body):
    self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)
    return
    message = json.loads(body)
    producer = message.keys()[0]
    #Iterate over each element of the batch, log and discard the failure(s)
    for content in message[producer]:
      try:
        result = json.dumps(self.strategies[producer](content))
      except Exception, e:
        if producer in ['UpdateRecordsWorker','MongoWriteWorker']:
          content = content['bibcode']
        self.logger.error('%s: %s' % (content,traceback.format_exc()))
        continue
      #Re-publish the single record
      for e in self.params['WORKERS']['publish']:
        self.channel.basic_publish(e['exchange'],e['routing_key'],result)
    self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)


  def run(self):
    self.connect(self.params['RABBITMQ_URL'])
    self.subscribe(self.on_message)

class FindNewRecordsWorker(RabbitMQWorker):
  def __init__(self,params):
    self.params=params
    from lib.MongoConnection import PipelineMongoConnection
    self.mongo = PipelineMongoConnection(**settings.MONGO)
    self.f = self.mongo.findNewRecords
    self.logger = self.setup_logging()
    self.logger.debug("Initialized")
  def on_message(self, channel, method_frame, header_frame, body):
    message = json.loads(body)
    try:
      results = self.f(message)
      if results:
        self.publish(json.dumps(results,default=date_handler))
    except Exception, e:
      self.logger.warning("Offloading to ErrorWorker due to exception: %s" % e.message)
      self.publish_to_error_queue(json.dumps({self.__class__.__name__:message}))
    self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)
  def run(self):
    self.connect(self.params['RABBITMQ_URL'])
    self.subscribe(self.on_message)


class ReadRecordsWorker(RabbitMQWorker):
  def __init__(self,params):
    self.params=params
    from lib import ReadRecords #Hack to avoid loading ADSRecords until it is necessary
    self.f = ReadRecords.readRecordsFromADSExports
    self.logger = self.setup_logging()
    self.logger.debug("Initialized")
  def on_message(self, channel, method_frame, header_frame, body):
    message = json.loads(body)
    try:
      results = self.f(message)
      self.publish(json.dumps(results,default=date_handler))
    except Exception, e:
      self.logger.warning("Offloading to ErrorWorker due to exception: %s" % e.message)
      self.publish_to_error_queue(json.dumps({self.__class__.__name__:message}))
    self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)
  def run(self):
    self.connect(self.params['RABBITMQ_URL'])
    self.subscribe(self.on_message)


class UpdateRecordsWorker(RabbitMQWorker):
  def __init__(self,params):
    self.params=params
    from lib import UpdateRecords #Hack to avoid loading ADSRecords until it is necessary
    self.f = UpdateRecords.mergeRecords
    self.logger = self.setup_logging()
    self.logger.debug("Initialized")
  def on_message(self, channel, method_frame, header_frame, body):
    message = json.loads(body)
    try:
      results = self.f(message)
      self.publish(json.dumps(results,default=date_handler))
    except Exception, e:
      self.logger.warning("Offloading to ErrorWorker due to exception: %s" % e.message)
      self.publish_to_error_queue(json.dumps({self.__class__.__name__:message}))
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
    self.logger = self.setup_logging()
    self.logger.debug("Initialized")
  def on_message(self, channel, method_frame, header_frame, body):
    message = json.loads(body)
    try:
      results = self.f(message)
      self.publish(json.dumps(results,default=date_handler))
    except Exception, e:
      self.logger.warning("Offloading to ErrorWorker due to exception: %s" % e.message)
      self.publish_to_error_queue(json.dumps({self.__class__.__name__:message}))
    self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)
  def run(self):
    self.connect(self.params['RABBITMQ_URL'])
    self.subscribe(self.on_message)


class SolrUpdateWorker(RabbitMQWorker):
  def __init__(self,params):
    self.params=params
    from lib import SolrUpdater
    self.f = SolrUpdater.solrUpdate
    self.logger = self.setup_logging()
    self.logger.debug("Initialized")
  def on_message(self, channel, method_frame, header_frame, body):
    message = json.loads(body)
    try:
      self.f(message)
    except Exception, e:
      self.logger.error('%s: %s' % (e,traceback.format_exc()))
      #self.logger.warning("Offloading to ErrorWorker due to exception: %s" % e)
      #self.publish_to_error_queue(json.dumps({self.__class__.__name__:message}))
    self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)
  def run(self):
    self.connect(self.params['RABBITMQ_URL'])
    self.subscribe(self.on_message)
