========
 DocSix
========

.. image:: https://travis-ci.org/nyergler/docsix.png?branch=master
   :target: https://travis-ci.org/nyergler/docsix

*DocSix* is a tool which helps you run your doctests_ under both
Python 2 and Python 3 (specifically 3.3 and later).

DocSix works by stripping unicode indicators from expected test output
before running the test on Python 3.

To use DocSix, simply pass it the list of files to execute tests on::

  >>> import unittest
  >>> from docsix import get_doctest_suite
  >>> suite = get_doctest_suite(['testdoc.rst'])
  >>> unittest.TextTestRunner(verbosity=2).run(suite)
  <unittest.runner.TextTestResult run=1 errors=0 failures=0>


.. _doctests: http://docs.python.org/2/library/doctest.html
