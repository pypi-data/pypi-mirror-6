'''
Created on Jan 7, 2014

@author: jbq
'''

import numpy
from channel import Channel
from dsf import Dsf
from logger import tr

class ChannelGroup(object):
  '''
  This class implements a group of channels
  representing a group of dynamic structure factors
  '''

  def __init__(self):
    '''
    Attributes:
      fseries: list of external parameter values
      channels: series of channels, one for each point of the dynamical domain.
    '''
    self.fseries = None
    self.channels = None
    self.shape = None

  def Nchannels(self):
    if self.shape is None:
      return 0
    return numpy.prod(self.shape)
  nchannels = property( fget = Nchannels )

  def InitFromDsfGroup(self, dsfg ):
    ''' Load a group of dynamic structure factors into a channel group '''
    self.fseries = dsfg.fseries
    self.shape = dsfg.shape
    # Instantiate the channels
    self.channels = numpy.empty( self.nchannels, dtype = object )
    # fill the channels.
    for i in range( self.nchannels ):
      self.channels[i] = Channel()
      self.channels[i].SetSignalSeries( dsfg.ExtractSignalSeries(i) )
      self.channels[i].SetErrorSeries( dsfg.ExtractErrorSeries(i) )

  def InitializeInterpolator(self, running_regr_type = 'linear', windowlength=3):
    ''' Create the spline interpolator for each channel '''
    def initInterp(channel):
      channel.InitializeInterpolator( self.fseries, running_regr_type = running_regr_type, windowlength=windowlength)
      return channel
    vinitInterp = numpy.vectorize( initInterp ) # faster than the classic "for" loop
    self.channels[:] = vinitInterp( self.channels )

  def __getitem__(self,index):
    ''' Return channel at appropriate index '''
    return self.channels[index]

  def __call__(self,fvalue):
    ''' Return a dsf object invoking the interpolators for the channels '''
    signalseries=[]
    errorseries=[]
    for ichannel in range(self.nchannels):
      signal,error = self[ichannel](fvalue)
      signalseries.append(signal)
      errorseries.append(error)
    dsf = Dsf()
    dsf.SetIntensities(numpy.array(signalseries).reshape(self.shape))
    dsf.SetErrors(numpy.array(errorseries).reshape(self.shape))
    dsf.SetFvalue(fvalue)
    return dsf
