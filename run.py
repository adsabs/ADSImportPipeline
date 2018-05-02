#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import datetime
import gzip

from aip.classic import read_records
from aip.direct import serialize_direct as sd
from adsputils import setup_logging, load_config
from aip.models import Records, ChangeLog
from aip import tasks
import pyingest.parsers.aps as aps
import pyingest.parsers.arxiv as arxiv

import time
import argparse
from collections import OrderedDict
from sqlalchemy.orm import load_only

app = tasks.app
logger = setup_logging('run.py')


def read_bibcodes(files):
    """Reads contents of the BIBFILES into memory; basically bibcode:json_fingerprint
    pairs.

    @param files: list of files to read from
    @return: OrderedDict instance
    """
    start = time.time()
    records = OrderedDict()

    for f in files:
        logger.debug('...loading %s' % f)
        with open(f) as fp:
            for line in fp:
                line = line.strip()
                if not line or line.startswith('#'):
                        continue
                r = line.split('\t')
                if len(r) != 2:
                    msg = \
                        'A bibcode entry should be "bibcode<tab>JSON_fingerprint". Skipping: %s' \
                        % r
                    logger.warning(msg)
                    continue
                if r[0] not in records:
                    records[r[0]] = r[1]

    logger.info('Loaded data in %0.1f seconds' % (time.time() - start))
    return records


def do_the_work(records, orphaned, max_deletions=-1):
    # submit orphaned docs (to be deleted)
    if len(orphaned):
        if max_deletions > 0 and len(orphaned) > max_deletions:
            logger.critical('Too many deletions: {} > {}'.format(len(orphaned),
                            max_deletions))
            logger.critical('%s...%s'.join(', '.join(orphaned[0:5], ', '.join(orphaned[-5:])))) #rca: yes, i know - when len(orphaned) < 10, we'll have duplicates...but i don't care
            sys.exit(1)
        for x in orphaned:
            tasks.task_delete_documents.delay(x)

    # submit others (to be compared and updated if necessary)
    bpj = app.conf.get('BIBCODES_PER_JOB', 100)
    step = max(len(records) / 100, 1)
    i = 0
    j = 0
    while i < len(records):
        payload = records[i:i+bpj]
        if payload[0][1] == 'ignore':
            tasks.task_read_records.delay(payload)
        else:
            tasks.task_find_new_records.delay(payload)
        if i / step > j:
            logger.info('There are %s records left (%0.1f%% completed)'
                             % (len(records)-i, ((len(records)-i) / 100.0)))
            j = i / step
        i += bpj


def show_api_diagnostics(records, orphaned, max_deletions=-1):
    print 'We would be processing %s records' % len(records)
    print 'Showing the first 3', records[0:3]
    print 'max_deletions=%s' % max_deletions
    print 'And we found %s orphaned records (those would be deleted)' % len(orphaned)

    to_be_deleted = []
    if len(orphaned):
        print 'I am submitting the first 3 records to be deleted'
        for x in list(orphaned)[0:3]:
            orig = app.get_record(x)
            if orig is None:
                orig = x
            to_be_deleted.append(orig)
            print x, tasks.task_delete_documents(x)

    submitted = []
    if len(records):
        print 'I am submitting first 3 record for processing'
        for x in records[0:3]:
            print x
            orig = app.get_record(x[0])
            if orig is None:
                orig = x[0]
            submitted.append(orig)

        print tasks.task_find_new_records(records[0:3])

    print 'Sleeping for 15secs'
    time.sleep(15)

    if len(to_be_deleted):
        print 'Now checking if the deleted docs were deleted'
        for x in to_be_deleted:
            print x
            if isinstance(x, basestring): # we had no prior record
                rec = app.get_record(x)
                print x, 'We had no db record originally, do we have one now?', rec
            else:
                rec = app.get_record(x['bibcode'])
                print x, 'We had db record originally, do we have one now?', rec and rec.toJSON() or None

    print 'Checking what happened to the submitted records (only inside our own database)'
    for x in submitted:
        print x
        if isinstance(x, basestring):
            rec = app.get_record(x)
            print x, 'We had no db record originally, do we have one now?', rec or rec.toJSON() or None
        else:
            rec = app.get_record(x['bibcode'])
            print x, 'We had db record originally, \noriginal=%s\ncurrent=%s?' % (x, rec or rec.toJSON() or None)


