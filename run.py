#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
from aip.libs import utils, read_records
from aip.tasks import task_find_new_records
from aip.models import Records
from aip import app

import time
import mmap
import argparse
from collections import OrderedDict
from sqlalchemy.orm import load_only

config = utils.load_config()
logger = utils.setup_logging('run.py')



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
        pairs = []  # holds (bibcode, fingerprint) pairs
        for bib in targetBibcodes:
            pairs.append((bib, None))
        task_find_new_records.delay(pairs)
        return  # return will be cleaned up later
    
    # submit orphaned docs (to be deleted)
    # discover differences
    # this will not work because it relies on the store which no longer is available
    canonical_bibcodes = set([x[0] for x in records])
    orphaned = store.difference(canonical_bibcodes)
    if args.process_deletions:
        if len(orphaned) > args.max_deletions:
            logger.critical('|'.join(orphaned)) #rca: hmm...
            logger.critical('Too many deletions: {} > {}'.format(len(orphaned),
                            args.max_deletions))
            sys.exit(1)
        for x in orphaned:
            app.task_delete_documents.delay(x)
    
    # submit others (to be compared and updated if necessary)
    bpj = config.get('BIBCODES_PER_JOB', 100)
    step = len(records) / 100
    i = 0
    j = 0
    while i < len(records):
        payload = records[i:i+bpj]
        app.task_find_new_records.delay(payload)
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
