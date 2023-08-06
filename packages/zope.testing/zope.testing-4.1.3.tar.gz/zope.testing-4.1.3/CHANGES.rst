zope.testing Changelog
**********************

4.1.3 (2014-03-19)
==================

- Added support for Python 3.4.

- Updated ``boostrap.py`` to version 2.2.


4.1.2 (2013-02-19)
==================

- Adjusted Trove classifiers to reflect the currently supported Python
  versions. Officially drop Python 2.4 and 2.5. Added Python 3.3.

- LP: #1055720: Fix failing test on Python 3.3 due to changed exception
  messaging.

4.1.1 (2012-02-01)
==================

- Fixed: Windows test failure.

4.1.0 (2012-01-29)
==================

- Added context-manager support to ``zope.testing.setupstack``

- Made ``zope.testing.setupstack`` usable with all tests, not just
  doctests and added ``zope.testing.setupstack.globs``, which makes it
  easier to write test setup code that workes with doctests and other
  kinds of tests.

- Added the ``wait`` module, which makes it easier to deal with
  non-deterministic timing issues.

- Renamed ``zope.testing.renormalizing.RENormalizing`` to
  ``zope.testing.renormalizing.OutputChecker``. The old name is an
  alias.

- Updated tests to run with Python 3.

- More clearly labeled which features were supported by Python 3.

- Reorganized documentation.

4.0.0 (2011-11-09)
==================

- Removes the deprecated zope.testing.doctest.

- Adds Python 3 support.

- Fixed test which fails if there is a file named `Data.fs` in the current
  working directory.


3.10.2 (2010-11-30)
===================

- Fix test of broken symlink handling to not break on Windows.


3.10.1 (2010-11-29)
===================

- Fix removal of broken symlinks on Unix.


3.10.0 (2010-07-21)
===================

- Removed zope.testing.testrunner, which now is moved to zope.testrunner.

- Update fix for LP #221151 to a spelling compatible with Python 2.4.

3.9.5 (2010-05-19)
==================

- LP #579019: When layers were run in parallel, their tearDown was not
  called. Additionally, the first layer which was run in the main
  thread did not have it's tearDown called either.

- Deprecated zope.testing.testrunner and zope.testing.exceptions. They have
  been moved to a separate zope.testrunner module, and will be removed from
  zope.testing in 4.0.0, together with zope.testing.doctest.

3.9.4 (2010-04-13)
==================

- LP #560259: Fix subunit output formatter to handle layer setup
  errors.

- LP #399394:  Added a ``--stop-on-error`` / ``--stop`` / ``-x`` option to
  the testrunner.

- LP #498162:  Added a ``--pdb`` alias for the existing ``--post-mortem``
  / ``-D`` option to the testrunner.

- LP #547023:  Added a ``--version`` option to the testrunner.

- Added tests for LP #144569 and #69988.

  https://bugs.launchpad.net/bugs/69988

  https://bugs.launchpad.net/zope3/+bug/144569


3.9.3 (2010-03-26)
==================

- zope.testing.renormalizer no longer imports zope.testing.doctest, which
  caused deprecation warnings.

- Fix testrunner-layers-ntd.txt to suppress output to sys.stderr.

- Suppress zope.testing.doctest deprecation warning when running
  zope.testing's own test suite.


3.9.2 (2010-03-15)
==================

- Fixed broken ``from zope.testing.doctest import *``

3.9.1 (2010-03-15)
==================

- No changes; reuploaded to fix broken 3.9.0 release on PyPI.

3.9.0 (2010-03-12)
==================

- Modified the testrunner to use the standard Python doctest module instead of
  the deprecated zope.testing.doctest.

- Fix testrunner-leaks.txt to use the run_internal helper, so that
  sys.exit() isn't triggered during the test run.

- Added support for conditionally using a subunit-based output
  formatter upon request if subunit and testtools are available. Patch
  contributed by Jonathan Lange.

3.8.7 (2010-01-26)
==================

- Downgraded the zope.testing.doctest deprecation warning into a
  PendingDeprecationWarning.

3.8.6 (2009-12-23)
==================

- Added MANIFEST.in and reuploaded to fix broken 3.8.5 release on PyPI.


3.8.5 (2009-12-23)
==================

- Added DocFileSuite, DocTestSuite, debug_src and debug back BBB imports
  back into zope.testing.doctestunit; apparently many packages still import
  them from there!

- Made zope.testing.doctest and zope.testing.doctestunit emit deprecation
  warnings: use the stdlib doctest instead.


3.8.4 (2009-12-18)
==================

- Fixed missing imports and undefined variables reported by pyflakes,
  adding tests to exercise the blind spots.

- Cleaned up unused imports reported by pyflakes.

- Added two new options to generate randomly ordered list of tests and to
  select a specific order of tests.

- RENormalizing checkers can be combined via ``+`` now:
  ``checker1 + checker2`` creates a checker with the transformations of both
  checkers.

- Test fixes for Python 2.7.

3.8.3 (2009-09-21)
==================

- Avoid a split() call or we get test failures when running from a directory
  with spaces in it.

- Fix testrunner behavior on Windows for -j2 (or greater) combined with -v
  (or greater).

3.8.2 (2009-09-15)
==================

- Removing hotshot profiler when using Python 2.6. That makes zope.testing
  compatible with Python 2.6


3.8.1 (2009-08-12)
==================

- Avoid hardcoding sys.argv[0] as script;
  allow, for instance, Zope 2's `bin/instance test` (LP#407916).

