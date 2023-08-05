#!/usr/bin/env python

import os
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

# # ext_modules = [Extension("", ["pyprophet/_optimized.c"])]
ext_modules = [Extension("msproteomicstoolslib/format._optimized",
                     ["msproteomicstoolslib/format/_optimized.pyx"],
                     language='c++',
                     )]

"""
all_scripts = [
    "analysis/alignment/feature_alignment.py",
    "analysis/alignment/requantAlignedValues.py",
    "analysis/alignment/compute_full_matrix.py",
              ]
"""

import fnmatch
all_scripts = []
for root, dirnames, filenames in os.walk('analysis'):
  for filename in fnmatch.filter(filenames, '*.py'):
      all_scripts.append(os.path.join(root, filename))

setup(name='msproteomicstools',
      version='0.1.0',
      packages = ['msproteomicstoolslib', 
                  "msproteomicstoolslib.algorithms",
                  "msproteomicstoolslib.algorithms.alignment",
                  "msproteomicstoolslib.data_structures",
                  "msproteomicstoolslib.format",
                  "msproteomicstoolslib.math",
                  "msproteomicstoolslib.util",
                  "openswathgui",
                  "openswathgui.models",
                  "openswathgui.views",
                 ],
      package_dir = {
          'openswathgui': 'gui/openswath',
          #'msproteomicstools/math': 'msproteomicstoolslib/math',
      },
      scripts=all_scripts,
      # package_data={'msproteomicstools': ['obo/*.obo']},
      # packages=find_packages(exclude=['ez_setup',
      #                                 'examples', 'tests']),
      #include_package_data=True,
      description='Tools for MS-based proteomics',
      long_description='msproteomicstools - python module for MS-based proteomics',
      url='https://code.google.com/p/msproteomicstools',
      license='Modified BSD',
      platforms='any that supports python 2.7',
      classifiers=[
      'Environment :: Console',
      'Intended Audience :: Science/Research',
      'License :: OSI Approved :: BSD License',
      'Operating System :: OS Independent',
      'Topic :: Scientific/Engineering :: Bio-Informatics',
      'Topic :: Scientific/Engineering :: Chemistry',
      ],
      # install_requires= TODO
      test_suite="nose.collector",
      tests_require="nose",
      )

      # ext_modules = ext_modules,
      # cmdclass = {'build_ext': build_ext},

