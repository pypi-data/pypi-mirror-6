# This file is part of the Ubuntu Continuous Integration test tools
#
# Copyright 2014 Canonical Ltd.
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

import unittest

import ucitests
from ucitests import (
    features,
    fixtures,
    styles,
    tests,
)


@features.requires(tests.minimal_pep8)
class TestTestPep8Usage(unittest.TestCase):

    def test_no_packages(self):
        with self.assertRaises(AssertionError) as cm:

            class Pep8(styles.TestPep8):

                packages = []

            test = Pep8('test_pep8_conformance')
            test.test_pep8_conformance()

        self.assertEqual('You should define some packages to check',
                         cm.exception.message)


@features.requires(tests.minimal_pyflakes)
class TestTestPyflakesUsage(unittest.TestCase):

    def test_no_packages(self):
        with self.assertRaises(AssertionError) as cm:

            class Pyflakes(styles.TestPyflakes):

                packages = []

            test = Pyflakes('test_pyflakes_conformance')
            test.test_pyflakes_conformance()

        self.assertEqual('You should define some packages to check',
                         cm.exception.message)


class TestIterFiles(unittest.TestCase):

    def setUp(self):
        super(TestIterFiles, self).setUp()
        fixtures.set_uniq_cwd(self)

    def test_empty(self):
        # self.assertEqual([], styles.iter_files([])
        pass


class TestPyflakesCheckFromDir(unittest.TestCase):

    def setUp(self):
        super(TestPyflakesCheckFromDir, self).setUp()
        fixtures.set_uniq_cwd(self)
        self.paths = []

        def check_file(path, ignored):
            self.paths.append(path)

        self.check = check_file

    def assertPaths(self, expected, tree, excludes=None):
        if excludes is None:
            excludes = []
        tests.write_tree_from_desc(tree)
        styles.pyflakes_check_dir(styles.PythonFileWalker('.'), '.',
                                  excludes, self.check, None)
        self.assertEqual(expected, self.paths)

    def test_empty(self):
        self.assertPaths([], '')

    def test_tree(self):
        self.assertPaths(['./a/bar.py', './b/c/baz.py', './foo.py'], '''
file: foo
file: foo.py
dir: a
file: a/bar
file: a/bar.py
dir: b
dir: b/c
file: b/c/baz.py
''')

    def test_tree_with_excludes(self):
        self.assertPaths(['./a/bar.py', './b/c/baz.py'], '''
file: foo
file: foo.py
dir: a
file: a/bar
file: a/bar.py
dir: b
dir: b/c
file: b/c/baz.py
''',
                         excludes=['foo.py'])


# Style tests for ucitests itself

class TestPep8(styles.TestPep8):

    packages = [ucitests]


class TestPyflakes(styles.TestPyflakes):

    packages = [ucitests]
