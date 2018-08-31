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

libxml2 is required, you may want to install globally via brew and access via virtualenv --system-site-packages.

A useful script that helps you see how the documents are transformed is found in tests/tests/readrecords.py

## Updating the code

When new code for the pipeline (or any of the libraries it uses) is released, it takes two steps
to have it become active in the ingest process:

1. deploy code in the proper location: `git pull`

1. restart running processes so that new code is loaded and executed: `supervisorctl restart ADSimportpipeline`
(if running under supervisord).


## Maintainers

Steve, Roman
