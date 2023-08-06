``drippy`` README
=================

This package provides a plugin for `nose <http://pypi.python.org/pypi/nose>`_
which reports tempfile leaks during test runs.

For example::

  $ /path/to/nosetests --with-drippy
  .......................
     test_some_feature (yourpackage.tests.FeatureTests) -- before: 0, after: 1
  
    Featuretests -- before: 0, after: 1
  ...........
   yourpackage.tests -- before: 0, after 1

  yourpackage -- before: 0, after: 1
  
  ----------------------------------------------------------------------
  Ran 34 tests in 0.243s
