#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'committer',
          version = '0.2.0',
          description = 'Unified command line interface for git, mercurial and subversion.',
          long_description = '''Please visit https://github.com/aelgru/committer for more information!''',
          author = "Michael Gruber",
          author_email = "aelgru@gmail.com",
          license = 'Apache License, Version 2.0',
          url = 'https://github.com/aelgru/committer',
          scripts = ['ci', 'up', 'st'],
          packages = ['committer', 'committer.vcsclients'],
          classifiers = ['Development Status :: 4 - Beta', 'Environment :: Console', 'Intended Audience :: Developers', 'License :: OSI Approved :: Apache Software License', 'Programming Language :: Python', 'Topic :: Software Development :: User Interfaces', 'Topic :: Software Development :: Version Control', 'Topic :: Utilities'],
             #  data files
          package_data = {'committer': ['LICENSE.txt']},   # package data
          
          
          zip_safe=True
    )
