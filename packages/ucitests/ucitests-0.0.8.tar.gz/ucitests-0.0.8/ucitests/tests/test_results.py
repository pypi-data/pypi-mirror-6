# This file is part of the Ubuntu Continuous Integration test tools
#
# Copyright 2013 Canonical Ltd.
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
    tests,
)


class TestTextResultOutput(unittest.TestCase):

    def assertOutput(self, expected, kind):
        test = fixtures.make_case(kind)
        out = StringIO()
        res = results.TextResult(out)

        # We don't care about timing here so we always return 0 which
        # simplifies matching the expected result
        def zero(atime):
            return 0.0
        res._delta_to_float = zero
        test.run(res)
        self.assertEqual(expected, res.stream.getvalue())

    def test_pass(self):
        self.assertOutput('.', 'pass')

    def test_fail(self):
        self.assertOutput('F', 'fail')

    def test_error(self):
        self.assertOutput('E', 'error')

    def test_skip(self):
        self.assertOutput('s', 'skip')

    def test_skip_reason(self):
        self.assertOutput('s', 'skip_reason')

    def test_expected_failure(self):
        self.assertOutput('x', 'expected_failure')

    def test_unexpected_success(self):
        self.assertOutput('u', 'unexpected_success')


def expand_template_for_test(template, test, kwargs=None):
    """Expand common references in template.

    Tests that check run outputs can be simplified if they use templates
    instead of litteral expected strings. There are plenty of examples below.

    :param template: A string where common strings have been replaced by a
        keyword so 1) tests are easier to read, 2) we don't run into pep8
        warnings for long lines.

    :param test: The test case under scrutiny.

    :param kwargs: A dict with more keywords for the template. This allows
        some tests to add more keywords when they are test specific.
    """
    if kwargs is None:
        kwargs = dict()

    def cleanup_file_name(name):
        # Getting the file name right is tricky, depending on whether the
        # module was just recompiled or not __file__ can be either .py or .pyc
        # but when it appears in an exception, the .py is always used.
        return name.replace('.pyc', '.py').replace('.pyo', '.py')

    filename = cleanup_file_name(__file__)
    traceback_fixed_length = kwargs.get('traceback_fixed_length', None)
    if traceback_fixed_length is not None:
        # We need to calculate the traceback detail length which includes the
        # file name.
        full_length = traceback_fixed_length + len(filename)
        # subunit prefixes the traceback with its length, this is the only
        # place that it can be properly calculated.
        kwargs['subunit_traceback_length'] = '%X' % (full_length,)
    traceback_line = getattr(test, 'traceback_line', None)
    kwargs['traceback_line'] = traceback_line
    traceback_file = getattr(test, 'traceback_file', None)
    kwargs['traceback_file'] = cleanup_file_name(traceback_file)
    # To allow easier reading for template, we format some known values
    kwargs.update(dict(classname='%s.%s' % (test.__class__.__module__,
                                            test.__class__.__name__),
                       name=test._testMethodName,
                       filename=filename))
    return template.format(**kwargs)


class TestVerboseResultOutput(unittest.TestCase):

    def assertOutput(self, template, kind):
        test = fixtures.make_case(kind)
        expected = expand_template_for_test(template, test)
        out = StringIO()
        res = results.TextResult(out, verbosity=2)

        # We don't care about timing here so we always return 0 which
        # simplifies matching the expected result
        def zero(atime):
            return 0.0
        res._delta_to_float = zero
        test.run(res)
        self.assertEqual(expected, res.stream.getvalue())

    def test_pass(self):
        self.assertOutput('''\
{classname}.{name} ... OK (0.000 secs)
''',
                          'pass')

    def test_fail(self):
        self.assertOutput('''\
{classname}.{name} ... FAIL (0.000 secs)
''',
                          'fail')

    def test_error(self):
        self.assertOutput('''\
{classname}.{name} ... ERROR (0.000 secs)
''',
                          'error')

    def test_skip(self):
        self.assertOutput('''\
{classname}.{name} ... SKIP (0.000 secs)
''',
                          'skip')

    def test_skip_reason(self):
        self.assertOutput('''\
{classname}.{name} ... SKIP Because (0.000 secs)
''',
                          'skip_reason')

    def test_expected_failure(self):
        self.assertOutput('''\
{classname}.{name} ... XFAIL (0.000 secs)
''',
                          'expected_failure')

    def test_unexpected_success(self):
        self.assertOutput('''\
{classname}.{name} ... NOTOK (0.000 secs)
''',
                          'unexpected_success')


def run_with_subunit(test):
        """Run a suite returning the subunit stream."""
        if tests.minimal_testtools.available():
            stream = io.BytesIO()
        else:
            stream = StringIO()
        res = subunit.TestProtocolClient(stream)
        test.run(res)
        return res, stream


def assertSubunitOutput(test, template, kind, kwargs=None):
    """Assert the expected output from a subunit run for a given test.

    :param template: A string where common strings have been replaced by a
        keyword so we don't run into pep8 warnings for long lines.

    :param kind: A string used to select the kind of test.

    :param kwargs: A dict with more keywords for the template. This allows some
        tests to add more keywords when they are test specific.
    """
    if kwargs is None:
        kwargs = dict()
    test_to_run = test.make_case(kind)
    res, stream = run_with_subunit(test_to_run)
    assertions.assertMultiLineAlmostEqual(
        test,
        expand_template_for_test(template, test_to_run, kwargs),
        stream.getvalue().decode('utf-8'))


