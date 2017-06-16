from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery.utils.log import get_task_logger
from celery import Task
from aip import app as app_module
from aip.libs import solr_adapter, merger, read_records
import adsputils as utils
from kombu import Exchange, Queue, BrokerConnection



app = app_module.create_app()
logger = utils.setup_logging('import-pipeline', 
                             level=app.conf.get('LOGGING_LEVEL', 'INFO'))


exch = Exchange(app.conf.get('CELERY_DEFAULT_EXCHANGE', 'import-pipeline'), 
                type=app.conf.get('CELERY_DEFAULT_EXCHANGE_TYPE', 'topic'))

app.conf.CELERY_QUEUES = (
    Queue('errors', exch, routing_key='errors', durable=False, message_ttl=24*3600*5),
    Queue('delete-documents', exch, routing_key='delete-documents'),
    Queue('find-new-records', exch, routing_key='find-new-records'),
    Queue('read-records', exch, routing_key='read-records'),
    Queue('merge-metadata', exch, routing_key='merge-metadata'),
    Queue('output-results', exch, routing_key='output-results'),
)

forwarding_connection = BrokerConnection(app.conf.get('OUTPUT_CELERY_BROKER',
                              '%s/%s' % (app.conf.get('CELERY_BROKER', 'pyamqp://'),
                                         app.conf.get('OUTPUT_EXCHANGE', 'master-pipeline'))))


class MyTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # TODO; finish the handling
        logger.error('{0!r} failed: {1!r}'.format(task_id, exc))



@app.task(base=MyTask, queue='find-new-records')
def task_find_new_records(fingerprints):
    """Finds bibcodes that are in need of updating. It will do so by comparing
    the json_fingerprint against existing db record.
    
    Inputs to this task are submitted by the run.py process; which reads/submits
    contents of the BIBFILES
    
    @param fingerprints: [(bibcode, json_fingerprint),....]
    """
    fingers = {}
    for k, v in fingerprints:
        fingers[k] = v
        
    bibcodes = [x[0] for x in fingerprints]
    results = app.get_record(bibcodes, load_only=['bibcode', 'fingerprint'])
    found = set()
    for r in results:
        found.add(r['bibcode'])
        if r['fingerprint'] != fingers[r['bibcode']]:
            task_read_records.delay([(r['bibcode'], fingers[r['bibcode']])])
    # submit bibcodes that we don't have in the database
    for b in set(fingers.keys()) - found:
        task_read_records.delay((b, fingers[b]))



@app.task(base=MyTask, queue='read-records')
def task_read_records(fingerprints):
    """
    Read ADS records from disk; and inserts them into the queue that ingests them.
    
    @param bibcodes: [(bibcode, json_fingerprint),.....]
    """
    results = read_records.readRecordsFromADSExports(fingerprints)
    if results:
        for r in results:
            task_merge_metadata.delay(r)


@app.task(base=MyTask, queue='merge-metadata')
def task_merge_metadata(record):
    """Receives the full metadata record (incl all the versions) as read by the ADS 
    extractors. We'll merge the versions and create a close-to-canonical version of
    a metadata record."""
    
    logger.debug('About to merge data')
    result = merger.mergeRecords([record])
    
    if result and len(result) > 0:
        for r in result: # TODO: save the mid-cycle representation of the metadata ???
            record = app.update_storage(r['bibcode'], record['JSON_fingerprint'])
            r['id'] = record['id']
            r = solr_adapter.SolrAdapter.adapt(r)
            solr_adapter.SolrAdapter.validate(r)  # Raises AssertionError if not validated
            
            task_output_results.delay(r)
    else:
        logger.debug('Strangely, the result of merge is empty: %s', record)


@app.task(base=MyTask, queue='output-results')
def task_output_results(msg):
    """
    This worker will forward results to the outside 
    exchange (typically an ADSMasterPipeline) to be
    incorporated into the storage
    
    :param msg: contains the bibliographic metadata
            
            {'bibcode': '....',
             'authors': [....],
             'title': '.....',
             .....
            }
    :return: no return
    """
    logger.debug('Forwarding results out %s', forwarding_connection)
    _forward_message.apply_async(
        (msg), 
        connection=forwarding_connection)
    app.update_processed_timestamp(msg['bibcode'])


@app.task(base=MyTask, name=app.conf.get('OUTPUT_TASKNAME', 'ads.import.pipeline.worker'), 
                     exchange=app.conf.get('OUTPUT_EXCHANGE', 'import_pipeline'),
                     queue=app.conf.get('OUTPUT_QUEUE', 'update-record'),
                     routing_key=app.conf.get('OUTPUT_QUEUE', 'update-record'))
def _forward_message(msg):
    """A handler that can be used to forward stuff out of our
    queue. It does nothing (it doesn't process data)"""
    logger.error('We should have never been called directly! %s' % (repr((bibcode, key, msg)))) 






if __name__ == '__main__':
    app.start()