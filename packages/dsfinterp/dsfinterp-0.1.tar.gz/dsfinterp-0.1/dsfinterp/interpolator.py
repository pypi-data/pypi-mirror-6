'''
Created on Jan 6, 2014

@author: jbq
'''
import numpy
from logger import vlog, tr
import copy

class Interpolator(object):
  '''
  Evaluate the structure factor at a particular phase point for any
  value of the external parameters
  '''


  def __init__(self, fseries, signalseries, errorseries=None, running_regr_type = 'linear', windowlength=3):
    '''
    Arguments:
      [running_regr_type]: method for the local, runnig regression
    
    Attributes:
      range: minimum and maximum of the fseries
      fitted: values of the structure factor at the external parameter values after the running regression
      errors: errorseries or estimated errors at the external parameter values from the running regression
      y: interpolator object for the struc ture factor (cubic spline)
      e: interpolator object for the error (linear)
      running_regr_type: type of running regression
      windowlength: length of window where local regression is done. Select zero for no regression
    '''
    # Deal with possible errors
    if len( fseries ) != len( signalseries ):
      vlog.error( 'signal and external parameter series have different lenght!' )
    self.running_regr_type = running_regr_type
    self.windowlength = windowlength
    self.range = ( fseries[ 0 ], fseries[ -1 ] )
    # Do running regression, and if necessary estimate errors
    if self.windowlength and running_regr_type == 'linear':
      if self.windowlength < 3:
        message = 'Linear regression requires a window length bigger than 2'
        vlog.error(message)
        raise ValueError(message)
      from scipy.stats import linregress
      if len( fseries ) < self.windowlength:
        vlog.error( 'series has to contain at least {0} members'.format( windowlength ) )
      else:
        # Lower boundary, the first self.windowlength/2 values
        x = fseries[ : self.windowlength ]
        y = signalseries[ : self.windowlength ]
        slope, intercept, r_value, p_value, std_err = linregress( x, y )
        linF = lambda xx: intercept + slope * xx
        self.fitted = []
        for i in range(0, 1+self.windowlength/2):
          self.fitted.append(linF(x[i]))
        residuals = numpy.square(numpy.vectorize(linF)(x) - y)
        residual = numpy.sqrt( numpy.mean(residuals)) #average residual
        self.errors = [residual,] * (1+self.windowlength/2)
        # Continue until hitting the upper boundary
        index = 1 # lower bound of the regression window
        while ( index + self.windowlength <= len( fseries ) ):
          x = fseries[ index : index + self.windowlength ]
          y = signalseries[ index : index + self.windowlength ]
          slope, intercept, r_value, p_value, std_err = linregress( x, y )
          linF = lambda xx: intercept + slope * xx
          self.fitted.append(linF(x[self.windowlength/2]))
          residuals = numpy.square(numpy.vectorize(linF)(x) - y)
          residual = numpy.sqrt( numpy.mean(residuals)) #average residual
          self.errors.append(residual)
          # Resolve the upper boundary
          if index + self.windowlength == len( fseries ):
            for i in range(1+self.windowlength/2, self.windowlength):
              self.fitted.append(linF(x[i]))
              self.errors.append(residual)
          index += 1
    elif self.windowlength and running_regr_type == 'quadratic':
      if self.windowlength < 4:
        message = 'Quadratic regression requires a window length bigger than 3'
        vlog.error(message)
        raise ValueError(message)
      from numpy import polyfit
      if len( fseries ) < self.windowlength:
        vlog.error( 'series has to contain at least {0} members'.format( self.windowlength ) )
      else:
        # Lower boundary, the first three values
        x = fseries[ : self.windowlength ]
        y = signalseries[ : self.windowlength ]
        coeffs, residuals, rank, singular_values, rcond= polyfit(x,y,2, full=True) #second order polynomial
        quadF = lambda xx: coeffs[0]*xx*xx + coeffs[1]*xx + coeffs[2]
        self.fitted = []
        for i in range(0, 1+self.windowlength/2):
          self.fitted.append(quadF(x[i]))
        residual = numpy.sqrt(numpy.mean( residuals )) #average residual
        self.errors = [residual,] * (1+self.windowlength/2)
        # Continue until hitting the upper boundary
        index = 1 # lower bound of the regression window
        while ( index + self.windowlength <= len( fseries ) ):
          x = fseries[ index : index + self.windowlength ]
          y = signalseries[ index : index + self.windowlength ]
          coeffs, residuals, rank, singular_values, rcond = polyfit(x,y,2, full=True) #second order polynomial
          quadF = lambda xx: coeffs[0]*xx*xx + coeffs[1]*xx + coeffs[2]
          self.fitted.append(quadF(x[self.windowlength/2]))
          residuals = numpy.square(numpy.vectorize(quadF)(x) - y)
          residual = numpy.sqrt( numpy.mean(residuals)) #average residual
          self.errors.append(residual)
          # Resolve the upper boundary
          if index + self.windowlength == len( fseries ):
            for i in range(1+self.windowlength/2, self.windowlength):
              self.fitted.append(quadF(x[i]))
              self.errors.append(residual)
          index += 1
    else:
      if self.windowlength == 0:
        self.fitted = copy.copy(signalseries)
        self.errors = [0.,] * len( fseries )
      else:
        vlog.warning( 'Requested regression type not recogized' )
    # Passed errors take precedence over calculated errors
    if errorseries is not None:
      self.errors = errorseries
    # Interpolators for fitted and errors
    from scipy.interpolate import interp1d, UnivariateSpline
    x = numpy.array( fseries )
    y = numpy.array( self.fitted )
    e = numpy.array( self.errors )
    if e.any():
      min_nonzero_error = numpy.min(e[numpy.nonzero(e)]) # smallest non-zero error
      e = numpy.where(e >=min_nonzero_error, e, min_nonzero_error) # substitute zero errors with the smallest non-zero error
      w = 1.0 / e
      s = len( fseries ) 
    else: # in the case of no errors, force the spline to pass through all points
      w = numpy.ones(len(fseries))
      s = 0
    self.y = UnivariateSpline( x, y, w=w, s=s )
    self.e = interp1d(x, e, kind='linear')


  def __call__(self, fvalue):
    ''' Evalue the interpolators for the particular value of the external parameter '''
    if self.range[0] <= fvalue <= self.range[1]:
      return self.y(fvalue), float(self.e(fvalue))
    else:
      vlog.error( 'Value outside of interpolating bounds' )
      return ( float( 'inf' ), float( 'inf' ) )