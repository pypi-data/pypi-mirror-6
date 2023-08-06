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

import os
import unittest
import sys


from ucitests import (
    assertions,
    fixtures,
)


class TestPatch(unittest.TestCase):

    def test_new_attribute(self):
        fixtures.patch(self, self, 'attr', 'hello')
        self.assertEqual('hello', self.attr)

    def test_new_value(self):
        self.attr = 'foo'
        fixtures.patch(self, self, 'attr', 'bar')
        self.assertEqual('bar', self.attr)

    def test_preserved_value(self):
        self.attr = 'foo'

        class LocalTest(unittest.TestCase):

            # We use inner below so 'self' can still refer to the outer test
            def test_it(inner):
                fixtures.patch(inner, self, 'attr', 'bar')
                # inner sees the modified value
                inner.assertEqual('bar', self.attr)

        assertions.assertSuccessfullTest(self, LocalTest('test_it'))
        # The value has been restored
        self.assertEqual('foo', self.attr)

    def test_removed_attribute_is_restored(self):
        self.attr = 'foo'

        class LocalTest(unittest.TestCase):

            # We use inner below so 'self' can still refer to the outer test
            def test_it(inner):
                fixtures.patch(inner, self, 'attr', 'bar')
                delattr(self, 'attr')
                inner.assertEqual('not there',
                                  getattr(self, 'attr', 'not there'))

        assertions.assertSuccessfullTest(self, LocalTest('test_it'))
        # The attribute is back with the proper value
        self.assertEqual('foo', self.attr)


class TestCwdToTmp(unittest.TestCase):

    def test_dir_created_and_changed(self):
        cur = os.getcwd()
        fixtures.set_uniq_cwd(self)
        self.assertNotEqual(cur, os.getcwd())

    def test_dir_restored(self):
        self.before = os.getcwd()
        self.during = None

        # To check the cleanup we need to run an inner test
        class LocalTest(unittest.TestCase):

            # We use inner below so 'self' can still refer to the outer test
            def test_it(inner):
                # The current directory has not changed
                inner.assertEqual(self.before, os.getcwd())
                fixtures.set_uniq_cwd(inner)
                # The current directory has changed
                inner.assertNotEqual(self.before, os.getcwd())
                self.during = os.getcwd()

        assertions.assertSuccessfullTest(self, LocalTest('test_it'))
        # The current directory has been restored
        self.assertEqual(self.before, os.getcwd())


class TestProtectImports(unittest.TestCase):

    def setUp(self):
        super(TestProtectImports, self).setUp()
        fixtures.protect_imports(self)

    def test_added_module_is_removed(self):
        self.assertIs(None, sys.modules.get('foo', None))

        class Test(unittest.TestCase):

            def test_it(self):
                fixtures.protect_imports(self)
                sys.modules['foo'] = 'bar'

        assertions.assertSuccessfullTest(self, Test('test_it'))
        self.assertIs(None, sys.modules.get('foo', None))

    def test_removed_module_is_restored(self):
        self.assertIs(None, sys.modules.get('I_dont_exist', None))
        sys.modules['I_dont_exist'] = 'bar'

        class Test(unittest.TestCase):

            def test_it(self):
                fixtures.protect_imports(self)
                self.assertEqual('bar', sys.modules['I_dont_exist'])
                del sys.modules['I_dont_exist']

        assertions.assertSuccessfullTest(self, Test('test_it'))
        self.assertEqual('bar', sys.modules['I_dont_exist'])

    def test_modified_module_is_restored(self):
        self.assertIs(None, sys.modules.get('I_dont_exist', None))
        sys.modules['I_dont_exist'] = 'bar'

        class Test(unittest.TestCase):

            def test_it(self):
                fixtures.protect_imports(self)
                self.assertEqual('bar', sys.modules['I_dont_exist'])
                sys.modules['I_dont_exist'] = 'qux'

        assertions.assertSuccessfullTest(self, Test('test_it'))
        self.assertEqual('bar', sys.modules['I_dont_exist'])

    def test_modified_sys_path_is_restored(self):
        fixtures.set_uniq_cwd(self)
        inserted = self.uniq_dir
        self.assertFalse(inserted in sys.path)

        class Test(unittest.TestCase):

            def test_it(self):
                fixtures.protect_imports(self)
                sys.path.insert(0, inserted)

        assertions.assertSuccessfullTest(self, Test('test_it'))
        self.assertFalse(inserted in sys.path)


class TestEnv(unittest.TestCase):

    def test_env_preserved(self):
        os.environ['NOBODY_USES_THIS'] = 'foo'

        class Inner(unittest.TestCase):

            def test_overridden(self):
                fixtures.isolate_from_env(self, {'NOBODY_USES_THIS': 'bar'})
                self.assertEqual('bar', os.environ['NOBODY_USES_THIS'])

        assertions.assertSuccessfullTest(self, Inner('test_overridden'))
        self.assertEqual('foo', os.environ['NOBODY_USES_THIS'])

    def test_env_var_deleted(self):
        os.environ['NOBODY_USES_THIS'] = 'foo'

        class Inner(unittest.TestCase):

            def test_deleted(self):
                fixtures.isolate_from_env(self, {'NOBODY_USES_THIS': None})
                self.assertIs('deleted',
                              os.environ.get('NOBODY_USES_THIS', 'deleted'))
        assertions.assertSuccessfullTest(self, Inner('test_deleted'))
        self.assertEqual('foo', os.environ['NOBODY_USES_THIS'])
