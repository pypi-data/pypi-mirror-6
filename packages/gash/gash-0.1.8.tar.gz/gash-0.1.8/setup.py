from setuptools import setup, find_packages
import sys, os

version = '0.1.8'

setup(name='gash',
      version=version,
      description="gash client in python",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='dantezhu',
      author_email='zny2008@gmail.com',
      url='https://github.com/dantezhu/gash',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'xmltodict',
          'pycrypto',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
