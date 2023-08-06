|Logo| |Build Status|

Fluent interface facade for Michael Foord's Mock. \* Easy and readable
configuration of mock side effects. \* Configuration and verification
using matchers.

A example test using *fluentmock* and hamcrest:

.. raw:: html

   <pre><code>from fluentmock import UnitTests, when, verify
   from hamcrest import assert_that, equal_to


   class SeveralAnswersTests(UnitTests):
     def test_should_return_configured_values_in_given_order(self):

       when(targetpackage).targetfunction(2).then_return(1).then_return(2).then_return(3)

       assert_that(targetpackage.targetfunction(2), equal_to(1))
       assert_that(targetpackage.targetfunction(2), equal_to(2))
       assert_that(targetpackage.targetfunction(2), equal_to(3))

       verify(targetpackage).targetfunction(2)</code></pre>

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


