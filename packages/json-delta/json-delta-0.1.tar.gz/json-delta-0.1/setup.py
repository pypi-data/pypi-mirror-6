#!/usr/bin/env python

from distutils.core import setup

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import json_delta

setup(name='json-delta',
      version=json_delta.__VERSION__,
      description='A diff/patch pair and library for JSON data structures.',
      author='Phil Roberts',
      author_email='himself@phil-roberts.name',
      url='http://www.phil-roberts.name/json_delta',
      py_modules=['json_delta', 'needle'],
      scripts=['src/scripts/json_diff', 
               'src/scripts/json_patch',
               'src/scripts/json_cat'],
      package_dir={'': 'src'},
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3'
        ]                
      )
