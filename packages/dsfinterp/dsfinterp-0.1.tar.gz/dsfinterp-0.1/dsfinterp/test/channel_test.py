'''
Created on Jan 16, 2014

@author: Jose Borreguero
'''
import unittest
import numpy

from channel import Channel

class TestChannel(unittest.TestCase):

  """
  def test_SetSeries(self):
    ''' Test signalseries and errorseries are properly initialized '''
    channel = Channel()

    signalseries = [1.42, 4.98, 2.78, 2.13, 2.69, 8.63, 5.88, 4.24, 8.96, 2.50]
    channel.SetSignalSeries(signalseries)
    self.assertEqual(channel.signalseries[0], signalseries[0])
    signalseries[0] += 1.0
    self.assertNotEqual(channel.signalseries[0], signalseries[0])

    errorseries = [0.42, 0.98, 0.78, 0.13, 0.69, 0.63, 0.88, 0.24, 0.96, 0.50]
    channel.SetErrorSeries(None)
    self.assertEqual(channel.errorseries, None)
    channel.SetErrorSeries(errorseries)
    self.assertEqual(channel.errorseries[-1], errorseries[-1])

  def test_InitializeInterpolator(self):
    fseries = 1.0*numpy.arange(10)
    channel = Channel()

    signalseries = [1.42, 4.98, 2.78, 2.13, 2.69, 8.63, 5.88, 4.24, 8.96, 2.50]
    channel.SetSignalSeries(signalseries)
    channel.InitializeInterpolator(fseries)

    errorseries = [0.42, 0.98, 0.78, 0.13, 0.69, 0.63, 0.88, 0.24, 0.96, 0.50]
    channel.SetErrorSeries(errorseries)
    channel.InitializeInterpolator(fseries)
    errorseries = [0.42, 0.98, 0.78, 0.13, 0.69, 0.63, 0.88, 0.24, 0.96, 0.50]
  """

  def test___call__(self):
    fseries = 1.0*numpy.arange(10)
    channel = Channel()

    signalseries = [1.42, 4.98, 2.78, 2.13, 2.69, 8.63, 5.88, 4.24, 8.96, 2.50]
    channel.SetSignalSeries(signalseries)
    channel.InitializeInterpolator(fseries)
    channel(numpy.mean(fseries))
    # Check bounds
    self.assertEqual( channel(min(fseries)-1.0), (float('inf'),float('inf')) )
    self.assertEqual( channel(max(fseries)+1.0), (float('inf'),float('inf')) )

def suite():
  loader = unittest.TestLoader()
  suite = unittest.TestSuite()
  suite.addTest(loader.loadTestsFromTestCase(TestChannel))
  return suite

if __name__ == "__main__":
  unittest.TextTestRunner(verbosity=2).run(suite())