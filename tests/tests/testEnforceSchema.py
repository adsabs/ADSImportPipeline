import unittest
import sys, os
PROJECT_HOME = os.path.abspath(os.path.join(os.path.dirname(__file__),'../../'))
sys.path.append(PROJECT_HOME)
from lib import EnforceSchema
from stubdata import stubdata

class TestEnforceSchema(unittest.TestCase):
  def setUp(self):
    self.e = EnforceSchema.Enforcer()
    self.general = self.e._generalEnforcer(stubdata.GENERAL)
    self.properties = self.e._propertiesEnforcer(stubdata.PROPERTIES)
    self.references = self.e._referencesEnforcer(stubdata.REFERENCES)
    self.relations = self.e._relationsEnforcer(stubdata.RELATIONS)

  def test_enforceMetadataSchema(self):
    blocks = self.e.enforceMetadataSchema([stubdata.GENERAL,stubdata.PROPERTIES,stubdata.REFERENCES,stubdata.RELATIONS])
    self.assertIsInstance(blocks,list)
    self.assertEqual(blocks,[
      self.general,
      self.properties,
      self.references,
      self.relations,
    ])

  def test_generalEnforcer(self):
    self.maxDiff=None
    self.assertEqual(self.general,stubdata.GENERAL_ENFORCED)

  def test_propertiesEnforcer(self):
    #self.maxDiff=None
    self.assertEqual(self.properties,stubdata.PROPERTIES_ENFORCED)

  def test_referencesEnforcer(self):
    #self.maxDiff=None
    self.assertEqual(self.references,stubdata.REFERENCES_ENFORCED)

  def test_relationsEnforcer(self):
    #self.maxDiff=None
    self.assertEqual(self.relations,stubdata.RELATIONS_ENFORCED)