- Produce a clear error message when a subprocess doesn't follow the
  zope.testing.testrunner protocol (LP#407916).

- Do not unnecessarily squelch verbose output in a subprocess when there are
  not multiple subprocesses.

- Do not unnecessarily batch subprocess output, which can stymie automated and
  human processes for identifying hung tests.

- Include incremental output when there are multiple subprocesses and a
  verbosity of -vv or greater is requested.  This again is not batched,
  supporting automated processes and humans looking for hung tests.


3.8.0 (2009-07-24)
==================

- Testrunner automatically picks up descendants of unittest.TestCase in test
  modules, so you don't have to provide a test_suite() anymore.


3.7.7 (2009-07-15)
==================

- Clean up support for displaying tracebacks with supplements by turning it
  into an always-enabled feature and making the dependency on zope.exceptions
  explicit.

- Fix #251759: Test runner descended into directories that aren't Python
  packages.

- Code cleanups.


3.7.6 (2009-07-02)
==================

- Add zope-testrunner console_scripts entry point. This exposes a
  zope-testrunner binary with default installs allowing the testrunner to be
  run from the command line.

3.7.5 (2009-06-08)
==================

- Fix bug when running subprocesses on Windows.

- The option REPORT_ONLY_FIRST_FAILURE (command line option "-1") is now
  respected even when a doctest declares its own REPORTING_FLAGS, such as
  REPORT_NDIFF.

- Fixed bug that broke readline with pdb when using doctest
  (see http://bugs.python.org/issue5727).

- Made tests pass on Windows and Linux at the same time.


3.7.4 (2009-05-01)
==================

- Filenames of doctest examples now contain the line number and not
  only the example number. So a stack trace in pdb tells the exact
  line number of the current example. This fixes
  https://bugs.launchpad.net/bugs/339813

- Colorization of doctest output correctly handles blank lines.


3.7.3 (2009-04-22)
==================

- Better deal with rogue threads by always exiting with status so even
  spinning daemon threads won't block the runner from exiting. This deprecated
  the ``--with-exit-status`` option.


3.7.2 (2009-04-13)
==================

- fix test failure on Python 2.4 because of slight difference in the way
  coverage is reported (__init__ files with only a single comment line are now
  not reported)
- fixed bug that caused the test runner to hang when running subprocesses (as a
  result Python 2.3 is no longer supported).
- there is apparently a bug in Python 2.6 (related to
  http://bugs.python.org/issue1303673) that causes the profile tests to fail.
- added explanitory notes to buildout.cfg about how to run the tests with
  multiple versions of Python


3.7.1 (2008-10-17)
==================

- The setupstack temporary-directory support now properly handles
  read-only files by making them writable before removing them.


3.7.0 (2008-09-22)
==================

- Added an alterate setuptools / distutils commands for running all tests
  using our testrunner.  See 'zope.testing.testrunner.eggsupport:ftest'.

- Added a setuptools-compatible test loader which skips tests with layers:
  the testrunner used by 'setup.py test' doesn't know about them, and those
  tests then fail.  See 'zope.testing.testrunner.eggsupport:SkipLayers'.

- Added support for Jython, when a garbage collector call is sent.

- Added support to bootstrap on Jython.

- Fixed NameError in StartUpFailure.

- Open doctest files in universal mode, so that packages released on Windows
  can be tested on Linux, for example.


3.6.0 (2008/07/10)
==================

- Added -j option to parallel tests run in subprocesses.

- RENormalizer accepts plain Python callables.

- Added --slow-test option.

- Added --no-progress and --auto-progress options.

- Complete refactoring of the test runner into multiple code files and a more
  modular (pipeline-like) architecture.

- Unified unit tests with the layer support by introducing a real unit test
  layer.

- Added a doctest for ``zope.testing.module``. There were several bugs
  that were fixed:

  * ``README.txt`` was a really bad default argument for the module
    name, as it is not a proper dotted name. The code would
    immediately fail as it would look for the ``txt`` module in the
    ``README`` package. The default is now ``__main__``.

  * The tearDown function did not clean up the ``__name__`` entry in the
    global dictionary.

- Fix a bug that caused a SubprocessError to be generated if a subprocess
  sent any output to stderr.

- Fix a bug that caused the unit tests to be skipped if run in a subprocess.


3.5.1 (2007/08/14)
==================

Bugs Fixed:
-----------

- Post-mortem debugging wasn't invoked for layer-setup failures.

3.5.0 (2007/07/19)
==================

New Features
------------

- The test runner now works on Python 2.5.

- Added support for cProfile.

- Added output colorizing (-c option).

- Added --hide-secondary-failures and --show-secondary-failures options
  (https://bugs.launchpad.net/zope3/+bug/115454).

Bugs Fixed:
-----------

- Fix some problems with Unicode in doctests.

- Fix "Error reading from subprocess" errors on Unix-like systems.

3.4 (2007/03/29)
================

New Features
------------

- Added exit-with-status support (supports use with buildbot and
  zc.recipe.testing)

- Added a small framework for automating set up and tear down of
  doctest tests. See setupstack.txt.

Bugs Fixed:
-----------

- Fix testrunner-wo-source.txt and testrunner-errors.txt to run with a
  read-only source tree.

3.0 (2006/09/20)
================

- Updated the doctest copy with text-file encoding support.

- Added logging-level support to loggingsuppport module.

- At verbosity-level 1, dots are not output continuously, without any
  line breaks.

- Improved output when the inability to tear down a layer causes tests
  to be run in a subprocess.

- Made zope.exception required only if the zope_tracebacks extra is
  requested.

2.x.y (???)
===========

- Fix the test coverage. If a module, for example `interfaces`, was in an
  ignored directory/package, then if a module of the same name existed in a
  covered directory/package, then it was also ignored there, because the
  ignore cache stored the result by module name and not the filename of the
  module.

2.0 (2006/01/05)
================

- Corresponds to the version of the zope.testing package shipped as part of
  the Zope 3.2.0 release.
