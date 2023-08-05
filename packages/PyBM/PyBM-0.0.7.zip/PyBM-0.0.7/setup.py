#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='PyBM',
      version='0.0.7',
      description='Python Build Monitor',
      author='Jos Hendriks',
      packages=find_packages(exclude=('*test','*test.*',)),
      package_dir={'pybm': 'pybm'},
      package_data={'pybm': ['logging.conf', 'segoeui.ttf'],
                    '': ['..\\LICENSE', '..\\NOTICE']},
      url='http://www.circuitdb.com/',
      install_requires=[
        'pytz',
        'requests',
      ],
    )