from aip.libs import mongo_connection, update_records, read_records

mongo = mongo_connection.PipelineMongoConnection()

_strategies = {
      'ads.import-pipeline.find-new-records':mongo.findNewRecords, #expects [('bibcode','fingerprint'),...]
      'ads.import-pipeline.ingest-records':  mongo.formatRecordsforReingestion, #expects ['bibcode',...]
      'ads.import-pipeline.read-records':    read_records.readRecordsFromADSExports, #expects [('bibcode','fingerprint'),...]
      'ads.import-pipeline.update-record':   update_records.mergeRecords, #expects [{record}, ...]
      'MongoWriteWorker':       self.mongo.upsertRecords, #expects [{records}, ...]
      'SolrUpdateWorker':       SolrUpdater.solrUpdate, #expects ['bibcode', ...]
      'DeletionWorker':         SolrUpdater.delete_by_bibcodes, #expects ['bibcode',...]
    }


def handle(producer, message):
    
    if producer not in _strategies:
        raise Exception('We have no strategy to handle errors in: {producer}'.format(producer=producer))
    
    s = _strategies[producer]
    s(message)
    