# ADSimportpipeline

[![Build Status](https://travis-ci.org/adsabs/ADSimportpipeline.svg?branch=master)](https://travis-ci.org/adsabs/ADSimportpipeline)
[![Coverage Status](https://coveralls.io/repos/adsabs/ADSimportpipeline/badge.svg?branch=master)](https://coveralls.io/r/adsabs/ADSimportpipeline)

## Overview

Set of celery workers that ingest full ADS record and send data to Master Pipeline.


## Configuration

Create `local_config.py` (in the top folder); you can override any variable that is specified in
the global `config.py`.


## Deployment

Follow the typical `eb-deploy` procedure for `backoffice` deployments.  


## Updating Solr
It is possible for Solr to be missing data on some bibcodes.  When
this happens, use ADSImportPipeline to send new data to master pipeline.
The AutomatedIngestReport automatically computes the list of missing bibcodes and
runs as a cron job (currently on adsqb).  The Ingest FAQ, stored on the Team Drive, contains the
various command to force reingesting of a set of bibcodes.  

## Developing
Since the code makes use of ads.ADSCachedExports for data ingest, you will have to clone the adsabs/adspy
repo to test the code locally.  Until we properly write tests that mock that input, follow the
directions given in adsabs/adspy/DEVELOP.txt for setting up adspy to read the required files from ADS Classic.

A useful script that helps you see how the documents are transformed is found in tests/tests/readrecords.py

## Updating the code

As with other ingest pipelines, when new code for the pipeline (or any of the libraries it uses)
is released, the production docker container can be updated with git pull and workers restarted with sv
or the container can be redeployed with eb-deploy.  

## Incorporating a new sub-pipeline

The steps below describe how to extend existing import pipeline. This is a preferred method to add a new
source (publisher) unless the transformations are really complex and it would be better to create a new
import pipeline just for that purpose.

  1. add a new storage column (if the new sub-pipeline needs to store its output)
    - run `alembic revision -m "......"` to update the database, example: `alembic/versions/43dc6621db1c_added_direct_ingest_pipeline.py`
    - update `aip/models.py`, add 3 new columns to the `storage` table
        - '<name>_data' : i.e. `direct_data` - the type is text, but for all practical purposes you should always use JSON formatted data
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
