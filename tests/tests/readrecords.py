#!/usr/bin/python
#

"""
Useful script to test the reading and serialization of input
records into JSON.  All bibcodes passed as arguments on the
command line are processed at once.

Here are some usage cases:

    python readrecords.py bibcode1 [bibcode2...]

    # process chunks of 100 bibcodes (default value for pipeline)
    cat list_of_bibcodes_file | xargs -n 100 python readrecords.py

    # process one by one
    cat list_of_bibcodes_file | xargs -n 1 python readrecords.py

"""


import os
import sys
import json
import codecs
import argparse

PROJECT_HOME = os.path.abspath(os.path.join(os.path.dirname(__file__),'../../'))
sys.path.insert(0, PROJECT_HOME)

from lib import ReadRecords
from lib import UpdateRecords
from lib import SolrUpdater

if __name__ == "__main__":
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr)

    argp = argparse.ArgumentParser()
    argp.add_argument(
        '--debug',
        default=False,
        action='store_true',
        dest='debug',
        help='turn on debugging')
    argp.add_argument(
        '--exported',
        default=False,
        action='store_true',
        dest='exported',
        help='output exported document')
    argp.add_argument(
        '--merged',
        default=False,
        action='store_true',
        dest='merged',
        help='output merged document')
    argp.add_argument(
        '--solr',
        default=False,
        action='store_true',
        dest='solr',
        help='output solr document')
    argp.add_argument('bibcodes', nargs='+')
    args = argp.parse_args()

    if len(args.bibcodes) == 0:
        sys.stderr.write("Usage: %s bibcode [...]\n" % sys.argv[0])
        sys.exit(1)

    sys.stderr.write("initializing cache...")
    ReadRecords.INIT_LOOKERS_CACHE()
    sys.stderr.write("done\n")

    # expected input is [(bibcode,json_fingerprint), ...]
    records = [(b,'fake') for b in args.bibcodes]
    exported = ReadRecords.readRecordsFromADSExports(records)
    if args.exported:
        print json.dumps(exported, indent=2)

    merged = UpdateRecords.mergeRecords(exported)
    if args.merged:
        print json.dumps(merged, indent=2)
        
    results = []
    i = 0
    for r in merged:
        if args.debug:
            sys.stderr.write("processing document:\n%s\n" % json.dumps(r, indent=2))
        i = i + 1
        r['_id'] = i
        s = SolrUpdater.SolrAdapter.adapt(r)
        SolrUpdater.SolrAdapter.validate(s)
        results.append(s)

    if args.solr:
        print json.dumps(results, indent=2)

    for r in results:
        print r['bibcode']

    sys.stderr.write("Processed %d/%d records\n" % (len(results), len(records)))

    if len(records) != len(results):
        input_bibcodes = set(args.bibcodes)
        output_bibcodes = set([r['bibcode'] for r in results])
        for r in (input_bibcodes - output_bibcodes):
            sys.stderr.write("FAILED: %s\n" % r)
        sys.exit(1)



