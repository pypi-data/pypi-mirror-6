'''
Created on Jan 14, 2014

@author: Jose Borreguero
'''

from logger import vlog
from abc import ABCMeta, abstractmethod


class DsfLoader(object):
  '''
  Abstract class for dynamic structure factor loaders
  '''
  __metaclass__ = ABCMeta

  def __init__(self):
    '''
    Constructor
    '''
    self.datatype = None

  @abstractmethod
  def Load(self, container):
    ''' This method must be implemented on every subclass '''
    pass


class DsfLoaderMantidWorkspace2D(DsfLoader):
  ''' This class implements a loader from a Mantid Workspace2D '''

  def __init__(self):
    self.datatype='mantid::Workspace2D'

  def Load(self, ws):
    try:
      intensities = ws.extractY()
      errors = ws.extractE()
      if not errors.any():
        errors = None # set errors to None if all errors are zero
      return intensities, errors
    except:
      raise TypeError

class DsfLoaderMantidNexusFile(DsfLoader):
  ''' This class implements a loader from a Mantid Nexus file containing
  one Mantid Workspace2D '''

  def __init__(self):
    self.datatype='mantid::NexusFile'

  def Load(self, filename):

    try:
      from mantid.simpleapi import LoadNexus
    except ImportError:
      vlog.error('mantid library not found!')
      raise ImportError

    try:
      workspace = LoadNexus(filename)
    except:
      raise TypeError

    loader = DsfLoaderMantidWorkspace2D()
    return loader.Load(workspace)

class DsfLoaderFactory(object):

  loaders = {'mantid::Workspace2D':DsfLoaderMantidWorkspace2D,
             'mantid::NexusFile':DsfLoaderMantidNexusFile,
             }

  def __init__(self):
    pass

  @property
  def datatypes(self):
    ''' Handy property returning the data types '''
    return DsfLoaderFactory.loaders.keys()

  def Instantiate(self, datatype):
    ''' Instantiate a dynamic structure factor loader of appropriate type '''
    if datatype not in self.datatypes:
      vlog.error('No dynamic structure factor loader for type {0}'.format(datatype))
    return DsfLoaderFactory.loaders[datatype]()