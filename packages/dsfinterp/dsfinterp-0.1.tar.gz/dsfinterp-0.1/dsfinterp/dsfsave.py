'''
Created on Jan 28, 2014

@author: Jose Borreguero
'''

from logger import vlog
from abc import ABCMeta, abstractmethod


class DsfSave(object):
  '''
  Abstract class for dynamic structure factor savers
  '''
  __metaclass__ = ABCMeta

  def __init__(self):
    '''
    Constructor
    '''
    self.datatype = None

  @abstractmethod
  def Save(self, dsf, *args):
    ''' This method must be implemented on every subclass '''
    pass


class DsfSaveMantidWorkspace2D(DsfSave):
  ''' This class implements a saver into a Mantid Workspace2D '''

  def __init__(self):
    self.datatype='mantid::Workspace2D'

  def Save(self, dsf, ws):
    ''' Save the dynamics structure factor into the workspace
    dsf: the dynamics structure factor to save
    ws: workspace where Y and E will be overwritten with dsf contents
    '''
    dimension = len(dsf.shape)
    if dimension != 2:
      vlog.error('Dimension of the dynamics structure factor is not 2')
      return
    nhist = dsf.shape[0]
    size = dsf.shape[1]
    try:
      mhist = ws.getNumberHistograms()
      if nhist != mhist:
        vlog.error('Number of histograms in the worskpace does not match the dynamics structure factor first dimension')
        return
      for ihist in range(nhist):
        if ws.dataY(ihist).size != size:
          vlog.error('second dimension of the dynamics structure factor has different size than that of histogram with index '+str(ihist))
          return
        ws.dataY(ihist)[:] = dsf.intensities[ihist]
        ws.dataE(ihist)[:] = dsf.errors[ihist]
    except TypeError:
      vlog.error('the workspace is not of type '+self.datatype)
      return


class DsfSaveFactory(object):

  savers = { 'mantid::Workspace2D':DsfSaveMantidWorkspace2D,
            }

  def __init__(self):
    pass

  @property
  def datatypes(self):
    ''' Handy property returning the data types '''
    return DsfSaveFactory.savers.keys()

  def Instantiate(self, datatype):
    ''' Instantiate a dynamic structure factor saver of appropriate type '''
    if datatype not in self.datatypes:
      vlog.error('No dynamic structure factor loader for type {0}'.format(datatype))
    return DsfSaveFactory.savers[datatype]()