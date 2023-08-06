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
"""Filter tests suite with regular expressions."""

import re
import unittest


def filter_suite(condition, suite):
    """Return tests for which ``condition`` is True in ``suite``.

    :param condition: A callable receiving a test and returning True if the
        test should be kept.

    :param suite: A test suite that can be iterated. It contains either tests
        or suite inheriting from ``unittest.TestSuite``.

    ``suite`` is a tree of tests and suites, the returned suite respect the
    received suite layout, only removing empty suites.
    """
    filtered_suite = suite.__class__()
    for test in suite:
        if issubclass(test.__class__, unittest.TestSuite):
            # We received a suite, we'll filter a suite
            filtered = filter_suite(condition, test)
            if filtered.countTestCases():
                # Keep only non-empty suites
                filtered_suite.addTest(filtered)
        elif condition(test):
            # The test is kept
            filtered_suite.addTest(test)
    return filtered_suite


def iter_flat(this):
    """Iterate a suite or yield a test.

    When preserving the test suite shape (a tree in the general case) is not a
    concern, this is the easiest way to iterate a test suite.
    """
    try:
        suite = iter(this)
    except TypeError:
        # If it can't be iterated, it's a test
        yield this
    else:
        for that in suite:
            for t in iter_flat(that):
                yield t


def include_regexps(regexps, suite):
    """Returns the tests that match one of ``regexps``.

    :param regexps: A list of test id regexps (strings, will be compiled
        internally) to include. All tests are included if no regexps are
        provided.

    :param suite: The test suite to filter.
    """
    if not regexps:
        # No regexeps, no filtering
        return suite

    def matches_one_of(test):
        # A test is kept if its id matches one of the regexps
        tid = test.id()
        for reg in regexps:
            if re.search(reg, tid) is not None:
                return True
        return False
    return filter_suite(matches_one_of, suite)


def exclude_regexps(regexps, suite):
    """Returns the tests whose id does not match with any of the regexps.

    :param regexps: A list of test id regexps (strings, will be compiled
        internally) to exclude. No tests are excluded if no regexps are
        provided.

    :param suite: The test suite to filter.
    """
    if not regexps:
        # No regexeps, no filtering
        return suite

    def matches_none_of(test):
        # A test is kept if its id matches none of the regexps
        tid = test.id()
        for regexp in regexps:
            if re.search(regexp, tid):
                return False
        return True
    return filter_suite(matches_none_of, suite)
