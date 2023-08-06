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
"""A collection of commonly used 'Features' to optionally run tests."""

from distutils import spawn
import unittest


class Feature(object):
    """An operating system Feature."""

    def __init__(self):
        self._available = None

    def available(self):
        """Is the feature available?

        :return: True if the feature is available.
        """
        if self._available is None:
            self._available = self._probe()
        return self._available

    def _probe(self):
        """Implement this method in concrete features.

        :return: True if the feature is available.
        """
        raise NotImplementedError

    def feature_name(self):
        return self.__class__.__name__

    def __unicode__(self):
        return self.feature_name()


class ExecutableFeature(Feature):
    """Feature testing whether an executable of a given name is on the PATH."""

    def __init__(self, name):
        super(ExecutableFeature, self).__init__()
        self.name = name
        self._path = None

    @property
    def path(self):
        # This is a property, so accessing path ensures _probe was called
        self.available()
        return self._path

    def _probe(self):
        self._path = spawn.find_executable(self.name)
        return self._path is not None

    def feature_name(self):
        return '{} executable'.format(self.name)


def requires(feature):
    """A decorator to skip a test if a feature is not available."""
    if not feature.available():
        reason = '{} is not available'.format(feature.feature_name())
        return unittest.skip(reason)

    # If the feature is available, there is no need to decorate
    return lambda obj: obj
