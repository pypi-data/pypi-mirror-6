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

import os
import unittest


from ucitests import (
    features,
    fixtures,
)


class MinimalTesttools(features.Feature):

    def _probe(self):
        import testtools
        return testtools.__version__ >= (0, 9, 30)


minimal_testtools = MinimalTesttools()


class MinimalPep8(features.Feature):
    # Supporting precise is just too much work, requires at least the saucy
    # version

    def _probe(self):
        import pep8
        return pep8.__version__ >= '1.4.6'


minimal_pep8 = MinimalPep8()


class MinimalPyflakes(features.Feature):
    # Supporting precise is just too much work, requires at least the saucy
    # version

    def _probe(self):
        import pyflakes
        return pyflakes.__version__ >= '0.7.3'


minimal_pyflakes = MinimalPyflakes()


def write_tree_from_desc(description):
    """Write a tree described in a textual form to disk.

    The textual form describes the file contents separated by file/dir names.

    'file: <file name>' on a single line starts a file description. The file
    name must be the relative path from the tree root.

    'dir: <dir name>' on a single line starts a dir description.

    'link: <link source> <link name>' on a single line describes a symlink to
    <link source> named <link name>. The source may not exist, spaces are not
    allowed.

    :param description: A text where files and directories contents is
        described in a textual form separated by file/dir names.
    """
    cur_file = None
    for line in description.splitlines():
        if line.startswith('file: '):
            # A new file begins
            if cur_file:
                cur_file.close()
            cur_file = open(line[len('file: '):], 'w')
            continue
        if line.startswith('dir:'):
            # A new dir begins
            if cur_file:
                cur_file.close()
                cur_file = None
            os.mkdir(line[len('dir: '):])
            continue
        if line.startswith('link: '):
            # We don't support spaces in names
            link_desc = line[len('link: '):]
            try:
                source, link = link_desc.split()
            except ValueError:
                raise ValueError('Invalid link description: %s' % (link_desc,))
            os.symlink(source, link)
            continue
        if cur_file is not None:  # If no file is declared, nothing is written
            # splitlines() removed the \n, let's add it again
            cur_file.write(line + '\n')
    if cur_file:
        cur_file.close()


class TestWriteTreeFromDesc(unittest.TestCase):

    def setUp(self):
        super(TestWriteTreeFromDesc, self).setUp()
        fixtures.set_uniq_cwd(self)

    def test_empty_description(self):
        self.assertEqual([], os.listdir('.'))
        write_tree_from_desc('')
        self.assertEqual([], os.listdir('.'))

    def test_single_line_without_return(self):
        self.assertEqual([], os.listdir('.'))
        write_tree_from_desc('file: foo')
        self.assertEqual(['foo'], os.listdir('.'))
        with open('foo') as f:
            self.assertEqual('', f.read())

    def test_leading_line_is_ignored(self):
        self.assertEqual([], os.listdir('.'))
        write_tree_from_desc('tagada\nfile: foo')
        self.assertEqual(['foo'], os.listdir('.'))
        with open('foo') as f:
            self.assertEqual('', f.read())

    def test_orphan_line_is_ignored(self):
        self.assertEqual([], os.listdir('.'))
        write_tree_from_desc('''
dir: foo
orphan line
file: foo/bar.py
baz
''')
        self.assertEqual(['foo'], os.listdir('.'))
        self.assertEqual(['bar.py'], os.listdir('foo'))
        with open('foo/bar.py') as f:
            self.assertEqual('baz\n', f.read())

    def test_empty_file_content(self):
        write_tree_from_desc('''file: foo''')
        with open('foo') as f:
            self.assertEqual('', f.read())

    def test_simple_file_content(self):
        write_tree_from_desc('''file: foo
tagada
''')
        with open('foo') as f:
            self.assertEqual('tagada\n', f.read())

    def test_file_content_in_a_dir(self):
        write_tree_from_desc('''dir: dir
file: dir/foo
bar
''')
        with open('dir/foo') as f:
            self.assertEqual('bar\n', f.read())

    def test_simple_symlink_creation(self):
        write_tree_from_desc('''file: foo
tagada
link: foo bar
''')
        with open('foo') as f:
            self.assertEqual('tagada\n', f.read())
        with open('bar') as f:  # Yeah ! Open Bar !
            self.assertEqual('tagada\n', f.read())

    def test_broken_symlink_creation(self):
        write_tree_from_desc('''link: foo bar
''')
        self.assertEqual('foo', os.readlink('bar'))

    def test_invalid_symlink_description_raises(self):
        with self.assertRaises(ValueError) as cm:
            write_tree_from_desc('''link: foo
''')
        self.assertEqual('Invalid link description: foo', cm.exception.args[0])
