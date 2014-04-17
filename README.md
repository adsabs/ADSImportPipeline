ADS_records_merger
==============

Coordinates ingest of a full ADS record.

  1. Parses "classic" bibcodes files defined in settings.py
  1. Operates on any bibcode whose "timestamp" differs from the "JSON_fingerprint" field in the mongodb
  1. Uses ads.ADSExports.ADSRecords to consolidate data from classic based on bibcodes in 2.
  1. Parses resulting xmlobject to python dict via [xmltodict.py](http://github.com/martinblech/xmltodict)
  1. Enforces type=list on any potentially repeated entries
  1. Merges any repeated <metadata> blocks having the same @type attribute
  1. Insert (upsert=True) data to mongodb
