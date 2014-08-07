# ADSimportpipeline

[![Build Status](https://travis-ci.org/adsabs/ADSimportpipeline.svg?branch=master)](https://travis-ci.org/adsabs/ADSimportpipeline)

## Overview

Coordinates ingest of a full ADS record.

1. Parses "classic" bibcodes files defined in settings.py
1. Operates on any bibcode whose "timestamp" differs from the cooresponding "JSON_fingerprint" field in the mongodb
1. Uses ads.ADSExports.ADSRecords to consolidate data from classic based on bibcodes in 2.
1. Parses resulting xmlobject to python dict via xmltodict.py
1. Enforces type=list on any potentially repeated entries
1. Merges any repeated blocks having the same @type attribute
1. Insert (upsert=True) data to mongodb

Step 1 is initiated by invoking `run.py`. 

## Async workflow with rabbitMQ

- Invoking `run.py --async` publishes the `[(bibcode, fingerprint),...]` records to rabbitmq. 
- Workers that consume these messages are defined in `pipeline/psettings.py` and `pipeline/workers.py`.
- Workers are controlled via a master process in `pipeline/ADSimportpipeliny.py`.
 

## Requirements
- pika
- rabbitmq
- ADSExports
- pymongo + mongo
- Note: The rabbitmq server should be configured for frame_max=512000
- Note: pika should be configured with frame_max=512000 (seemingly must be changed in spec.py in addition to normal connection definition)
