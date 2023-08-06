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
"""Common fixtures with minimal constraints on the test class used.

A common pattern in TestCase is to add fixtures in the base class so they are
accessible to all tests. This pollutes the base classes with methods or
attributes not used by most of the tests.

Fixtures are better used via composition. But requiring an additional
'.fixtures.feature_x.attribute_y' make them harder to use.

We use a middle ground here by just joining a simpler (and a bit surprising at
first) syntax and using python's ability to handle arbitrary attributes.

Apart from that modest invasise use of test objects namespace, the only
constraint is that the test object supports the 'addCleanup' and the most usual
assertX methods. Since 'addCleanup' is provided by unittest.TestCase itself,
this is a light constraint, most python test frameworks inheriting from it.

The benefit is that these fixtures can be used on any TestCase class without
requiring inheritance which can then be used for other needs without
interferences.
"""


import inspect
import os
import shutil
import sys
import tempfile
import unittest


import testtools

_DOESNT_EXIST = object()
"""Special value to denote an attribute that didn't exist before patching."""


def patch(test, obj, attr_name, new):
    """Set 'obj.<attr_name>' to 'new' while the test is running.

    If 'obj' has no attribute named 'attr_name', then the patch will still go
    ahead, and the attribute will be deleted instead of restored to its
    original value at the end of the test.

    :param obj: The object to patch. Can be anything.

    :param attr_name: The attribute name on 'obj' to patch.

    :param new: The value to set 'obj.attr_name' to.
    """
    actual = getattr(obj, attr_name, _DOESNT_EXIST)
    setattr(obj, attr_name, new)

    def restore(obj, attr_name, value):
        """Restore 'obj.<attr_name>' to 'value'."""
        if value is _DOESNT_EXIST:
            delattr(obj, attr_name)
        else:
            setattr(obj, attr_name, value)
    # Using 'actual' below capture the value in the cleanup, preserving it when
    # this function (patch) is left
    test.addCleanup(restore, obj, attr_name, actual)


def set_uniq_cwd(test):
    """Create a temporary directory an cd into it for the test duration.

    :param test: The test to isolate in a temporary directory.

    This is generally called during a test setup. It requires a test providing
    the 'addCleanup' method and will set the 'uniq_dir' attribute.

    Note that it doesn't prohibit the test to write anywhere it has access to,
    but it changes its current directory so that relative paths end in a
    temporary directory. In practice, this means using simple strings paths
    instead of os.path.join'ing them which is less readable and clutter the
    test.

    This can also be used to create a home directory (as long as $HOME is also
    set appropriately) when the test needs to access '~/' files for example.
    """
    test.uniq_dir = tempfile.mkdtemp(prefix='mytests-', suffix='.tmp')
    test.addCleanup(shutil.rmtree, test.uniq_dir, True)
    current_dir = os.getcwd()
    test.addCleanup(os.chdir, current_dir)
    os.chdir(test.uniq_dir)


def protect_imports(test):
    """Protect sys.modules and sys.path for the test duration.

    This is useful to test imports which modifies sys.modules or requires
    modifying sys.path.
    """
    # Protect sys.modules and sys.path to be able to test imports
    patch(test, sys, 'path', list(sys.path))
    orig_modules = sys.modules.copy()

    def cleanup_modules():
        # Remove all added modules
        added = [m for m in sys.modules.keys() if m not in orig_modules]
        if added:
            for m in added:
                del sys.modules[m]
        # Restore deleted or modified modules
        sys.modules.update(orig_modules)
    test.addCleanup(cleanup_modules)


