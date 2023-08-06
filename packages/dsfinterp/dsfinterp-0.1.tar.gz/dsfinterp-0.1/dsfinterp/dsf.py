'''
Created on Jan 7, 2014

@author: Jose Borreguero
'''

from logger import vlog, tr
import numpy

class Dsf(object):
  '''
  This class implements a dynamic structure factor
  '''

  def __init__(self):
    '''
    Attributes:
      fvalue: value of the external parameter
      intensities: actual values of the structure factor
      errors: associated errors of the intensities. Mostly for experimentally-derived data
      shape: shape of the intensities array
    '''
    self.fvalue = None
    self.intensities = None
    self.errors = None

  @property
  def shape(self):
    return self.intensities.shape

  def ExtractIntensity(self, index ):
    return self.intensities.ravel()[ index ]

  def ExtractError(self, index ):
    if self.errors is not None:
      return self.errors.ravel()[ index ]
    else:
      return None

  def SetFvalue(self,fvalue):
    self.fvalue = fvalue

  def SetIntensities(self,intensities):
    self.intensities = numpy.array(intensities)

  def SetErrors(self,errors):
    if self.intensities is None:
      vlog.error('Error: Set intensities before setting errors')
      return
    if numpy.array(errors).shape != self.intensities.shape:
      vlog.error('Error: shape of errors different than shape of intensities')
      return
    self.errors = numpy.array(errors)

  def Load(self, container, datatype=None):
    ''' Load intensities and errors from an object or reference.
    
    Iterates over all data loaders until it finds an appropriate loader
    
    Arguments:
      [datatype]: one of the DsfLoad types registered in DsfLoaderFactory
    
    Returns:
      intensities array loaded from the data
    
    Exceptions:
      TypeError is data cannot be loaded
    '''
    from dsfload import DsfLoaderFactory
    loader_factory = DsfLoaderFactory()
    datatypes = [datatype,] if datatype else loader_factory.datatypes
    for datatype in datatypes:
      try:
        loader = loader_factory.Instantiate(datatype)
        self.intensities, self.errors = loader.Load(container)
        return self.intensities # stop iteration over loaders
      except Exception, e:
        pass
    vlog.error('Appropriate loader not found for supplied data')
    raise TypeError

  def Save(self, container, datatype=None):
    ''' Save intensities and errors to a container
    
    Iterates over all data savers until it finds appropiate saver
    
    Arguments:
      [datatype]: one of the DsfSave types registered in DsfSaverFactory
    
    Returns:
      first successful datatype
    
    Exceptions:
      TypeError if container and datatype don't agree
    '''
    from dsfsave import DsfSaveFactory
    save_factory = DsfSaveFactory()
    datatypes = [datatype,] if datatype else save_factory.datatypes
    for datatype in datatypes:
      try:
        saver = save_factory.Instantiate(datatype)
        saver.Save(self, container)
        return datatype
      except Exception, e:
        pass
    vlog.error('Appropriate loader not found for supplied data')
    raise TypeError