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


## Maintainers

Steve, Roman
