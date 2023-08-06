'''
Created on Jan 7, 2014

@author: Jose Borreguero
'''
from logger import vlog

class DsfGroup(object):
  '''
  This class implements a group of dynamic structure factors
  obtained as a series versus some external parameter
  '''


  def __init__(self):
    '''
    Attributes:
      fseries: list of external parameter values
      dsfseries: list of dynamical structure factors
      shape: shape of the dynamical structure factors
    '''
    self.fseries = None
    self.dsfseries = None
    self.shape = None

  def AppendDsf(self, dsf ):
    if self.shape is None:
      self.shape =  dsf.shape
      self.fseries = [ dsf.fvalue, ]
      self.dsfseries = [ dsf, ]
    elif self.shape == dsf.shape:
      self.fseries.append( dsf.fvalue )
      self.dsfseries.append( dsf )
    else:
      vlog.error('DsfGroup.AppendDsf() error: Shape of the structure factor different than shape of the group')

  def InsertDsf(self, dsf):
    ''' Insert in sorted order from low to high fvalue '''
    if self.shape is None:
      self.shape =  dsf.shape
      self.fseries = [ dsf.fvalue, ]
      self.dsfseries = [ dsf, ]
    else:
      import bisect
      i = bisect.bisect_left(self.fseries, dsf.fvalue)
      self.fseries.insert(i, dsf.fvalue)
      self.dsfseries.insert(i, dsf)

  def ExtractSignalSeries(self, index ):
    series = []
    for dsf in self.dsfseries:
      series.append( dsf.ExtractIntensity(index) )
    return series

  def ExtractErrorSeries(self, index ):
    series = []
    for dsf in self.dsfseries:
      series.append( dsf.ExtractError(index) )
    if None in series:
      return None
    return series