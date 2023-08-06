#! /usr/bin/env python
#-*- coding: utf-8 -*-
from setuptools import setup, find_packages
import sys, os

version = '0.1.3'

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

description = long_description = 'Control the Windows GUI'
try:
    with open('README', 'rb') as fp:
        long_description = fp.read()
except (OSError, IOError) as err:
    pass


setup(name='guippy',
      version=version,
      description=description,
      long_description=long_description,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: System Administrators',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Operating System :: Microsoft :: Windows',
          'Natural Language :: English',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.3',
          'Topic :: Office/Business',
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='TakesxiSximada',
      author_email='takesxi.sximada@gmail.com',
      url='https://bitbucket.org/takesxi_sximada/guippy',
      license='GPLv3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests', 'demo', 'scripts']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
