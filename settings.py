import os
import sys

PROJECT_HOME = os.path.abspath(os.path.dirname(__file__))

# CLASSIC_BIBCODES = {
#   'AST': '/proj/ads/abstracts/ast/load/current/index.status',
#   'PHY': '/proj/ads/abstracts/phy/load/current/index.status',
#   'GEN': '/proj/ads/abstracts/gen/load/current/index.status',
#   'PRE': '/proj/ads/abstracts/pre/load/current/index.status',
# }
# CLASSIC_BIBCODES = {
#   'AST': 'ast.txt',
# }
CLASSIC_BIBCODES = {}

BIBCODES_PER_JOB = 200

MONGO = {
  'HOST': os.environ.get('MONGO_HOST','localhost'),
  'PORT': os.environ.get('MONGO_PORT',27017),
  'DATABASE': os.environ.get('MONGO_DATABASE','ads'),
  'USER': None,    #May be set to None
  'PASSWD': None,  #May be set to None
  'COLLECTION': 'classic',

}
