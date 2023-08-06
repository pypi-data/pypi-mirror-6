'''
Created on Jan 17, 2014

@author: Jose Borreguero
'''
import unittest

from logger import tr
from channelgroup import ChannelGroup
from dsfgroup_test import LoadDsfGroup

class TestChannelGroup(unittest.TestCase):


  def test_InitFromDsfGroup(self):
    dsfgroup, fseries = LoadDsfGroup()
    channelgroup = ChannelGroup()
    channelgroup.InitFromDsfGroup(dsfgroup)

    channel_index = 700*4+321 # select one channel
    channel = channelgroup[channel_index]

    series = channel.signalseries
    self.assertAlmostEqual(series[0], 0.0302994, places=6)
    self.assertAlmostEqual(series[-1], 0.0289113, places=6)

    series = channel.errorseries
    self.assertAlmostEqual(series[0], 0.001094, places=6)
    self.assertAlmostEqual(series[-1], 0.00107701, places=6)

  def test_InitializeInterpolator(self):
    dsfgroup, fseries = LoadDsfGroup()
    channelgroup = ChannelGroup()
    channelgroup.InitFromDsfGroup(dsfgroup)
    print "\nInterpolating. Please wait some seconds..."
    channelgroup.InitializeInterpolator(running_regr_type = 'linear')

    temperature = 265.7
    dsf = channelgroup(temperature) # interpolate a dynamic structure factor
    channel_index = 700*4+321 # select one channel
    signal = dsf.intensities[4][321]
    error = dsf.errors[4][321]
    self.assertAlmostEqual(signal, 0.04916, places=5)
    self.assertAlmostEqual(error, 0.00147, places=5)

def suite():
  loader = unittest.TestLoader()
  suite = unittest.TestSuite()
  suite.addTest(loader.loadTestsFromTestCase(TestChannelGroup))
  return suite

if __name__ == "__main__":
  unittest.TextTestRunner(verbosity=2).run(suite())