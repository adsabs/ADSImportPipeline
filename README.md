# ADSimportpipeline

[![Build Status](https://travis-ci.org/adsabs/ADSimportpipeline.svg?branch=master)](https://travis-ci.org/adsabs/ADSimportpipeline)

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
