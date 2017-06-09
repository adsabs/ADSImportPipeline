#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse

import sys, os
PROJECT_HOME = os.path.abspath(os.path.join(os.path.dirname(__file__),'../'))
sys.path.append(PROJECT_HOME)

from aip import app
from aip.db import session_scope
from aip.models import Records
from sqlalchemy.orm import load_only


def get_all_bibcodes():
    store = set()
    with session_scope() as session:
        for r in session.query(Records).options(load_only(['bibcode'])).all():
            store.add(r.bibcode)
    return store


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('bibcodes', nargs='*',
                        help='bibcodes to publish')

    parser.add_argument(
        '--from-file',
        nargs=1,
        default=None,
        dest='bibcode_file',
        type=str,
        help='Load bibcodes from file, one bibcode per line',
        )

    parser.add_argument('--whole-database', default=False,
                        dest='whole_database', action='store_true')

    parser.add_argument(
        '--bibcodes-per-message',
        nargs=1,
        default=100,
        dest='bibcodes_per_message',
        type=int,
        help='Publish N bibcodes at a time',
        )

    args = parser.parse_args()

    if args.whole_database:
        bibcodes = get_all_bibcodes()
    elif args.bibcode_file:
        with open(args.bibcode_file[0]) as fp:
            bibcodes = [L.strip() for L in fp.readlines() if L
                        and not L.startswith('#')]
    else:
        if not args.bibcodes and not args.whole_database:
            raise Exception('Not enough arguments given')
        if not args.whole_database:
            bibcodes = [i for i in args.bibcodes]
    
    for b in bibcodes:
        app.task_update_solr.delay(b) 
        


if __name__ == '__main__':
    main()
