#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'fluentmock',
          version = '0.2.2',
          description = '''Fluent interface facade for Michael Foord's mock.''',
          long_description = '''|Logo| |Build Status|

Fluent interface facade for Michael Foord's Mock. \* Easy and readable
configuration of mock side effects. \* Configuration and verification
using matchers.

A example test using *fluentmock* and hamcrest: \`\`\`python from
fluentmock import UnitTests, when, verify from hamcrest import
assert\_that, equal\_to

class SeveralAnswersTests(UnitTests): def
test\_should\_return\_configured\_values\_in\_given\_order(self):

::

    when(targetpackage).targetfunction(2).then_return(1).then_return(2).then_return(3)

    assert_that(targetpackage.targetfunction(2), equal_to(1))
    assert_that(targetpackage.targetfunction(2), equal_to(2))
    assert_that(targetpackage.targetfunction(2), equal_to(3))

    verify(targetpackage).targetfunction(2)

\`\`\`

Documentation
-------------

-  `Comparing Mock and
   Fluentmock <https://github.com/aelgru/fluentmock/blob/master/docs/COMPARISON.md>`__
-  `Migrating from Mockito to
   Fluentmock <https://github.com/aelgru/fluentmock/blob/master/docs/MIGRATION.md>`__

Motivation
----------

... was to replace mockito with something that is as powerful as Mock.

.. |Logo| image:: https://raw.github.com/aelgru/fluentmock/master/docs/fluentmock-logo.png
   :target: https://pypi.python.org/pypi/fluentmock
.. |Build Status| image:: https://travis-ci.org/aelgru/fluentmock.png?branch=master
   :target: https://travis-ci.org/aelgru/fluentmock
''',
          author = "Michael Gruber",
          author_email = "aelgru@gmail.com",
          license = 'Apache License, Version 2.0',
          url = 'https://github.com/aelgru/fluentmock',
          scripts = [],
          packages = ['fluentmock'],
          classifiers = ['Development Status :: 3 - Alpha', 'Intended Audience :: Developers', 'License :: OSI Approved :: Apache Software License', 'Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 2.7', 'Programming Language :: Python :: 3', 'Programming Language :: Python :: 3.0', 'Programming Language :: Python :: 3.1', 'Programming Language :: Python :: 3.2', 'Programming Language :: Python :: 3.3', 'Topic :: Software Development :: Testing', 'Topic :: Software Development :: Quality Assurance'],
             #  data files
          package_data = {'fluentmock': ['LICENSE.txt']},   # package data
          install_requires = [ "mock" ],
          
          zip_safe=True
    )
