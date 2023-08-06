'''
Created on Jan 14, 2014

@author: Jose Borreguero
'''
import unittest
from dsfload import DsfLoaderFactory, DsfLoaderMantidWorkspace2D, DsfLoaderMantidNexusFile

try:
  import mantid.simpleapi as mapi
except ImportError:
  print 'mantid library not found!'
  raise

class TestDsfLoad(unittest.TestCase):

  def test_DsfLoaderFactory(self):
    ''' Instantiate all loaders through the factory'''
    factory = DsfLoaderFactory()
    for datatype in factory.datatypes:
      loader = factory.Instantiate(datatype)
      self.assertEqual(datatype, loader.datatype)

  def test_DsfLoaderMantidWorkspace2D(self):
    ''' Load a Nexus file containing a workspace2D with data '''
    ws = mapi.LoadNexus(Filename='./data/exp100K.nxs') #workspace with 9 Q-values and 700-Evalues
    loader = DsfLoaderMantidWorkspace2D()
    intensities,errors = loader.Load(ws)
    nQ, nE = intensities.shape
    self.assertEqual(nQ, 9)
    self.assertEqual(nE, 700)
    self.assertAlmostEqual(intensities[4][321], 0.0302994, places=6) #equal up to 6 decimal places
    self.assertAlmostEqual(errors[4][321], 0.001094, places=6)

  def test_DsfLoaderMantidNexusFile(self):
    loader = DsfLoaderMantidNexusFile()
    intensities,errors = loader.Load('./data/exp100K.nxs')
    nQ, nE = intensities.shape
    self.assertEqual(nQ, 9)
    self.assertEqual(nE, 700)
    self.assertAlmostEqual(intensities[4][321], 0.0302994, places=6) #equal up to 6 decimal places
    self.assertAlmostEqual(errors[4][321], 0.001094, places=6)

def suite():
  loader = unittest.TestLoader()
  suite = unittest.TestSuite()
  suite.addTest(loader.loadTestsFromTestCase(TestDsfLoad))
  return suite

if __name__ == "__main__":
  unittest.TextTestRunner(verbosity=2).run(suite())