#Settings for the rabbitMQ/ADSimportpipeline


#The %2F is expected by pika if we connect to vhost="/"
#backpressure_detection is currently broken in pika(stable), but fixed in master.
#Push expected in 0.9.14 release
#see https://github.com/pika/pika/issues/347
#RABBITMQ_URL = 'amqp://guest:guest@localhost:5672/%2F?backpressure_detection=t'
RABBITMQ_URL = 'amqp://admin:password@localhost:5672/%2F?socket_timeout=10&frame_max=512000' #Max message size = 500kb

PIDFILE = '/tmp/ADSimportpipeline.lock'
POLL_INTERVAL = 15 #how many seconds to poll each worker to make sure it is alive.

RABBITMQ_ROUTES = {
  'EXCHANGES':[
    {
      'exchange': 'MergerPipelineExchange',
      'exchange_type': 'direct',
      'passive': False,
      'durable': True,
    },
  ],
  'QUEUES':[
    {
      'queue': 'FindNewRecordsQueue',
      'durable': True,
    },
    {
      'queue': 'ReadRecordsQueue',
      'durable': True,
    },
    {
      'queue': 'UpdateRecordsQueue',
      'durable': True,
    },
    {
      'queue': 'MongoWriteQueue',
      'durable': True,
    },
  ],
  'BINDINGS':[
    {
      'queue':        'FindNewRecordsQueue',
      'exchange':     'MergerPipelineExchange',
      'routing_key':  'FindNewRecordsRoute',
    },
    {
      'queue':        'ReadRecordsQueue',
      'exchange':     'MergerPipelineExchange',
      'routing_key':  'ReadRecordsRoute',
    },
    {
      'queue':        'UpdateRecordsQueue',
      'exchange':     'MergerPipelineExchange',
      'routing_key':  'UpdateRecordsRoute',
    },
    {
      'queue':        'MongoWriteQueue',
      'exchange':     'MergerPipelineExchange',
      'routing_key':  'MongoWriteRoute',
    },  
  ],
}

WORKERS = {
  'FindNewRecordsWorker': { 
    'concurrency': 1,
    'publish': [
      {'exchange': 'MergerPipelineExchange', 'routing_key': 'ReadRecordsRoute',},
    ],
    'subscribe': [
      {'queue': 'FindNewRecordsQueue',},
    ],
  },

  'ReadRecordsWorker': { 
    'concurrency': 3,
    'publish': [
      {'exchange': 'MergerPipelineExchange', 'routing_key': 'UpdateRecordsRoute',},
    ],
    'subscribe': [
      {'queue': 'ReadRecordsQueue',},
    ],
  },

  'UpdateRecordsWorker': {
    'concurrency': 3,
    'publish': [
      {'exchange': 'MergerPipelineExchange','routing_key': 'MongoWriteRoute',},
    ],
    'subscribe': [
      {'queue': 'UpdateRecordsQueue',},
    ],
  },
  
  'MongoWriteWorker': {
    'concurrency': 1,
    'publish': [],
    'subscribe': [
      {'queue':'MongoWriteQueue',},
    ],
  },
}