====================
NEWS about uci-tests
====================

Overview of changes to uci-tests in reverse chronological order.

0.0.9
=====

* runners.RunTestsArgParser can be subclassed.

* import errors give a better traceback revealing where they happen (instead
  of inside ucitests which was a poor UI).

* /!\ Incompatible change: NameMatcher has been moved from loaders to
  matchers.

* /!\ Incompatible change: TestPep8 and TestPyflakes have been moved from
  ucitests.tests.test_style to ucitests.styles.

* provide a walker.Walker class that can filter a file system tree and call
  a handler for each file or directory.

0.0.8
=====

* add the tests themselves to the installed packages (so dep8 can use them
  and test_style can be used by other projects).

* disable tests that requires recent versions for testtools, pep8 and
  pyflakes so most of the package can be dep8 tested on precise.

0.0.7
=====

* allow tests to be loaded from importable modules with -m MODULE.

* provide a Loader.packageSysPathFromName convenience method to find where a
  package is imported from.


0.0.6
=====

* add pyflakes support in test_style.


0.0.5
=====

 * add features.py with ExecutableFeature as an example.

 * add a features.requires decorator to skip tests when a feature is not
   available.

 * make assertSuccessfullTest part of assertions.py.

0.0.4
=====

 * revert to python2 to match current needs.


0.0.3
=====

 * add assertions.assertLength to check the length of an iterable and
   display it when the length is wrong.

 * add fixtures.isolate_env to isolate tests from os.environ.


0.0.2
=====

New release to fix packaging issues.


0.0.1
=====

First release.
