import unittest

from aip.libs import enforce_schema
from tests.stubdata import stubdata

class TestEnforceSchema(unittest.TestCase):
    def setUp(self):
        self.e = enforce_schema.Enforcer()
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
        #self.maxDiff=None
        self.assertEqual(self.general,stubdata.GENERAL_ENFORCED)

    def test_propertiesEnforcer(self):
        self.maxDiff=None
        self.assertEqual(self.properties,stubdata.PROPERTIES_ENFORCED)

    def test_referencesEnforcer(self):
        self.maxDiff=None
        self.assertEqual(self.references,stubdata.REFERENCES_ENFORCED)

    def test_relationsEnforcer(self):
        #self.maxDiff=None
        self.assertEqual(self.relations,stubdata.RELATIONS_ENFORCED)

    def test_parseDate(self):
        testCases = {
          '2012-01-01': u'2012-01-01T00:30:00.000000Z',
          '2012-01':    u'2012-01-01T00:00:00.000000Z',
          '2012':       u'2012-01-01T00:00:00.000000Z',
          '2012-01-00': u'2012-01-01T00:00:00.000000Z',
          '2012-00-00': u'2012-01-01T00:00:00.000000Z',
        }
        for _input, _output in testCases.iteritems():
            self.assertEqual(self.e.parseDate(_input),_output)


if __name__ == '__main__':
    unittest.main()
