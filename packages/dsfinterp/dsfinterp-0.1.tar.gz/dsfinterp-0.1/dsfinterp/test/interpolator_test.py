'''
Created on Jan 16, 2014

@author: Jose Borreguero
'''
import unittest
import numpy

from interpolator import Interpolator
from logger import tr

class TestInterpolator(unittest.TestCase):

  def LoadSeries(self, infile):
    ''' Helper method, loads f-values, signals, and errors from a three-column file '''
    fseries = []
    signalseries = []
    errorseries = []
    for line in open(infile).readlines():
      if line[0]=='#': continue
      f, y, e = [float(x) for x in line.split()]
      fseries.append(f)
      signalseries.append(y)
      errorseries.append(e)
    return fseries,signalseries,errorseries

  def RecordTriad(self, fseries, signalseries, errorseries, outfile):
    ''' Helper method, saves to a file. For debugging purposes '''
    size = len(fseries)
    buf='# f signal error\n'
    for i in range(size):
      buf += '{0} {1} {2}\n'.format(fseries[i],signalseries[i],errorseries[i])
    open(outfile,'w').write(buf)

  def ServeInput(self, create_errorseries=False, outfile=None):
    ''' Helper method to serve data for the test cases 
    
    Arguments:
      [create_errorseries]: also generate a list of errors
      [outfile]: save the series to a file, for debugging purposes
    '''
    size = 100
    fseries = 1.0*numpy.arange(size)
    function = numpy.sin(2*numpy.pi*numpy.arange(size)*0.01)
    noise = 0.2*numpy.random.rand(size)
    signalseries = numpy.abs(function + noise)
    errorseries = None
    if create_errorseries:
      errorseries = 0.2*numpy.random.rand(size)
    if outfile:
      buf='#f  signal error\n'
      for i in range(size):
        buf += '{0} {1}'.format(fseries[i],signalseries[i])
        if create_errorseries:
          buf += ' {0}'.format(errorseries[i])
        buf +='\n'
      open(outfile,'w').write(buf)
    return fseries, signalseries, errorseries

  def test___init__(self):
    ''' Just run the linear and quadratic interpolations '''

    fseries, signalseries, errorseries = self.ServeInput()
    interpolator = Interpolator(fseries, signalseries, running_regr_type = 'linear', windowlength=0)
    y_interpolated = interpolator.y(fseries)
    e_interpolated = interpolator.e(fseries)
    self.assertAlmostEqual(numpy.sum(signalseries-y_interpolated), 0.0, places=10)
    self.assertAlmostEqual(numpy.sum(e_interpolated), 0.0, places=10)

    fseries, signalseries, errorseries = self.ServeInput()
    interpolator = Interpolator(fseries, signalseries, running_regr_type = 'linear', windowlength=5)
    y_interpolated = interpolator.y(fseries)
    e_interpolated = interpolator.e(fseries)

    fseries, signalseries, errorseries = self.ServeInput(create_errorseries=True)
    interpolator = Interpolator(fseries, signalseries, running_regr_type = 'linear', windowlength=5)
    y_interpolated = interpolator.y(fseries)
    e_interpolated = interpolator.e(fseries)

    fseries, signalseries, errorseries = self.ServeInput()
    interpolator = Interpolator(fseries, signalseries, running_regr_type = 'quadratic', windowlength=5)
    y_interpolated = interpolator.y(fseries)
    e_interpolated = interpolator.e(fseries)

    fseries, signalseries, errorseries = self.ServeInput(create_errorseries=True)
    interpolator = Interpolator(fseries, signalseries, running_regr_type = 'quadratic', windowlength=5)
    y_interpolated = interpolator.y(fseries)
    e_interpolated = interpolator.e(fseries)

  def test__call__(self):
    ''' Just make sure the object is callable '''
    fseries, signalseries, errorseries = self.ServeInput()
    interpolator = Interpolator(fseries, signalseries, running_regr_type = 'linear', windowlength=5)
    interpolator(numpy.mean(fseries))
    # Test the bounding errors
    self.assertEqual( interpolator(min(fseries)-1.0), (float('inf'),float('inf')) )
    self.assertEqual( interpolator(max(fseries)+1.0), (float('inf'),float('inf')) )


def suite():
  loader = unittest.TestLoader()
  suite = unittest.TestSuite()
  suite.addTest(loader.loadTestsFromTestCase(TestInterpolator))
  return suite

if __name__ == "__main__":
  unittest.TextTestRunner(verbosity=2).run(suite())