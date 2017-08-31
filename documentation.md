# Description

This is a transformation pipeline. It receives bibcodes, metadata, nonbib data, fulltext, orcid claims and other
information associated to a *bibcode*. The service will construct a SOLR document and push the final version to
SOLR.

## Diagram




```

                                                                            +---------------+
                                                                            |               |
                                                                     +------+ find-new-records
                                                                     |      |               |
                                                                     |      +---------------+
                                                                     |             ^
                                                                     |             |
                          +-------------> +--------------+           |             |
                          |               |              | <---------+             +
                          | +-------------+  read-records|                      broker
                          | |             |              |                         +
                          | |             +--------------+                         |
                          | |                    |                                 |
                          | |             +--------------+                         v
                          | |  +--------> |              |
                          | |  | +--------+  merge-metadata                 +--------------+
                          | |  | |        |              |                  |              |
                          | v  | v        +--------------+                  | delete-documents
                          |    |                 |                          |              |
           Inputs       +----------+      +--------------+                  +--------------+
                        |          +----> |              |                    |
         +-------->     |  Broker  |      | update-record| <------------------+
                        |          | <----+              |
                        +----------+      +--------------+
                           |     |               |
                           |  ^  |        +--------------+            Outputs
                           |  |  +----->  |              |
                           |  +-----------+ update-solr  +------------------------->
                           |              |              |
                           |              +--------------+
                           v

                          +---------------+
                          |               |
                          |   errors      |
                          |               |
                          +---------------+
```


## Explanation

Described above are the queues. Celery workers will attach to the queue.

 - Inputs: data arriving from external sources (other pipelines) must be sent to the proper rabbitmq vhost/exchnage/key
 
    example: adsfulltext will send its data to rabbitmq running on adsqb; into the virtual host `import-pipeline` and exchange called 'import-pipeline'; the routing key will be 'update-record'
    
 - read-records: the worker in this queue receives list of bibcodes; it will use ADSRecord module to read ADS Classic
     metadata (off a disk; therefore the worker must run on ADS server with access to /proj/ads/soft). Results of the
     read will be forwarded to the queue *merge-metadata*
     
 - merge-metadata: receives all versions of bibliographic metadata and merges them into one *canonical* representation; it will also enforce schema. Forwards results to *update-record*
 
 - update-record: this worker receives several types of inputs and *stores* them into a postgres database. The worker
    will record the type of the input and also updates the timestamp of when this piece of information arrived. The 
    types are:
    
    - metadata: bibliographic metadata
    - orcid_claims: claims received from ADSOrcid pipeline
    - fulltext: results from ADSfulltext pipeline
    - nonbib_data: results from ADSData pipeline (reads, citations)
    
    The worker will decide (based on the type of the received data and the completeness of the record)
    whether it triggers a solr update, or whether it is better to wait - it will register a callback
    with a certain delay.
    
 - update-sorl: the worker in this queue receives bibcodes; it will reach to the database - build a final version of 
    the SOLR document; verify it and push it to the SOLR servers for indexing.
    
    
 - find-new-records: this queue is populated by an external process. This process (a script?) runs on the ADS servers
    monitors the updates to ADS Classic. It will publish (bibcode, json_fingerprint) tuples into this queue. The worker
    in this queue will compare the fingerprints with the existing versions (in our postgres database) and will trigger
    updates to metadata if the fingerprints differ.
    
 - delete-documents: again an external process that monitors ADS Classic publishes list of bibcodes to this queue. The
    worker in this queue will remove the records from the database and from SOLR.
    
 - errors: this worker will receive messages from all the other queues. It will try to recover (for example by repushing
    a claim into the update-record queue). There are different strategies implemented inside the worker.


## Invocation

The workflow is initiated by invoking `run.py`.
    
It has various options but basically it will (brute force) comparison of ADS Classic against the
current database state. It will read off all ADS Classic bibcodes, discover orphaned records (and
submit them for deletion) - and then it will submit everything else into the `find-new-records`
queue. There the workers take over.    

 

## Requirements
    - celery
    - rabbitmq
    - ADSExports (and access to the /proj/ads... files)
    - sqlalchemy (+ postgres)
    - Note: The rabbitmq server should be configured for frame_max=512000

## Update store

To force an update of a list of bibcodes use the following:
```
python run.py --ignore-json-fingerprints --bibcodes @reindex/reingest_20161122.txt
```

## Updating Solr
It is possible for Solr to be missing data on some bibcodes.  When
this happens, use ADSimportpipeline to add the missing bibcodes.  
First, to obtain a list of bibcodes known to Solr use:
```
curl 
http://solrInstance:8983/solr/collection1/select?q=*:*&rows=20000000&fl=bibcode&wt=csv
> solrBibcodes.txt
```

The canonical list of bibcodes is available as a column/flat file (sorted case-insensitively)
from the ingest pipeline.  Comparing these two files requires sorting the new file
and then using unix's join command:

```
sort -f solrBibcodes.txt | join -i bibcodes.list.can - > notInSolr_20161122.txt
```

This creates a file with bibcodes that were in canonical but not
solr.  This list can be injected into the pipeline with:
```
python/bin/python2.7 utils/publish_bibcodes_to_solr.py --from-file reindex/notInSolr_20161122.txt
```
  