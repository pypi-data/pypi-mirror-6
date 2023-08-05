from setuptools import setup, find_packages
import sys, os

version = '0.2.1'

setup(name='backend',
      version=version,
      description="Backend Utility Tools",
      long_description="""\
Backend Utility Tools for Python Django""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='django backend',
      author='Vibhaj Rajan',
      author_email='vibhaj8@gmail.com',
      url='http://vibhaj.com/',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
