from __future__ import absolute_import, unicode_literals
from aip import app as app_module
from aip.libs import solr_adapter, merger, read_records
from kombu import Queue
from adsmsg import BibRecord, DenormalizedRecord


app = app_module.ADSImportPipelineCelery('import-pipeline')
logger = app.logger


app.conf.CELERY_QUEUES = (
    Queue('delete-documents', app.exchange, routing_key='delete-documents'),
    Queue('find-new-records', app.exchange, routing_key='find-new-records'),
    Queue('read-records', app.exchange, routing_key='read-records'),
    Queue('merge-metadata', app.exchange, routing_key='merge-metadata'),
    Queue('output-results', app.exchange, routing_key='output-results'),
)


@app.task(queue='find-new-records')
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
    bpj = app.conf.get('BIBCODES_PER_JOB', 100)

    batch = []
    for r in results:
        found.add(r['bibcode'])
        if r['fingerprint'] != fingers[r['bibcode']]:
            batch.append((r['bibcode'], fingers[r['bibcode']]))
            if len(batch) >= bpj:
                logger.debug("Calling 'task_read_records' with '%s'", batch)
                task_read_records.delay(batch)
                batch = []
    if len(batch):
        logger.debug("Calling 'task_read_records' with '%s'", batch)
        task_read_records.delay(batch)
    
    # submit bibcodes that we don't have in the database
    to_do = list(set(fingers.keys()) - found)
    i = 0
    while i < len(to_do):
        batch = [(b, fingers[b]) for b in to_do[i:i+bpj]]
        logger.debug("Calling 'task_read_records' with '%s'", batch)
        task_read_records.delay(batch)
        i += bpj



@app.task(queue='read-records')
def task_read_records(fingerprints):
    """
    Read ADS records from disk; and inserts them into the queue that ingests them.

    @param bibcodes: [(bibcode, json_fingerprint),.....]
    """
    results = read_records.readRecordsFromADSExports(fingerprints)
    if results:
        for r in results:
            logger.debug("Calling 'task_merge_metadata' with '%s'", r)
            task_merge_metadata.delay(r)


@app.task(queue='merge-metadata')
def task_merge_metadata(record):
    """Receives the full metadata record (incl all the versions) as read by the ADS
    extractors. We'll merge the versions and create a close-to-canonical version of
    a metadata record."""

    logger.debug('About to merge data')
    result = merger.mergeRecords([record])
    logger.debug('Result of the merge: %s', result)

    if result and len(result) > 0:
        for r in result: # TODO: save the mid-cycle representation of the metadata ???
            record = app.update_storage(r['bibcode'], record['JSON_fingerprint'])
            r['id'] = record['id']
            r = solr_adapter.SolrAdapter.adapt(r)
            solr_adapter.SolrAdapter.validate(r)  # Raises AssertionError if not validated

            logger.debug("Calling 'task_output_results' with '%s'", r)
            task_output_results.delay(r)
    else:
        logger.debug('Strangely, the result of merge is empty: %s', record)


@app.task(queue='output-results')
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
    logger.debug('Will forward this record: %s', msg)
    rec = DenormalizedRecord(**msg)
    app.forward_message(rec)
    app.update_processed_timestamp(rec.bibcode)



@app.task(queue='delete-documents')
def task_delete_documents(bibcode):
    """Delete document from SOLR and from our storage.
    @param bibcode: string
    """
    logger.debug('To delete: %s', bibcode)
    app.delete_by_bibcode(bibcode)
    rec = DenormalizedRecord(bibcode=bibcode, status='deleted')
    app.forward_message(rec)



if __name__ == '__main__':
    app.start()
