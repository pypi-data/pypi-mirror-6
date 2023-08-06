# This file is part of the Ubuntu Continuous Integration test tools
#
# Copyright 2013, 2014 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3, as published by the
# Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranties of MERCHANTABILITY,
# SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

from cStringIO import StringIO
import io
import unittest


import subunit


from ucitests import (
    assertions,
    features,
    fixtures,
    results,
    runners,
    tests,
)


class TestCliRun(unittest.TestCase):
    "Smoke blackbox tests."""

    def setUp(self):
        super(TestCliRun, self).setUp()
        fixtures.setup_for_local_imports(self)
        self.out = StringIO()
        self.err = StringIO()

    def test_run_no_tests_errors(self):
        ret = runners.cli_run(['no-such-test'],
                              stdout=self.out, stderr=self.err)
        self.assertEqual(1, ret)

    def test_list_no_tests_errors(self):
        ret = runners.cli_run(['-l', 'no-such-test'],
                              stdout=self.out, stderr=self.err)
        self.assertEqual(1, ret)
        self.assertEqual('', self.out.getvalue())
        self.assertEqual('', self.err.getvalue())


class TestListTests(unittest.TestCase):

    def setUp(self):
        super(TestListTests, self).setUp()
        fixtures.setup_for_local_imports(self)

    def list_tests(self, kinds):
        suite = fixtures.make_suite(kinds)
        out = StringIO()
        ret = runners.list_tests(suite, out)
        return ret, out.getvalue().splitlines()

    def test_no_tests_return_1(self):
        ret, test_names = self.list_tests([])
        self.assertEqual(1, ret)
        self.assertEqual([], test_names)

    def assertTestNames(self, expected, kinds):
        ret, actual = self.list_tests(kinds)
        self.assertEqual(0, ret)
        self.assertEqual(expected, actual)

    def test_single(self):
        self.assertTestNames(['ucitests.fixtures.Test.test_pass'],
                             ['pass'])

    def test_several(self):
        self.assertTestNames(['ucitests.fixtures.Test.test_pass',
                              'ucitests.fixtures.Test.test_fail',
                              'ucitests.fixtures.Test.test_skip'],
                             ['pass', 'fail', 'skip'])


class TestRunTests(unittest.TestCase):

    def setUp(self):
        super(TestRunTests, self).setUp()
        fixtures.setup_for_local_imports(self)

    def run_tests(self, kinds):
        suite = fixtures.make_suite(kinds)
        result = results.TextResult(StringIO())
        ret = runners.run_tests(suite, result)
        return ret

    def test_pass(self):
        self.assertEqual(0, self.run_tests(['pass']))

    def test_fail(self):
        self.assertEqual(1, self.run_tests(['fail']))

    def test_skip(self):
        self.assertEqual(0, self.run_tests(['skip']))


class TestRunTestsTextOutput(unittest.TestCase):

    def setUp(self):
        super(TestRunTestsTextOutput, self).setUp()
        fixtures.setup_for_local_imports(self)

    def assertOutput(self, expected, kinds, result=None):
        suite = fixtures.make_suite(kinds)
        if result is None:
            result = results.TextResult(StringIO(), verbosity=2)
        runners.run_tests(suite, result)
        assertions.assertMultiLineAlmostEqual(self, expected,
                                              result.stream.getvalue())

    def test_pass(self):
        self.assertOutput('''Tests running...
ucitests.fixtures.Test.test_pass ... OK (... secs)

Ran 1 test in ...s
OK
''',
                          ['pass'])

    def test_fail(self):
        self.assertOutput('''Tests running...
ucitests.fixtures.Test.test_fail ... FAIL (... secs)
======================================================================
FAIL: ucitests.fixtures.Test.test_fail
----------------------------------------------------------------------
Traceback (most recent call last):
  File ..., in test_fail
    raise self.failureException
AssertionError

Ran 1 test in ...s
FAILED (failures=1)
''',
                          ['fail'])

    def test_skip(self):
        self.assertOutput('''Tests running...
ucitests.fixtures.Test.test_skip ... SKIP (... secs)

Ran 1 test in ...s
OK
''',
                          ['skip'])

    @features.requires(tests.minimal_testtools)
    def test_fail_fast(self):
        result = results.TextResult(StringIO(), verbosity=2, failfast=True)
        self.assertOutput('''Tests running...
ucitests.fixtures.Test.test_fail ... FAIL (... secs)
======================================================================
FAIL: ucitests.fixtures.Test.test_fail
----------------------------------------------------------------------
Traceback (most recent call last):
  File ..., in test_fail
    raise self.failureException
AssertionError

Ran 1 test in ...s
FAILED (failures=1)
''',
                          ['fail', 'pass'], result=result)


