#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
from aip.libs import read_records
from adsputils import setup_logging, load_config
from aip.db import session_scope
from aip.models import Records
from aip import app, tasks

import time
import mmap
import argparse
from collections import OrderedDict
from sqlalchemy.orm import load_only

config = load_config()
logger = setup_logging('run.py')



def readBibcodesFromFile(files): #rca: all here is old code, i don't see why mmap was used
    """Reads contents of the BIBFILES into memory; basically bibcode:json_fingerprint
    pairs.
    
    @param files: list of files to read from
    @return: OrderedDict instance
    """
    start = time.time()
    records = OrderedDict()
    
    for f in files:
        with open(f) as fp:
            logger.debug('...loading %s' % f)

            # Size 0 will read the ENTIRE file into memory!
            m = mmap.mmap(fp.fileno(), 0, prot=mmap.PROT_READ)  # File is open read-only
            if m.size() < 1 or os.path.getsize(f) < 1:
                logger.error('%s is seemingly an empty file; Exit!')
                sys.exit(1)

            # note the file is already in memory
            line = 'init'
            while line:
                line = m.readline()
                if not line or line.startswith('#'):
                    continue
                r = tuple(line.strip().split('\t'))
                if len(r) != 2:
                    msg = \
                        'A bibcode entry should be "bibcode<tab>JSON_fingerprint". Skipping: %s' \
                        % r
                    logger.warning(msg)
                    continue
                if r[0] not in records:
                    records[r[0]] = r[1]
            m.close()
    logger.info('Loaded data in %0.1f seconds' % (time.time() - start))
    return records


def main(*args):
    if args:
        sys.argv.extend(*args) #rca: hmmm....

    parser = argparse.ArgumentParser()

    parser.add_argument('--target-bibcodes', nargs='*', default=[],
                        dest='targetBibcodes',
                        help='Only analyze the specified bibcodes, and ignore their JSON fingerprints. Only works when --async=False. Use the syntax @filename.txt to read these from file (1 bibcode per line)'
                        )

    parser.add_argument('--dont-init-lookers-cache', default=False,
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
    args = parser.parse_args()

    # initialize cache (to read ADS records)
    if not args.dont_init_lookers_cache and read_records.INIT_LOOKERS_CACHE:
        start = time.time()
        logger.info('Calling init_lookers_cache()')
        read_records.INIT_LOOKERS_CACHE()
        logger.info('init_lookers_cache() returned in %0.1f sec'
                    % (time.time() - start))

    # read bibcodes:json_fingerprints into memory
    records = readBibcodesFromFile(config.get('BIBCODE_FILES'))
    targets = None
    if args.targetBibcodes:
        if args.targetBibcodes[0].startswith('@'):
            with open(args.targetBibcodes[0].replace('@', '')) as fp:
                targetBibcodes = [L.strip() for L in
                        fp.readlines() if L and not L.startswith('#')]
        else:
            targetBibcodes = args.targetBibcodes
        targets = {bibcode:records[bibcode] for bibcode in targetBibcodes}
    records = read_records.canonicalize_records(records, targets)

    # we can force updates
    if args.ignore_json_fingerprints:
        records = [(r[0], 'ignore') for r in records]
        
    # get all bibcodes from the storage (into memory)
    store = set()
    with app.session_scope() as session:
        for r in session.query(Records).options(load_only(['bibcode'])).all():
            store.add(r.bibcode)
    
    # discover differences
    canonical_bibcodes = set([x[0] for x in records])
    orphaned = store.difference(canonical_bibcodes)
    
    # submit orphaned docs (to be deleted)
    if args.process_deletions:
        if len(orphaned) > args.max_deletions:
            logger.critical('|'.join(orphaned)) #rca: hmm...
            logger.critical('Too many deletions: {} > {}'.format(len(orphaned),
                            args.max_deletions))
            sys.exit(1)
        for x in orphaned:
            tasks.task_delete_documents.delay(x)
    
    # submit others (to be compared and updated if necessary)
    bpj = config.get('BIBCODES_PER_JOB', 100)
    step = len(records) / 100
    i = 0
    j = 0
    while i < len(records):
        payload = records[i:i+bpj]
        tasks.task_find_new_records.delay(payload)
        if i / step > j: 
            logger.info('There are %s records left (%0.1f%% completed)'
                             % (len(records)-i, ((len(records)-i) / 100.0)))
            j = i / step
        i += bpj
        

if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        pass  # this exception is raised by argparse if -h or wrong args given; we will ignore.
    except:
        raise    
