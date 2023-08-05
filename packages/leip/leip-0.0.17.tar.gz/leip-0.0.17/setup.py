#!/usr/bin/env python

import sys
from setuptools import setup

DESCRIPTION = "Ultralightweight python CLI framework"


if sys.version < '3':
      package_dir = {'': 'src.2'}
else:
      package_dir = {'': 'src.3'}

entry_points = {
    'console_scripts': [
        'leip = leip.cli:dispatch'
        ]}

setup(name='leip',
      version='0.0.17',
      description=DESCRIPTION,
      author='Mark Fiers',
      entry_points = entry_points,
      author_email='mark.fiers.42@gmail.com',
      url='http://mfiers.github.com/Leip',
      packages=['leip'],
      include_package_data=True,
      package_dir=package_dir,
      requires=[
          'Yaco (>=0.1.26)',
      ],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.3',
      ]
    )
