import sys, os
PROJECT_HOME = os.path.abspath(os.path.join(os.path.dirname(__file__),'../../'))
sys.path.append(PROJECT_HOME)
from settings import BIBCODE_FILES

import os
import unittest

class TestBibcodeFiles(unittest.TestCase):
  @unittest.skipIf(any(['/proj/ads' in i for i in BIBCODE_FILES]),"Skipping reading of ADS bibcode files")
  def setUp(self):
    self.content = []
    for filename in BIBCODE_FILES+[os.path.join(PROJECT_HOME,'tests/stubdata','merge_test_cases.txt')]:
      with open(os.path.abspath(filename)) as fp:
        results = []
        for line in fp:
          if line and not line.startswith("#"):
            results.append( tuple(line.strip().split('\t')) )
      print "Read %(num_entries)s entires from %(filename)s" % {'num_entries':len(results),'filename':filename}
      self.content.append(results)

  def test_textContent(self):
    for content in self.content:
      for L in content:
        self.assertIsInstance(L,tuple)
        self.assertEqual(len(L),2) #The bibcode files are expected to have a <bibcode,note> per line
        self.assertEqual(len(L[0]),19) #Bibcodes should always have a fixed length of 19 characters

  def tearDown(self):
    del self.content

if __name__ == '__main__':
    unittest.main()
