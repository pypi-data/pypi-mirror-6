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

import argparse
import sys


import subunit


from ucitests import (
    filters,
    loaders,
    results,
)


class RunTestsArgParser(argparse.ArgumentParser):
    """A parser for the uci-run-tests script.

    This can be used as a base class for scripts that want to add more options
    to suit their needs.
    """

    def __init__(self, prog=None, description=None):
        if prog is None:
            prog = 'uci-run-tests'
        if description is None:
            description = 'Load and run tests.'
        super(RunTestsArgParser, self).__init__(prog=prog,
                                                description=description)
        self.add_argument(
            'include_regexps', metavar='INCLUDE', nargs='*',
            help='All tests matching the INCLUDE regexp will be run.'
            ' Can be repeated.')
        # Optional arguments
        self.add_argument(
            '--module', '-m', metavar='MODULE',  action='append',
            dest='modules',
            help='Load tests from MODULE[:PATH]. MODULE is found in'
            ' python path or PATH if specified.'
            ' Can be repeated.')
        self.add_argument(
            '--exclude', '-X', metavar='EXCLUDE',  action='append',
            dest='exclude_regexps',
            help='All tests matching the EXCLUDE regexp will not be run.'
            ' Can be repeated.')
        self.add_argument(
            '--list', '-l', action='store_true',
            dest='list_only',
            help='List the tests instead of running them.')
        self.add_argument(
            '--format', '-f', choices=['text', 'subunit'], default='text',
            help='Output format for the test results.')

    def parse_args(self, args=None, out=None, err=None):
        """Parse arguments, overridding stdout/stderr if provided.

        Overridding stdout/stderr is provided for tests.

        :params args: The arguments to the script.

        :param out: Default to sys.stdout.

        :param err: Default to sys.stderr.

        :return: The populated namespace.
        """
        out_orig = sys.stdout
        err_orig = sys.stderr
        try:
            if out is not None:
                sys.stdout = out
            if err is not None:
                sys.stderr = err
            return super(RunTestsArgParser, self).parse_args(args)
        finally:
            sys.stdout = out_orig
            sys.stderr = err_orig


def cli_run(args=None, stdout=None, stderr=None):
    """Run tests from the command line."""
    if args is None:
        args = sys.argv[1:]
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr
    parser = RunTestsArgParser()
    ns = parser.parse_args(args)
    suite = load_tests(ns.include_regexps, ns.exclude_regexps,
                       modules=ns.modules)
    if ns.list_only:
        ret = list_tests(suite, stdout)
    else:
        if ns.format == 'text':
            result = results.TextResult(stdout, verbosity=2)
        else:
            result = subunit.TestProtocolClient(stdout)
        ret = run_tests(suite, result)
    return ret


def load_tests(include_regexps, exclude_regexps=None, modules=None):
    """Load tests matching inclusive and exclusive regexps.

    :param include_regexps: A list of regexps describing the tests to include.

    :param exclude_regexps: A list of regexps describing the tests to exclude.

    :param modules: A list of module python names from which the tests should
        be loaded. Default to None which fallbacks to loading tests from the
        current directory.

    :return: The test suite for all collected tests.
    """
    loader = loaders.Loader()
    suite = loader.suiteClass()
    if modules is None:
        suite.addTests(loader.loadTestsFromTree('.'))
    else:
        for mod_name in modules:
            mod_tests = loader.loadTestsFromSysPathModule(mod_name)
            if mod_tests is not None:
                suite.addTests(mod_tests)
    suite = filters.include_regexps(include_regexps, suite)
    suite = filters.exclude_regexps(exclude_regexps, suite)
    return suite


def list_tests(suite, stream):
    """List the test ids , one by line.

    :param suite: A test suite to list.

    :param stream: A writable stream.

    :return: 0 on success, 1 otherwise.

    :note: Listing no tests is an error. The rationale is that when used from a
        script, most people expects to select at least one test and there has
        been numerous reports of people being confused that listing *no* tests
        wasn't flagged as an error. In most of these cases, *another* error led
        to no tests being selected but trapping it here helps.
    """
    no_tests = True
    for t in filters.iter_flat(suite):
        stream.write('{}\n'.format(t.id()))
        no_tests = False
    return int(no_tests)


def run_tests(suite, result):
    """Run the provided tests with the provided test result.

    :param suite: A test suite.

    :param result: The collecting test result object.

    :return: 0 on success, 1 otherwise.

    :note: Running no tests is an error. The rationale is that when used from a
        script, most people expects to run at least one test and there has been
        numerous reports of people being confused that running *no* tests
        wasn't flagged as an error. In most of these cases, *another* error led
        to no tests being run but trapping it here helps.
    """
    result.startTestRun()
    try:
        suite.run(result)
    finally:
        result.stopTestRun()
    return int(not (result.wasSuccessful() and result.testsRun > 0))
