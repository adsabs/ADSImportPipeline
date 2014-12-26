#Settings for the rabbitMQ/ADSimportpipeline


#The %2F is expected by pika if we connect to vhost="/"
#backpressure_detection is currently broken in pika(stable), but fixed in master.
#Push expected in 0.9.14 release
#see https://github.com/pika/pika/issues/347
#RABBITMQ_URL = 'amqp://guest:guest@localhost:5672/%2F?backpressure_detection=t'
RABBITMQ_URL = 'amqp://admin:password@localhost:5672/%2F?socket_timeout=10&backpressure_detection=t' #Max message size = 500kb

PIDFILE = '/tmp/ADSimportpipeline.lock'
POLL_INTERVAL = 15 #per-worker poll interval (to check health) in seconds.
ERROR_HANDLER = {
  'exchange': 'MergerPipelineExchange',
  'routing_key': 'ErrorHandlersRoute',
}

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
      'queue': 'ErrorHandlerQueue',
      'durable': True,
    },
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
    {
      'queue': 'SolrUpdateQueue',
      'durable': True,
    },
    {
      'queue': 'FindDeletedRecordsQueue',
      'durable': True,
    },
    {
      'queue': 'DeletionQueue',
      'durable': True,
    },     
  ],
  'BINDINGS':[
    {
      'queue':        'ErrorHandlerQueue',
      'exchange':     'MergerPipelineExchange',
      'routing_key':  'ErrorHandlersRoute',
    },
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
    {
      'queue':        'SolrUpdateQueue',
      'exchange':     'MergerPipelineExchange',
      'routing_key':  'SolrUpdateRoute',
    },
    {
      'queue':        'DeletionQueue',
      'exchange':     'MergerPipelineExchange',
      'routing_key':  'DeletionRoute',
    },    
  ],
}

WORKERS = {
  'ErrorHandlerWorker': { 
    'concurrency': 2,
    'publish': [
    ],
    'subscribe': [
      {'queue': 'ErrorHandlerQueue',},
    ],
  },

  'FindNewRecordsWorker': { 
    'concurrency': 5,
    'publish': [
      {'exchange': 'MergerPipelineExchange', 'routing_key': 'ReadRecordsRoute',},
    ],
    'subscribe': [
      {'queue': 'FindNewRecordsQueue',},
    ],
  },

  'ReadRecordsWorker': { 
    'concurrency': 4,
    'publish': [
      {'exchange': 'MergerPipelineExchange', 'routing_key': 'UpdateRecordsRoute',},
    ],
    'subscribe': [
      {'queue': 'ReadRecordsQueue',},
    ],
  },

  'UpdateRecordsWorker': {
    'concurrency': 2,
    'publish': [
      {'exchange': 'MergerPipelineExchange','routing_key': 'MongoWriteRoute',},
    ],
    'subscribe': [
      {'queue': 'UpdateRecordsQueue',},
    ],
  },
  
  'MongoWriteWorker': {
    'concurrency': 1,
    'publish': [
      {'exchange': 'MergerPipelineExchange','routing_key': 'SolrUpdateRoute',},
    ],
    'subscribe': [
      {'queue':'MongoWriteQueue',},
    ],
  },

  'SolrUpdateWorker': {
    'concurrency': 7,
    'publish': [],
    'subscribe': [
      {'queue':'SolrUpdateQueue',},
    ],
  }, 

  'DeletionWorker': {
    'concurrency': 1,
    'publish': [],
    'subscribe': [
      {'queue':'DeletionQueue',},
    ],
  }, 
}