def main(*args):
    if args:
        sys.argv.extend(*args) #rca: hmmm....

    parser = argparse.ArgumentParser()

    parser.add_argument('-b',
                        '--bibcodes',
                        nargs='*',
                        default=[],
                        dest='bibcodes',
                        help='Only analyze the specified bibcodes, and ignore their JSON fingerprints.' +
                        ' Use the syntax @filename.txt to read these from file (1 bibcode per line)'
                        )

    parser.add_argument('--no-cache', default=False,
                        action='store_true',
                        dest='dont_init_lookers_cache',
                        help='dont call ADSExports2.init_lookers_cache()'
                        )

    parser.add_argument('--ignore-json-fingerprints', default=False,
                        action='store_true',
                        dest='ignore_json_fingerprints',
                        help='ignore json fingerprints when finding new records to update (ie, force update)'
                        )

    parser.add_argument('--process-deletions', default=False,
                        action='store_true', dest='process_deletions',
                        help='Find orphaned bibcodes in the storage, then send these bibcodes to delete via rabbitMQ. No updates will be processed with this flag is set.'
                        )

    parser.add_argument('--max-deletions', default=2000, type=int,
                        dest='max_deletions',
                        help='Maximum number of deletions to attempt; If over this limit, exit and log an error'
                        )

    parser.add_argument('-d',
                        '--diagnose',
                        dest='diagnose',
                        action='store_true',
                        default=False,
                        help='Show me what you would do with bibcodes')

    parser.add_argument('-r',
                        '--replay-deletions',
                        dest='replay_deletions',
                        action='store_true',
                        default=False,
                        help='Resubmit all bibcodes (that were ever deleted) again to the master pipeline.')

    parser.add_argument('--APS',
                        dest='direct',
                        action='store_const',
                        const='APS',
                        help='Launch a direct import of APS content.')

    parser.add_argument('--Arxiv',
                        dest='direct',
                        action='store_const',
                        const='Arxiv',
                        help='Launch a direct import of Arxiv content.')

    parser.add_argument('-c',
                        '--caldate',
                        dest = 'caldate',
                        action = 'store',
                        help = 'Process direct import metadata for YYYY-MM-DD')

    args = parser.parse_args()

# for testing of direct import
    if args.direct:

        parsed_records = list()

        if isinstance(args.caldate,basestring):
            pass
        else:
            args.caldate = datetime.datetime.today().strftime('%Y-%m-%d')

        if args.direct == 'APS':

            logfile = app.conf.get('APS_UPDATE_AGENT_LOG') + args.caldate
            reclist = list()
            with open(logfile,'rU') as flist:
                for l in flist.readlines():
                    a,b,c = l.split('\t')
                    reclist.append(b)

            if (len(reclist) > 0):
                for f in reclist:
                    with open(f,'rU') as fp:
                        try:
                            parser = aps.APSJATSParser()
                            parsed_records.append(parser.parse(fp))
                        except:
                            logger.error("bad record: %s from %s ingest"%(f,args.direct))

        elif args.direct == 'Arxiv':

            logfile = app.conf.get('ARXIV_UPDATE_AGENT_DIR') + '/UpdateAgent.out.' + args.caldate + '.gz'
            reclist = list()
            with gzip.open(logfile,'r') as flist:
                for l in flist.readlines():
                    a = app.conf.get('ARXIV_INCOMING_ABS_DIR') + '/' + l.split()[0]
                    reclist.append(a)

            if (len(reclist) > 0):
                for f in reclist:
                    with open(f,'rU') as fp:
                        try:
                            parser = arxiv.ArxivParser()
                            parsed_records.append(parser.parse(fp))
                        except:
                            logger.error("bad record: %s from %s ingest"%(f,args.direct))


        else:
            print "lol, wut?"

        for r in parsed_records:

#           tasks.task_output_results(direct_translate(r))

            foo = sd.translate(r)
            if type(foo) is not type(None):
                tasks.task_output_direct(sd.translate(r))
            else:
                print "zomg nonetype."




    else:

        # initialize cache (to read ADS records)
        if not args.dont_init_lookers_cache and read_records.INIT_LOOKERS_CACHE:
            start = time.time()
            logger.info('Calling init_lookers_cache()')
            read_records.INIT_LOOKERS_CACHE()
            logger.info('init_lookers_cache() returned in %0.1f sec'
                        % (time.time() - start))

        # read bibcodes:json_fingerprints into memory
        records = read_bibcodes(app.conf.get('BIBCODE_FILES'))
        logger.info('Read %s records', len(records))
        targets = OrderedDict()
        if args.bibcodes:
            for t in args.bibcodes:
                if t.startswith('@'):
                    with open(t.replace('@', '')) as fp:
                        for line in fp:
                            if line.startswith('#'):
                                continue
                            b = line.strip()
                            if b not in records:
                                logger.error('Asked to process %s but the bibcode is not in the list of canonical bibcodes (%s)', 
                                             b, app.conf.get('BIBCODE_FILES'))
                                continue
                            if b:
                                targets[b] = records[b]
                else:
                    targets[t] = records[t]

        #TODO(rca): getAlternates is called multiple times unnecessarily
        records = read_records.canonicalize_records(records, targets or records, ignore_fingerprints=args.ignore_json_fingerprints)
        logger.info('Canonicalize %s records', len(records))

        if args.replay_deletions:
            with app.session_scope() as session:
                for r in session.query(ChangeLog).filter(ChangeLog.key == 'deleted').yield_per(1000):
                    tasks.task_delete_documents.delay(r.oldvalue)

        # discover differences
        orphaned = set()
        if args.process_deletions:
            logger.info('Will discover orphans')
            # get all bibcodes from the storage (into memory)
            store = set()
            with app.session_scope() as session:
                for r in session.query(Records).options(load_only('bibcode')).yield_per(1000):
                    store.add(r.bibcode)
            logger.info('Loaded %s bibcodes from the database', len(store))
            canonical_bibcodes = set([x[0] for x in records])
            orphaned = store.difference(canonical_bibcodes)
            logger.info('Discovered %s orphans', len(orphaned))


        if args.diagnose:
            logger.info('Running diagnostics on %s records (orphaned=%s)', len(records), len(orphaned))
            show_api_diagnostics(records, orphaned)
        else:
            logger.info('Running %s records (orphaned=%s)', len(records), len(orphaned))
            do_the_work(records, orphaned)




if __name__ == '__main__':
    main()
