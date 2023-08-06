'''
Created on Jan 15, 2014

@author: Jose Borreguero
'''


from setuptools import setup

setup(
  name = 'dsfinterp',
  packages = ['dsfinterp','dsfinterp/test' ],
  version = '0.1',
  description = 'Cubic Spline Interpolation of Dynamics Structure Factors',
  long_description = open('README.md').read(),
  author = 'Jose Borreguero',
  author_email = 'jose@borreguero.com',
  url = 'https://github.com/camm-sns/dsfinterp',
  download_url = 'http://pypi.python.org/pypi/dsfinterp',
  keywords = ['AMBER', 'mdend', 'energy', 'molecular dynamics'],
  classifiers = [
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Development Status :: 4 - Beta',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Topic :: Scientific/Engineering :: Physics',
    ],
)
