#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(name='tds7xx',
      version='1.0.0',
      description='HP TDS4xx Series GPIB Driver',
      url='',
      author='ElectroOptical Innovations, LLC.',
      author_email='simon.hobbs@electrooptical.net',
      license='BSD',
      packages=[],
      #packages=find_packages(),
      install_requires=[
          'prologix-gpib-ethernet',
          'click',
          'pyserial',
          'numpy',
          'timeout_decorator'
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      scripts=["bin/tektronix-tds-7xx.py"],
      include_package_data=True,
      zip_safe=True)
