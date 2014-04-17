import sys,os
import logging
import json
from logging.handlers import RotatingFileHandler

PROJECT_HOME = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
sys.path.append(PROJECT_HOME)
import run
from settings import MONGO

LOGFILE = os.path.join(PROJECT_HOME,'logs','tests_merger.log')
LOG_LEVEL = logging.DEBUG
logfmt = '%(levelname)s\t%(process)d [%(asctime)s]:\t%(message)s'
datefmt= '%m/%d/%Y %H:%M:%S'
formatter = logging.Formatter(fmt=logfmt,datefmt=datefmt)
LOGGER = logging.getLogger('tests_ADS_records_merger')
logging.root.setLevel(LOG_LEVEL)
rfh = RotatingFileHandler(filename=LOGFILE,maxBytes=2097152,backupCount=3,mode='a') #2MB file
rfh.setFormatter(formatter)
ch = logging.StreamHandler() #console handler
ch.setFormatter(formatter)
LOGGER.handlers = []
LOGGER.addHandler(ch)
LOGGER.addHandler(rfh)

def main(*args,**kwargs):
  args = ['--bibcodes']
  with open(os.path.join(PROJECT_HOME,'tests','merge_test_cases2.txt'),'r') as fp:
    lines = fp.readlines()

  MONGO['DATABASE'] = 'tests_%s' % MONGO['DATABASE']
  args.extend([L.strip().split()[0] for L in lines if L and not L.startswith('#')])
  #args.extend(['--classic-databases','PHY','AST'])

  records = run.main(LOGGER,MONGO,args)

  with open(os.path.join(PROJECT_HOME,'tests','tests_output.txt'),'w') as fp:
    fp.write(json.dumps(records))


if __name__ == '__main__':
  main()