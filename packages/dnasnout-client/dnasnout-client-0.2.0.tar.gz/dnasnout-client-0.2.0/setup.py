import sys
if (sys.version_info[0] < 3) or (sys.version_info[0] == 3 and sys.version_info[1] < 3):
    print("Python 3.3 required")
    sys.exit(1)

import os    
from setuptools import setup

from src import __version__


packname = 'dnasnout_client'
srcpath = 'src'


with open('README.rst', 'r') as fh:
    long_description = fh.read()

setup(name='dnasnout-client',
      version=__version__,
      install_requires=['ngs_plumbing>=0.13.0',],
      description='DNASnout client',
      long_description=long_description,
      author='Laurent Gautier',
      author_email='lgautier@gmail.com',
      url='http://www.cbs.dtu.dk/~laurent/dnasnout',
      package_dir = {packname: srcpath},
      packages = [packname,],
      classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'],
      package_data = {packname: ['LICENSE*.txt']},
      #data_files = ['./LICENSE.txt', './LICENSE_AGPL.txt'],
      license='This software is available under a dual license model: the AGPLv3 or a commercial license. If you need a commercial license, contact the author.'
)
