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

from __future__ import unicode_literals
import testtools
from testtools import testresult


class TextResult(testresult.TextTestResult):
    """A TestResult which outputs activity to a text stream."""

    def __init__(self, stream, failfast=False, verbosity=1):
        if testtools.__version__ >= (0, 9, 30):
            super(TextResult, self).__init__(stream, failfast)
        else:
            # Maintain compatibility with what is shipped on precise until we
            # switch to trusty. In the mean time, we just ignore --failfast :-/
            # -- vila 2014-01-28
            super(TextResult, self).__init__(stream)
        self.verbose = verbosity > 1

    def startTest(self, test):
        if self.verbose:
            self.stream.write(test.id())
            self.stream.write(' ... ')
        self.start_time = self._now()
        super(TextResult, self).startTest(test)

    def stopTest(self, test):
        if self.verbose:
            elapsed_time = self._now() - self.start_time
            self.stream.write(' (%.3f secs)\n'
                              % self._delta_to_float(elapsed_time))
            self.stream.flush()
        super(TextResult, self).stopTest(test)

    def addError(self, test, err=None, details=None):
        if self.verbose:
            self.stream.write('ERROR')
        else:
            self.stream.write('E')
        super(TextResult, self).addError(test, err, details)

    def addFailure(self, test, err=None, details=None):
        if self.verbose:
            self.stream.write('FAIL')
        else:
            self.stream.write('F')
        super(TextResult, self).addFailure(test, err, details)

    def addSkip(self, test, reason):
        if self.verbose:
            if not reason:
                reason_displayed = ''
            else:
                reason_displayed = ' ' + reason
            self.stream.write('SKIP%s' % reason_displayed)
        else:
            self.stream.write('s')
        super(TextResult, self).addSkip(test, reason)

    def addSuccess(self, test, details=None):
        if self.verbose:
            self.stream.write('OK')
        else:
            self.stream.write('.')
        super(TextResult, self).addSuccess(test, details)

    def addExpectedFailure(self, test, err=None):
        if self.verbose:
            self.stream.write('XFAIL')
        else:
            self.stream.write('x')
        super(TextResult, self).addExpectedFailure(test, err)

    def addUnexpectedSuccess(self, test):
        if self.verbose:
            self.stream.write('NOTOK')
        else:
            self.stream.write('u')
        super(TextResult, self).addUnexpectedSuccess(test)
