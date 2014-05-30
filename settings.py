import os
import sys

import logging
from logging.handlers import RotatingFileHandler

PROJECT_HOME = os.path.abspath(os.path.dirname(__file__))
LOGFILE = os.path.join(PROJECT_HOME,'logs','merger.log')
LOG_LEVEL = logging.DEBUG
#LOG_LEVEL = logging.INFO

# CLASSIC_BIBCODES = {
#   'AST': '/proj/ads/abstracts/ast/load/current/index.status',
#   'PHY': '/proj/ads/abstracts/phy/load/current/index.status',
#   'GEN': '/proj/ads/abstracts/gen/load/current/index.status',
#   'PRE': '/proj/ads/abstracts/pre/load/current/index.status',
# }
CLASSIC_BIBCODES = {
  'AST': 'ast.txt',
}

BIBCODES_PER_JOB = 200

#ADSrecords->mongodb mapping
# key: <how to get key from ADSExports dict>
# Not yet implemented; does nothing
SCHEMA = {
  'deletions': [
    ['metadata','properties','JSON_timestamp'],
    ['metadata','general','bibcode'],
  ],
}

MONGO = {
  'HOST': os.environ.get('MONGO_HOST','localhost'),
  'PORT': os.environ.get('MONGO_PORT',27017),
  'DATABASE': os.environ.get('MONGO_DATABSE','ads'),
  'USER': None,    #May be set to None
  'PASSWD': None,  #May be set to None
  'COLLECTION': 'classic',

}
auth = ''
if MONGO['USER'] and MONGO['PASSWD']:
  auth =  '%s@' % (':'.join([MONGO['USER'],MONGO['PASSWD']]))
MONGO['MONGO_URI'] = 'mongodb://%s%s:%s' % (auth,MONGO['HOST'],MONGO['PORT'])

logfmt = '%(levelname)s\t%(process)d [%(asctime)s]:\t%(message)s'
datefmt= '%m/%d/%Y %H:%M:%S'
formatter = logging.Formatter(fmt=logfmt,datefmt=datefmt)
LOGGER = logging.getLogger('ADS_records_merger')
logging.root.setLevel(LOG_LEVEL)
rfh = RotatingFileHandler(filename=LOGFILE,maxBytes=2097152,backupCount=3,mode='a') #2MB file
rfh.setFormatter(formatter)
ch = logging.StreamHandler() #console handler
ch.setFormatter(formatter)
LOGGER.handlers = []
LOGGER.addHandler(ch)
LOGGER.addHandler(rfh)
