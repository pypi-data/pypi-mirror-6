#!/usr/bin/env python

from distutils.core import setup

setup(name='gammacap',
      version='0.9.0',
      description='Gamma Ray Cluster Analysis Package',
      author='Eric Carlson',
      author_email='erccarls@ucsc.edu',
      url='http://planck.ucsc.edu',
      keywords=['Requires: numpy','Requires: scikit-learn','Requires: pyfits'], 
      package_dir = {'': './'},
      packages = ['Stats','BGTools']
     )