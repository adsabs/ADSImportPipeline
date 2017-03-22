from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery.utils.log import get_task_logger
from celery import Task
from aip import error_handler
from aip.libs import solr_updater, update_records, utils, read_records
import traceback
from kombu import Exchange, Queue



logger = get_task_logger('ADSimportpipeline')
conf = utils.load_config()
app = Celery('ADSimportpipeline',
             broker=conf.get('CELERY_BROKER', 'pyamqp://'),
             include=['aip.app'])


exch = Exchange(conf.get('CELERY_DEFAULT_EXCHANGE', 'import-pipeline'), type=conf.get('CELERY_DEFAULT_EXCHANGE_TYPE', 'topic'))

app.conf.CELERY_QUEUES = (
    Queue('errors', exch, routing_key='errors', durable=False, message_ttl=24*3600*5),
    Queue('delete-documents', exch, routing_key='delete-documents'),
    Queue('find-new-records', exch, routing_key='find-new-records'),
    Queue('merge-metadata', exch, routing_key='merge-metadata'),
    Queue('update-record', exch, routing_key='update-record'),
    Queue('update-solr', exch, routing_key='update-solr'),
)

app.conf.update(conf)

class MyTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error('{0!r} failed: {1!r}'.format(task_id, exc))


@app.task(base=MyTask, queue='foo')
def task_foo(a, b):
    print a, b, a+b
    return a+b
        

@app.task(base=MyTask, queue='delete-documents')
def task_delete_documents(bibcodes):
    """Delete documents from SOLR and from our storage.
    
    @param bibcodes: array of bibcodes 
    """
    for b in bibcodes:
        update_records.delete_by_bibcode(b)
    deleted, failed = solr_updater.delete_by_bibcodes(bibcodes, app.conf['SOLR_URLS'])
    task_handle_errors.delay('ads.import-pipeline.delete-documents', failed)


@app.task(base=MyTask, queue='errors')
def task_handle_errors(producer, message, redelivered=False):
    """
    @param producer: string, the name of the queue where the error originated
    @param body: 
    """
    
    if redelivered:
        logger.error("Fail: %s" % message)
        return
  
    #Iterate over each element of the batch, log and discard the failure(s)
    for content in message:
        try:
            logger.info('Trying to recover: %s' % producer)
            error_handler.handle(producer, content)
        except Exception, e:
            logger.error('%s: %s' % (content, traceback.format_exc()))
    


@app.task(base=MyTask, queue='find-new-records')
def task_find_new_records(fingerprints):
    """Finds bibcodes that are in need of updating. It will do so by comparing
    the json_fingerprint against the new record.
    
    @param fingerprints: [(bibcode, json_fingerprint),....]
    
    TODO: likely an obsolete method, to be removed/nuked/erased?
    """
    
    results = [] #_mongo.findNewRecords(fingerprints)
    if results:
        task_read_records.delay(results)
    

@app.task(base=MyTask, queue='read-records')
def task_read_records(message):
    """
    Read ADS records from disk; and inserts them into the queue that ingests them.
    
    @param bibcodes: [(bibcode, json_fingerprint),.....]
    """
    results = read_records.readRecordsFromADSExports(message)
    if results:
        for r in results:
            task_merge_metadata.delay(r)


@app.task(base=MyTask, queue='merge-metadata')
def task_merge_metadata(record):
    """Receives the full metadata record (incl all the versions) as read by the ADS 
    extractors. We'll merge the versions and create a close-to-canonical version of
    a metadata record."""
    
    result = update_records.mergeRecords([record])
    
    if result and len(result) > 0:
        for r in result: # TODO: save the mid-cycle representation of the metadata ???
            task_update_record.delay('metadata', r)


@app.task(base=MyTask, queue='update-record')
def task_update_record(type, payload):
    """Receives the canonical version of the metadata.
    
    @param record: JSON metadata
    """
    
    bibcode = payload['bibcode']
    
    # save into a database
    if type == 'metadata':
        task_update_solr.delay(bibcode, force=True)
    else:
        task_update_solr.delay(bibcode)


@app.task(base=MyTask, queue='update-solr')
def task_update_solr(bibcodes, force=False):
    #TODO: for every bibcode check if we have all parts
    # if yes, and the time window of last update was long enough
        # build the record and send it to solr
    # if not, register a delayed execution
    pass



if __name__ == '__main__':
    app.start()