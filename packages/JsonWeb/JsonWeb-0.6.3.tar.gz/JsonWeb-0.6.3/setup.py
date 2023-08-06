import os
from setuptools import setup, find_packages

version = '0.6.3'

if os.path.exists("README.rst"):
    long_description = open("README.rst").read()
else:
    long_description = "See http://www.jsonweb.net/en/latest"

setup(name='JsonWeb',
      version=version,
      description="Package for building json de/serialization of your data models in a web app.",
      long_description=long_description,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Shawn Adams',
      author_email='',
      url='',
      license='BSD',
      packages=find_packages(exclude=['examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
