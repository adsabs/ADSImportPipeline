# ADSimportpipeline

[![Build Status](https://travis-ci.org/adsabs/ADSimportpipeline.svg?branch=master)](https://travis-ci.org/adsabs/ADSimportpipeline)
[![Coverage Status](https://coveralls.io/repos/adsabs/ADSimportpipeline/badge.svg?branch=master)](https://coveralls.io/r/adsabs/ADSimportpipeline)

## Overview

Set of celery workers that ingest full ADS record and trigger updates of SOLR index.


## Configuration

Create `local_config.py` (in the top folder); you can override any variable that is specified in
the global `config.py`.

## Documentation

For details see: ./documentation.md


## Deployment

Follow the typical `eb-deploy` procedure for `backoffice` deployments.  



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
and then using unix's join command to print bibcodes which only appear in the canonical list
but not in the solr list:

```
env LC_ALL=C sort -f solrBibcodes.txt | join -i -v1 $ADS_ABSCONFIG/bibcodes.list.can - > notInSolr_20161122.txt
```

This creates a file with bibcodes that were in canonical but not
solr.  This list can be injected into the pipeline with:
```
python/bin/python2.7 utils/publish_bibcodes_to_solr.py --from-file reindex/notInSolr_20161122.txt
```

## Developing
Since the code makes use of ads.ADSCachedExports for data ingest, you will have to clone the adsabs/adspy
repo to test the code locally.  Until we properly write tests that mock that input, follow the
directions given in adsabs/adspy/DEVELOP.txt for setting up adspy to read the required files from ADS Classic.

A useful script that helps you see how the documents are transformed is found in tests/tests/readrecords.py

## Updating the code

When new code for the pipeline (or any of the libraries it uses) is released, it takes two steps
to have it become active in the ingest process:

1. deploy code in the proper location: `git pull`

1. restart running processes so that new code is loaded and executed: `supervisorctl restart ADSimportpipeline`
(if running under supervisord).

## Incorporating a new sub-pipeline

The steps below describe how to extend existing import pipeline. This is a preferred method to add a new
source (publisher) unless the transformations are really complex and it would be better to create a new
import pipeline just for that purpose.

  1. add a new storage column (if the new sub-pipeline needs to store its output)
    - run `alembic revision -m "......"` to update the database, example: `alembic/versions/43dc6621db1c_added_direct_ingest_pipeline.py`
    - update `aip/models.py`, add 3 new columns to the `storage` table
        - '<name>_data' : i.e. `arxiv_data` - the type is text, but for all practical purposes you should always use JSON formatted data
        - '<name>_created' : timestamp that says when this particular column was updated
        - '<name>_updated' : timestamp that says when this particular column was created
  1. place your sub-pipeline code into `aip/<subpipeline-name`; i.e. `aip/classic`
    - and unittests into `tests/<name>/...`, example `tests/classic/test_tasks.py`
  1. update app.py if necessary
    - it should contain methods that are generally useful
    - update its accompanying unittest: `tests/test_app.py`
  1. update `tasks.py`
    - create whatever queue/taks that is necessary for your pipeline
    - output is always redirected through `task_output_results`
        - modify this task to incorporate/load any additional data that should be exported
        - the sub-pipelines are NOT expected to be sending their own protobuf (ADSImportPipeline always sends `DenormalizedRecord`)
  1. update `run.py`
    - try to update the diagnostics() function to provide output useful for testing
    - add options to start/run your sub-pipeline


## Maintainers

Steve, Roman
