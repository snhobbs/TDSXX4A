#!/usr/bin/env python3
from setuptools import setup, find_packages

with open("README.md", 'r') as f:
    description = f.read()


with open("requirements.txt", 'r') as f:
    requirements = f.readlines()


setup(name='tdsxx4a',
      version='1.0.0',
      description='HP TDS4xx4a Series GPIB Driver',
      long_description = description,
      url='',
      author='ElectroOptical Innovations, LLC.',
      author_email='simon.hobbs@electrooptical.net',
      license='BSD',
      packages=find_packages(),
      install_requires=requirements,
      test_suite='nose.collector',
      tests_require=['nose'],
      scripts=["bin/tektronix-tds-7xx.py"],
      include_package_data=True,
      zip_safe=True)
