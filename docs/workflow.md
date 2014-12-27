# Workflow

Here's my workflow for using ADSrecords on adsx (if you don't care about xmltodict, you can remove that cooresponding code)

In [1]: import sys

In [2]: sys.path.append('/proj/ads/soft/python/lib/site-packages')

In [3]: cd /proj.adsx/ADSimportpipeline/
/proj.adsx/ADSimportpipeline

In [4]: from lib import xmltodict

In [5]: from ads.ADSCachedExports import ADSRecords, init_lookers_cache

In [6]: bibcode='2008OAP....21...57L';

In [7]: adsrecords = ADSRecords('full','XML',cacheLooker=True);adsrecords.addCompleteRecord(bibcode,fulltext=True);adsrecords = adsrecords.export();rec=xmltodict.parse(adsrecords.serialize())['records']['record'];metadata=rec['metadata'];general=[i for i in metadata if i['@type']=='general'];properties=[i for i in metadata if i['@type']=='properties'];

In [8]: import json

In [9]: print json.dumps(metadata, indent=2)


# How to get example data from ADSimportpipeline

The most straightforward way to do this is the following:

/proj.adsx/python/bin/python /proj.adsx/ADSimportpipeline/run.py --target-bibcodes "my_bibcode" --dump-output-to-file foo.txt --dont-init-lookers-cache

This process goes through all steps of the pipeline except, instead of writing to mongo, it dumps ascii to disk.

The ascii will contain both the non-merged (which is coming from ADSexports after the schema has been enforced) and merged document.

The process will block on bibcode file reading and canonical bibcode resolving, which takes about 3-5 minutes total.
