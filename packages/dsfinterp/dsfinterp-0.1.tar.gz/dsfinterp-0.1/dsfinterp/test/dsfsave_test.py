'''
Created on Jan 29, 2014

@author: Jose Borreguero
'''
import unittest

try:
  import mantid.simpleapi as mapi
except ImportError:
  print 'mantid library not found!'
  raise
  
from logger import tr
from dsf import Dsf
from dsfsave import DsfSaveMantidWorkspace2D

class TestDsfSave(unittest.TestCase):

  def test_DsfSaveMantidWorkspace2D(self):
    mapi.LoadNexus(Filename='./data/exp100K.nxs',OutputWorkspace='ws')
    ws = mapi.mtd['ws']
    ws.dataY(4)[321] = 0.0
    ws.dataE(4)[321] = 0.0

    dsf = Dsf()
    dsf.Load('./data/exp100K.nxs')
    saver = DsfSaveMantidWorkspace2D()
    saver.Save(dsf,ws)

    self.assertAlmostEqual(ws.dataY(4)[321], 0.0302994, places=6) #equal up to 6 decimal places
    self.assertAlmostEqual(ws.dataE(4)[321], 0.001094, places=6)

def suite():
  loader = unittest.TestLoader()
  suite = unittest.TestSuite()
  suite.addTest(loader.loadTestsFromTestCase(TestDsfSave))
  return suite

if __name__ == "__main__":
  unittest.TextTestRunner(verbosity=2).run(suite())