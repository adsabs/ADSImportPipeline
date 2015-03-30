# Architecture


The [ADSimportpipeline](github.com/adsabs/ADSimportpipeline) is a set of tasks that:
  1. Finds records that either do not exist or need to be updated based on its JSON_fingerprint
  1. Reads data from ADSExports
  1. Coerces that data into a consistent JSON schema
  1. Merges any multiply defined metadata blocks based on a field specific curated set of rules
  1. Saves the resulting document into mongodb
  1. HTTP-POSTs the resulting document to a solr /update endpoint (after adapting the document into a solr schema)

The ADSimportpipeline makes heavy use of [rabbitmq](http://www.rabbitmq.com/) and the python rabbitmq driver [pika](https://pika.readthedocs.org). JSON is the message serialization format.

Several named queues are defined in `pipeline/psettings.py`, whose name references the type of work that will happen to message consumed from that queue:
  - FindNewRecordsQueue
  - ReadRecordsQueue
  - UpdateRecordsQueue
  - MongoWriteQueue
  - SolrUpdateQueue
  - ErrorHandlerQueue

Workers subscribe to a queue. When a message arrives in a queue, the cooresponding worker (consumer in rabbitmq terminology) executes some action on that message, and optionally publishes its results to one or more queues. Every message is atomic and every worker is independent, enabling the concurrent and asynchronous consumption of messages. Each worker has its own logfile in `logs/`.

# Individual queues/consumers

#### FindNewRecordsQueue
  - Expects: [["bibcode","fingerprint"],...]
  - Publishes: [["bibcode","fingerprint"],...]

Essentially removes elements from the input message to create the output, where the removes elements are those that already exist within the mongodb (including having the same fingerprint). More explicitly, it performs the following actions:

    [1] currentRecords = [(r['bibcode'],r['JSON_fingerprint']) for r in self.db[self.collection].find({"bibcode": {"$in": [rec[0] for rec in records]}})]
    [2] results = list(set([(r[0],r[1]) for r in records]).difference(currentRecords))

#### ReingestRecordsQueue
  - Expects ["bibcode",...]

Perpares the `[["bibcode","fingerprint],...]` payload necessary for the ReadRecordsQueue based on the bibcodes passed to it. The fingerprint passed will be its current fingerprint. Use this queue as a entrypoint to publish bibcodes that should be re-read, re-merged, re-saved to mongo, and reindexed to solr regardless of their fingerprint. Any bibcodes that do not already exist in the mongo database will be silently ignored.

#### ReadRecordsQueue
  - Expects: [["bibcode","fingerprint"],...]
  - Publishes: [{<full record>},...]

Calls `ADSCachedExports.ADSRecords` to compile the dataset for each bibcode. Coerces the XML ouput to a python dictionary, and further enforces the schema of this dictionary to that defined in `schema.json` using `lib/Enforcer.py`.



#### UpdateRecordsQueue
  - Expects: [{<full record>},...]
  - Publishes: [{<full record (merged)>},...]

Calls `lib/Merger.py` to merge any multiple defined metadatablocks. The field specific rules for merging are dispatched based on `settings.py`.



#### MongoWriteQueue
  - Expects: [{<full record (merged)>},...]
  - Publishes: ['bibcode',...]

Performs an upsert on mongodb for each record. Update will occur if the bibcode already exists in the database, OR if an alternate bibcode already exists. Since we use incrementing integer `_id` primary keys in mongo, and because we have to manage these ourselves, the concurrency of this consumer should be set to 1, at least until someone that understands write concerns and concurrent writes to mongo under this paradigm says otherwise.



#### SolrUpdateQueue
  - Expects: ['bibcode',...]
  - Publishes: (does not publish anything)
  
Compiles a complete solr document by querying mongo (including adsdata/docs) for each bibcode. Coerces the resulting output from mongo into a solr schema. Makes an HTTP-POST request to a solr endpoint with the list of solr documents.



#### ErrorHandlerQueue
 - Expects: Varied
 - Publishes: Varied

Each other consumer's functionality is wrapped in a blanket `try: ... except: Exception` clause, wherein the except statement publishes that payload (and the name of the consumer) to the ErrorHandlerQueue. The ErrorHandlerWorker recieves the message and iterates through each member of the payload. On each iteration, it performs the functionality of the worker that sent the payload (the mapping of worker->function is stored internally in `pipeline/workers.py`). If no exception is raised on the individual record, it is published "down the line" as a payload of length 1. Otherwise, the full traceback and bibcode will be logged.


# Usage and workflow

The pipeline connects to an instance of rabbitmq specified by `RABBITMQ_URL` in `pipeline/psettings.py`. All of routes, exchanges, queues, and bindings are defined in the same file, and are idempotently created on pipeline initialization (`pipeline/ADSimportpipeline.py start`). This main process also spawns each of the consumers defined in `pipeline/psettings.py`, `pipeline/workers.py`, and previously described in this document. `pipeline/ADSimportpipeline status` prints the current state of this master process, and `pipeline/ADSimportpipeline stop` kills it and its children.

Note that stopping and starting the pipeline at any time is perfectly safe: Messages are removed from the queue only after a worker has successfully processed it, each message is atomic, and each worker is independent. Workers are monitored for failures and restarted automatically, and also restarted in any case every 2 hours.

The script `run.py`, called with the `--async` flag publishes the initial set of [['bibcode','fingerprint'],...] messages to the FindNewRecordsQueue by reading the ads-classic bibcode files defined in `settings.py` and resolving their canonical bibcodes. There is hard-coded throttling based on how many messages are in the queue build in to this script, but very likely this is unnecessary: The queue RAM usage rarely exceeds 1GB, even with all 100K 100-bibcode messages stored.

The script `utils/publish_to_solr.py` will publish payloads directly to the SolrUpdateQueue, with several ways to specify bibcodes. This or `run.py` can be used as a template to write similar scripts that publish directly to a particular queue.