class TestSubunitOutputForUnittest(unittest.TestCase):
    """Test subunit output stream."""

    def make_case(self, kind):
        return fixtures.make_case(kind)

    def test_pass(self):
        assertSubunitOutput(self, '''\
test: {classname}.{name}
successful: {classname}.{name}
''',
                            'pass')

    def test_fail(self):
        assertSubunitOutput(self, '''\
test: {classname}.{name}
failure: {classname}.{name} [
Traceback (most recent call last):
  File "{traceback_file}", line {traceback_line}, in {name}
    raise self.failureException
AssertionError
]
''',
                            'fail')

    def test_error(self):
        assertSubunitOutput(self, '''\
test: {classname}.{name}
error: {classname}.{name} [
Traceback (most recent call last):
  File "{traceback_file}", line {traceback_line}, in {name}
    (self.traceback_file, 1, 1, 'No python'))
  File "{traceback_file}", line 1
    # This file is part of the Ubuntu Continuous Integration test tools
    ^
SyntaxError: invalid syntax
]
''',
                            'error')

    def test_skip(self):
        assertSubunitOutput(self, '''\
test: {classname}.{name}
skip: {classname}.{name} [

]
''',
                            'skip')

    def test_skip_reason(self):
        assertSubunitOutput(self, '''\
test: {classname}.{name}
skip: {classname}.{name} [
Because
]
''',
                            'skip_reason')

    @features.requires(tests.minimal_testtools)
    def test_expected_failure(self):
        assertSubunitOutput(self, '''\
test: ucitests.fixtures.Test.test_expected_failure
xfail: ucitests.fixtures.Test.test_expected_failure [
Traceback (most recent call last):
  File "{traceback_file}", line {traceback_line}, in {name}
    self.assertEqual(1, 0, "1 should be 0")
  File ..., in assertEqual
    assertion_func(first, second, msg=msg)
  File ..., in _baseAssertEqual
    raise self.failureException(msg)
AssertionError: 1 should be 0
]
''',
                            'expected_failure')

    def test_unexpected_success(self):
        assertSubunitOutput(self, '''\
test: {classname}.{name}
uxsuccess: {classname}.{name}
''',
                            'unexpected_success')


class TestSubunitOutputForTesttools(unittest.TestCase):
    """Test subunit output stream."""

    def make_case(self, kind):
        return fixtures.make_testtools_case(kind)

    def test_pass(self):
        assertSubunitOutput(self, '''\
test: {classname}.{name}
successful: {classname}.{name} [ multipart
]
''',
                            'pass')

    def test_fail(self):
        assertSubunitOutput(self, '''\
test: {classname}.{name}
failure: {classname}.{name} [ multipart
Content-Type: text/x-traceback;...language=python...
traceback
{subunit_traceback_length}\r
Traceback (most recent call last):
  File "{traceback_file}", line {traceback_line}, in {name}
    raise self.failureException
AssertionError
0\r
]
''',
                            'fail',
                            dict(traceback_fixed_length=106))

    def test_error(self):
        assertSubunitOutput(self, '''\
test: {classname}.{name}
error: {classname}.{name} [ multipart
Content-Type: text/x-traceback;...language=python...
traceback
{subunit_traceback_length}\r
Traceback (most recent call last):
  File "{traceback_file}", line {traceback_line}, in {name}
    raise SyntaxError
SyntaxError: None
0\r
]
''',
                            'error',
                            dict(traceback_fixed_length=100))

    @features.requires(tests.minimal_testtools)
    def test_skip(self):
        assertSubunitOutput(self, '''\
test: {classname}.{name}
skip: {classname}.{name} [ multipart
Content-Type: text/plain;charset=utf8
reason
0\r
]
''',
                            'skip')

    @features.requires(tests.minimal_testtools)
    def test_skip_reason(self):
        assertSubunitOutput(self, '''\
test: {classname}.{name}
skip: {classname}.{name} [ multipart
Content-Type: text/plain;charset=utf8
reason
7\r
Because0\r
]
''',
                            'skip_reason')

    @features.requires(tests.minimal_testtools)
    def test_expected_failure(self):
        assertSubunitOutput(self, '''\
test: {classname}.{name}
xfail: {classname}.{name} [ multipart
Content-Type: text/plain;charset=utf8
reason
D\r
1 should be 00\r
Content-Type: text/x-traceback;...language=python...
traceback
16\r
MismatchError: 1 != 0
0\r
]
''',
                            'expected_failure')

    @features.requires(tests.minimal_testtools)
    def test_unexpected_success(self):
        assertSubunitOutput(self, '''\
test: {classname}.{name}
uxsuccess: {classname}.{name} [ multipart
Content-Type: text/plain;charset=utf8
reason
A\r
1 is not 10\r
]
''',
                            'unexpected_success')


@features.requires(tests.minimal_testtools)
class TestSubunitInputStreamTextResultOutput(TestTextResultOutput):
    """Test subunit input stream.

    More precisely, ensure our test result can properly handle a subunit input
    stream.
    """

    def assertOutput(self, expected, kind):
        test = fixtures.make_case(kind)
        # Get subunit output (what subprocess produce)
        stream = io.BytesIO()
        res = subunit.TestProtocolClient(stream)
        test.run(res)
        # Inject it again (what controlling process consumes)
        input_stream = io.BytesIO(stream.getvalue())
        receiver = subunit.ProtocolTestCase(input_stream)
        out = io.StringIO()
        text_result = results.TextResult(out, verbosity=0)

        # We don't care about timing here so we always return 0 which
        # simplifies matching the expected result
        def zero(atime):
            return 0.0
        text_result._delta_to_float = zero
        receiver.run(text_result)
        self.assertEqual(expected, out.getvalue())
