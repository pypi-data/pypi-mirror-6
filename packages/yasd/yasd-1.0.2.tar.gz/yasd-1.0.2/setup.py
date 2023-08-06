#!/usr/bin/env python

from setuptools import setup

setup(name='yasd',
      version='1.0.2',
      description='Yet Another Syslog Daemon',
      author='Nikolay Bryskin',
      author_email='devel.niks@gmail.com',
      url='https://github.com/nikicat/yasd',
      packages=['yasd'],
      install_requires=['cffi', 'pyelasticsearch', 'pyyaml', 'graphitesend'],
      scripts=['scripts/yasd'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 3',
          'Topic :: System :: Networking :: Monitoring',
      ]
     )
