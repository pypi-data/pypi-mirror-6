'''
Created on Jan 16, 2014

@author: Jose Borreguero
'''
import unittest

from dsf import Dsf
from dsfgroup import DsfGroup

def LoadDsfGroup():
  ''' Helper method, serves a DsfGroup object to the tests '''
  dsfgroup = DsfGroup()
  temperatures = '100 150 175 200 225 250 300 350'.split()
  for temperature in temperatures:
    dsf = Dsf()
    dsf.Load('./data/exp{0}K.nxs'.format(temperature))
    dsf.SetFvalue(float(temperature))
    dsfgroup.AppendDsf(dsf)
  return dsfgroup, temperatures

class TestDsfGroup(unittest.TestCase):
  ''' This class implements the unit test for module dsfgroup '''

  def test_InitDsfGroup(self):
    ''' Test loading of the first dynamic structure factor into a group '''
    dsf = Dsf()
    dsf.Load('./data/exp100K.nxs')
    dsfgroup = DsfGroup()
    dsfgroup.AppendDsf(dsf)
    self.assertEqual(dsfgroup.shape, dsf.shape)
    self.assertEqual(len(dsfgroup.dsfseries), 1)
    self.assertEqual(dsfgroup.dsfseries[0], dsf)

  def test_AppendDsf(self):
    ''' Test loading of several dynamic structure factors into a group '''
    dsfgroup, temperatures = LoadDsfGroup()

    self.assertEqual(len(dsfgroup.dsfseries), len(temperatures))
    self.assertNotEqual(dsfgroup.dsfseries[0], dsfgroup.dsfseries[-1])

    dsf = dsfgroup.dsfseries[0] # structure factor at 100K
    self.assertAlmostEqual( dsf.intensities[4][321], 0.0302994, places=6)
    self.assertAlmostEqual( dsf.errors[4][321], 0.001094, places=6)

    dsf = dsfgroup.dsfseries[-1] # structure factor at 350K
    self.assertAlmostEqual( dsf.intensities[4][321], 0.0289113, places=6)
    self.assertAlmostEqual( dsf.errors[4][321], 0.00107701, places=6)

  def test_ExtractSignalSeries(self):
    ''' Test extract intensities and errors for a given dynamical channel'''

    dsfgroup, temperatures = LoadDsfGroup()
    self.assertEqual(len(dsfgroup.dsfseries), len(temperatures))
    channel_index = 700*4+321

    series = dsfgroup.ExtractSignalSeries(channel_index)
    self.assertAlmostEqual(series[0], 0.0302994, places=6)
    self.assertAlmostEqual(series[-1], 0.0289113, places=6)

    series = dsfgroup.ExtractErrorSeries(channel_index)
    self.assertAlmostEqual(series[0], 0.001094, places=6)
    self.assertAlmostEqual(series[-1], 0.00107701, places=6)


def suite():
  loader = unittest.TestLoader()
  suite = unittest.TestSuite()
  suite.addTest(loader.loadTestsFromTestCase(TestDsfGroup))
  return suite

if __name__ == "__main__":
  unittest.TextTestRunner(verbosity=2).run(suite())