#!/usr/bin/env python
from setuptools import setup, find_packages

from accounts import VERSION


setup(name='django-account-balances',
      version=VERSION,
      author="Jason Carver",
      author_email="jason@membright.com",
      description="Track account credits in Django",
      long_description=open('README.md').read(),
      license=open('LICENSE').read(),
      packages=find_packages(exclude=['sandbox*', 'tests*']),
      include_package_data=True,
      # See http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: Unix',
          'Programming Language :: Python'],
      install_requires=[
          'python-dateutil>=2.1,<2.2',
          'django-treebeard>=2.0b2',
          ])
