'''
Created on Jan 16, 2014

@author: Jose Borreguero
'''

import unittest
from logger import vlog, tr
from dsf import Dsf 

class TestDsf(unittest.TestCase):
  ''' This class implements the unit test for module dsf '''

  def test_LoadMantidNexusFile(self):
    ''' Load intensities and errors from a Mantid Nexus file '''
    dsf = Dsf()
    dsf.Load('./data/exp100K.nxs')
    self.assertEqual( dsf.shape, (9,700) )
    self.assertEqual( dsf.errors.shape, (9,700) )

  def test_LoadMantidWorkspace2D(self):
    ''' Load intensities and errors from a Mantid Workspace2D '''

    try:
      from mantid.simpleapi import LoadNexus
    except ImportError:
      vlog.error('mantid library not found!')
      raise ImportError
    workspace = LoadNexus('./data/exp100K.nxs')
    dsf = Dsf()
    dsf.Load(workspace)
    self.assertEqual(dsf.shape, (9,700))
    self.assertEqual(dsf.errors.shape, (9,700))

  def test_LoadNotSupported(self):
    wrongdata = ''
    dsf = Dsf()
    self.assertRaises(TypeError,dsf.Load, wrongdata)

  def test_LoadMantidNexusSimulatedFile(self):
    ''' Load simulated data, containing no errors '''
    dsf = Dsf()
    dsf.Load('./data/sim200K.nxs')
    self.assertEqual(dsf.shape, (9,1000))
    self.assertEqual(dsf.errors, None)


def suite():
  loader = unittest.TestLoader()
  suite = unittest.TestSuite()
  suite.addTest(loader.loadTestsFromTestCase(TestDsf))
  return suite

if __name__ == "__main__":
  unittest.TextTestRunner(verbosity=2).run(suite())