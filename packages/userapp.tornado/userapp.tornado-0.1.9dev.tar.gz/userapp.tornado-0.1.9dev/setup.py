from setuptools import setup, find_packages
import sys, os

version = '0.1.9'

setup(name='userapp.tornado',
      version=version,
      description="UserApp support for Tornado.",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='tornado userapp',
      author='Robin Orheden',
      author_email='robin.orheden@userapp.io',
      url='https://github.com/userapp-io/userapp-tornado',
      license='MIT',
      namespace_packages = ['userapp'],
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      install_requires = ['setuptools', 'userapp'],
      include_package_data=True,
      zip_safe=False,
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
