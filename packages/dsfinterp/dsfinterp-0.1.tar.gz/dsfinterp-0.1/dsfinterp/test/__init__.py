from dsfinterp import dsfload
import test_dsfload
import unittest

def suite():
  import doctest
  suite = unittest.TestSuite()
  suite.addTests(doctest.DocTestSuite(dsfload))
  suite.addTests(test_dsfload.suite())
  return suite

if __name__ == '__main__':
  unittest.TextTestRunner(verbosity=2).run(suite())