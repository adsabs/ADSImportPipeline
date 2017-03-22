from aip.libs import update_records, read_records, solr_updater


_strategies = {
      'ads.import-pipeline.find-new-records': None, #mongo.findNewRecords, #expects [('bibcode','fingerprint'),...]
      'ads.import-pipeline.ingest-records':  None, #mongo.formatRecordsforReingestion, #expects ['bibcode',...]
      'ads.import-pipeline.read-records':    read_records.readRecordsFromADSExports, #expects [('bibcode','fingerprint'),...]
      'ads.import-pipeline.update-record':   update_records.mergeRecords, #expects [{record}, ...]
      'MongoWriteWorker':       None, #self.mongo.upsertRecords, #expects [{records}, ...]
      'SolrUpdateWorker':       solr_updater.solrUpdate, #expects ['bibcode', ...]
      'DeletionWorker':         solr_updater.delete_by_bibcodes, #expects ['bibcode',...]
    }


def handle(producer, message):
    
    if producer not in _strategies:
        raise Exception('We have no strategy to handle errors in: {producer}'.format(producer=producer))
    
    s = _strategies[producer]
    s(message)
    