class TestRunTestsSubunitOutput(unittest.TestCase):

    def setUp(self):
        super(TestRunTestsSubunitOutput, self).setUp()
        fixtures.setup_for_local_imports(self)

    def assertOutput(self, expected, kinds, result=None):
        suite = fixtures.make_suite(kinds)
        if result is None:
            if tests.minimal_testtools.available():
                stream = io.BytesIO()
            else:
                stream = StringIO()
            result = subunit.TestProtocolClient(stream)
        runners.run_tests(suite, result)
        actual = result._stream.getvalue().decode('utf8')
        assertions.assertMultiLineAlmostEqual(self, expected, actual)

    def test_pass(self):
        self.assertOutput('''test: ucitests.fixtures.Test.test_pass
successful: ucitests.fixtures.Test.test_pass
''',
                          ['pass'])

    def test_fail(self):
        self.assertOutput('''test: ucitests.fixtures.Test.test_fail
failure: ucitests.fixtures.Test.test_fail [
Traceback (most recent call last):
  File ..., in test_fail
    raise self.failureException
AssertionError
]
''',
                          ['fail'])

    def test_skip(self):
        self.assertOutput('''test: ucitests.fixtures.Test.test_skip
skip: ucitests.fixtures.Test.test_skip [

]
''',
                          ['skip'])

    @features.requires(tests.minimal_testtools)
    def test_fail_fast(self):
        result = subunit.TestProtocolClient(io.BytesIO())
        result.failfast = True
        self.assertOutput('''test: ucitests.fixtures.Test.test_fail
failure: ucitests.fixtures.Test.test_fail [
Traceback (most recent call last):
  File ..., in test_fail
    raise self.failureException
AssertionError
]
''',
                          ['fail', 'pass'], result=result)


class TestOptionParsing(unittest.TestCase):

    def setUp(self):
        super(TestOptionParsing, self).setUp()
        self.out = StringIO()
        self.err = StringIO()

    def parse_args(self, args):
        ns = runners.RunTestsArgParser().parse_args(args, self.out, self.err)
        return ns

    def test_help(self):
        with self.assertRaises(SystemExit):
            self.parse_args(['-h'])
        self.maxDiff = None
        assertions.assertMultiLineAlmostEqual(self, '''\
usage: uci-run-tests [-h] [--module MODULE] [--exclude EXCLUDE] [--list]
                     [--format {text,subunit}]
                     [INCLUDE [INCLUDE ...]]

Load and run tests.

positional arguments:
  INCLUDE               All tests matching the INCLUDE regexp will be run. Can
                        be repeated.

optional arguments:
  -h, --help            show this help message and exit
  --module MODULE, -m MODULE
                        Load tests from MODULE[:PATH]. MODULE is found in
                        python path or PATH if specified. Can be repeated.
  --exclude EXCLUDE, -X EXCLUDE
                        All tests matching the EXCLUDE regexp will not be run.
                        Can be repeated.
  --list, -l            List the tests instead of running them.
  --format {text,subunit}, -f {text,subunit}
                        Output format for the test results.
''',
                                              self.out.getvalue())

    def test_default_values(self):
        ns = self.parse_args([])
        self.assertEqual([], ns.include_regexps)
        self.assertEqual(None, ns.modules)
        self.assertEqual(None, ns.exclude_regexps)
        self.assertFalse(ns.list_only)
        self.assertEqual('text', ns.format)

    def test_include_regexps(self):
        ns = self.parse_args(['a', 'b'])
        self.assertEqual(['a', 'b'], ns.include_regexps)

    def test_modules(self):
        ns = self.parse_args(['--module', 'a', '-m', 'b:.'])
        self.assertEqual(['a', 'b:.'], ns.modules)

    def test_exclude_regexps(self):
        ns = self.parse_args(['--exclude', 'a', '-X', 'b'])
        self.assertEqual(['a', 'b'], ns.exclude_regexps)

    def test_list(self):
        ns = self.parse_args(['--list'])
        self.assertTrue(ns.list_only)

    def test_format_text(self):
        ns = self.parse_args(['--format', 'text'])
        self.assertEqual('text', ns.format)

    def test_format_subunit(self):
        ns = self.parse_args(['-f', 'subunit'])
        self.assertEqual('subunit', ns.format)


class TestArgParserSubClassing(unittest.TestCase):

    def test_new_prog(self):

        class New(runners.RunTestsArgParser):

            def __init__(self, prog):
                super(New, self).__init__(prog)

        new = New('foo')
        self.assertEqual('foo', new.prog)

    def test_new_description(self):
        class New(runners.RunTestsArgParser):

            def __init__(self, description):
                super(New, self).__init__(description=description)

        new = New('foo')
        self.assertEqual('foo', new.description)
        # 'prog' is unchanged
        self.assertEqual('uci-run-tests', new.prog)
