# ADSimportpipeline

[![Build Status](https://travis-ci.org/adsabs/ADSimportpipeline.svg?branch=master)](https://travis-ci.org/adsabs/ADSimportpipeline)
[![Coverage Status](https://coveralls.io/repos/adsabs/ADSimportpipeline/badge.svg?branch=master)](https://coveralls.io/r/adsabs/ADSimportpipeline)

## Overview

Coordinates ingest of a full ADS record. The workflow is as follows.

1. Read bibcodes from file
1. Query mongo for changed records. A changed record is one whose `record.JSON_fingerprint` is different than that parsed from disk
1. Call ads.ADSExports.ADSRecords to consolidate each record's data (ADS-classic)
1. Parses resulting xmlobject to a native python structure via `xmltodict.py`
1. Enforces a set schema that is documented in `schema.json`
1. Merges any repeated metadata blocks
1. Insert/update record in mongodb. Insert if it is new, update if that bibcode or one of its alternate bibcodes exists.

The workflow is initiated by invoking `run.py`. 

## Async workflow with rabbitMQ

- Invoking `run.py --async` publishes the `[(bibcode, fingerprint),...]` records to rabbitmq. 
- Workers that consume these messages are defined in `pipeline/psettings.py` and `pipeline/workers.py`.
- Workers are controlled via a master process in `pipeline/ADSimportpipeliny.py`.
- Workers perform their tasks independently and (optionally) concurrently.
- Workers expect and return JSON.
 

## Requirements
- pika
- rabbitmq
- ADSExports
- pymongo + mongo
- Note: The rabbitmq server should be configured for frame_max=512000
- Note: pika should be configured with frame_max=512000 (seemingly must be changed in spec.py in addition to normal connection definition)

## Updating Mongo
Occasionally ingest of a record into mongo fails due to a number of possible problems
(badly formatted metadata, encoding issues, unexpected schema elements).  These problems
are visible as errors and warnings in the ReadRecords.log file.

In other cases, the record may get created successfully in mongo but its serialization into
a solr document may fail due to unexpected formatting or schema conversion.  These errors
are found in the SolrUpdateWorker.log and ErrorHandlerWorker.log files.

When such problems are fixed in the ADS classic records or new code is deployed to deal with
them, it may be necessary to force the re-creation of a specific record in mongo. This is because
by default the ingest pipeline will only update a record when its metadata is updated (by
comparing its json fingerprint), and therefore will not detect a change in the handling of the
metadata in software.

To force an update in mongo of a list of bibcodes use the following:
```
python run.py --ignore-json-fingerprints --target-bibcodes @reindex/reingest_20161122.txt
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

## Updating the code

When new code for the pipeline (or any of the libraries it uses) is released, it takes two steps
to have it become active in the ingest process:

1. deploy code in the proper location: `git pull`

1. restart running processes so that new code is loaded and executed: `supervisorctl restart ADSimportpipeline`