def make_case(kind='pass'):
    """Build a unittest.TestCase of a given kind.

    :param kind: The kind of test (pass, fail, see code for details). This used
        to select the method named 'test_{kind}'.

    :return: A freshly built unittest test case.

    :note: This relies on a locally defined class so test loading does not see
        it.
    """
    class Test(unittest.TestCase):

        # When this file is edited, the tracebacks for test_fail and test_error
        # change. To avoid spurious failures, we automate by capturing the
        # proper line.
        traceback_line = None
        # Getting the file name right is tricky, depending on whether the
        # module was just recompiled or not __file__ can be either .py or .pyc
        # but when it appears in an exception, the .py is always used.
        traceback_file = __file__.replace('.pyc', '.py').replace('.pyo', '.py')

        def test_pass(self):
            pass

        def test_fail(self):
            self.traceback_line = inspect.currentframe().f_lineno + 1
            raise self.failureException

        def test_error(self):
            self.traceback_line = inspect.currentframe().f_lineno + 2
            raise SyntaxError('invalid syntax',
                              (self.traceback_file, 1, 1, 'No python'))

        def test_skip(self):
            self.skipTest('')

        def test_skip_reason(self):
            self.skipTest('Because')

        @unittest.expectedFailure
        def test_expected_failure(self):
            self.traceback_line = inspect.currentframe().f_lineno + 1
            self.assertEqual(1, 0, "1 should be 0")

        @unittest.expectedFailure
        def test_unexpected_success(self):
            self.assertEqual(1, 1, "1 is not 1")

    return Test('test_{}'.format(kind))


def make_testtools_case(kind='pass'):
    """Build a testtools.TestCase of a given kind.

    :param kind: The kind of test (pass, fail, see code for details). This used
        to select the method named 'test_{kind}'.

    :return: A freshly built unittest test case.

    :note: This relies on a locally defined class so test loading does not see
        it. This differs from make_case() in subtle but invasive ways which are
        better kept in a separated function.
    """
    class Test(testtools.TestCase):

        # When this file is edited, the tracebacks for test_fail and test_error
        # change. To avoid spurious failures, we automate by capturing the
        # proper line.
        traceback_line = None
        traceback_file = __file__

        def test_pass(self):
            pass

        def test_fail(self):
            self.traceback_line = inspect.currentframe().f_lineno + 1
            raise self.failureException

        def test_error(self):
            self.traceback_line = inspect.currentframe().f_lineno + 1
            raise SyntaxError

        def test_skip(self):
            self.skipTest('')

        def test_skip_reason(self):
            self.skipTest('Because')

        def test_expected_failure(self):
            # We expect the test to fail and it does
            self.expectFailure("1 should be 0", self.assertEqual, 1, 0)

        def test_unexpected_success(self):
            # We expect the test to fail but it doesn't
            self.expectFailure("1 is not 1", self.assertEqual, 1, 1)

    return Test('test_{}'.format(kind))


def make_suite(kinds, maker=None):
    """Build a test suite from a list of kinds.

    :param kinds: A list of kinds to be passed to maker to make a test case.

    :param maker: A callable accepting a kind and returning a test case.

    :return: A test suite
    """
    suite = unittest.TestSuite()
    if maker is None:
        maker = make_case
    suite.addTests([maker(kind) for kind in kinds])
    return suite


def setup_for_local_imports(test):
    """A setup method allowing test to import local files.

    This protects sys.path and sys.modules while allowing importing local
    files.
    """
    set_uniq_cwd(test)
    protect_imports(test)
    sys.path.insert(0, test.uniq_dir)


def override_env_variable(name, value):
    """Modify the environment, setting or removing the env_variable.

    :param name: The environment variable to set.

    :param value: The value to set the environment to. If None, then
        the variable will be removed.

    :return: The original value of the environment variable.
    """
    orig = os.environ.get(name)
    if value is None:
        if orig is not None:
            del os.environ[name]
    else:
        os.environ[name] = value
    return orig


def override_env(test, name, new):
    """Set an environment variable, and reset it after the test.

    :param name: The environment variable name.

    :param new: The value to set the variable to. If None, the variable is
        deleted from the environment.

    :returns: The actual variable value.
    """
    value = override_env_variable(name, new)
    test.addCleanup(override_env_variable, name, value)
    return value


isolated_environ = {
    'HOME': None,
}


def isolate_from_env(test, env=None):
    """Isolate test from the environment variables.

    This is usually called in setUp for tests that needs to modify the
    environment variables and restore them after the test is run.

    :param test: A test instance

    :param env: A dict containing variable definitions to be installed. Only
        the variables present there are protected. They are initialized with
        the provided values.
    """
    if env is None:
        env = isolated_environ
    for name, value in env.items():
        override_env(test, name, value)
