#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'fluentmock',
          version = '0.1.12',
          description = '''Fluent interface for mock.''',
          long_description = '''Please visit https://github.com/aelgru/fluentmock for more information!''',
          author = "Michael Gruber",
          author_email = "aelgru@gmail.com",
          license = 'Apache License, Version 2.0',
          url = 'https://github.com/aelgru/fluentmock',
          scripts = [],
          packages = ['fluentmock'],
          classifiers = ['Development Status :: 1 - Planning', 'Intended Audience :: Developers', 'License :: OSI Approved :: Apache Software License', 'Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 2.7', 'Programming Language :: Python :: 3', 'Programming Language :: Python :: 3.0', 'Programming Language :: Python :: 3.1', 'Programming Language :: Python :: 3.2', 'Programming Language :: Python :: 3.3', 'Topic :: Software Development :: Testing', 'Topic :: Software Development :: Quality Assurance'],
             #  data files
          package_data = {'fluentmock': ['LICENSE.txt']},   # package data
          install_requires = [ "mock" ],
          
          zip_safe=True
    )
