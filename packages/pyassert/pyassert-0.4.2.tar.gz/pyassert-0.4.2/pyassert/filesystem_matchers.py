#  pyassert
#  Copyright 2012 The pyassert team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

__author__ = "Alexander Metzner"

import os
import six

from .matcher_registry import Matcher, register_matcher


@register_matcher("is_a_directory")
@register_matcher("is_not_a_directory", negated=True)
class DirectoryExistsMatcher(Matcher):
    def accepts(self, actual):
        return isinstance(actual, six.string_types)

    def matches(self, actual):
        return os.path.exists(actual) and os.path.isdir(actual)

    def describe(self, actual):
        return "'{0}' is not an existing directory".format(actual)

    def describe_negated(self, actual):
        return "'{0}' is an existing directory".format(actual)


@register_matcher("is_a_file")
@register_matcher("is_not_a_file", negated=True)
class FileExistsMatcher(Matcher):
    def accepts(self, actual):
        return isinstance(actual, six.string_types)

    def matches(self, actual):
        return os.path.exists(actual) and os.path.isfile(actual)

    def describe(self, actual):
        return "'{0}' is not an existing file".format(actual)

    def describe_negated(self, actual):
        return "'{0}' is an existing file".format(actual)


@register_matcher("has_file_length_of")
class FileLengthMatcher(FileExistsMatcher):
    def __init__(self, expected_size):
        self._expected_size = expected_size
        self._actual_size = -1

    def matches(self, actual):
        if not FileExistsMatcher.matches(self, actual):
            return False

        self._determine_file_size(actual)

        return int(self._actual_size) == int(self._expected_size)

    def describe(self, actual):
        return "Actual '{0}' has a length of {1:d} bytes but expected {2:d} bytes.".format(actual,
                                                                                           self._actual_size,
                                                                                           self._expected_size)

    def _determine_file_size(self, filename):
        self._actual_size = os.stat(filename).st_size


@register_matcher("is_a_empty_file")
class EmptyFileMatcher(FileLengthMatcher):
    def __init__(self):
        self._expected_size = 0

    def describe(self, actual):
        return "Actual file '{0}' is not empty.".format(actual)


@register_matcher("is_a_file_with_content")
class FileContentMatcher(FileExistsMatcher):
    """matches a given file for the expected file content"""
    def __init__(self, expected_content):
        self._actual_content = None
        self._expected_content = expected_content

    def matches(self, actual_file_name):
        """checks if the file with the given name has the expected content"""
        if not FileExistsMatcher.matches(self, actual_file_name):
            return False

        with open(actual_file_name, "r") as actual_file:
            self._actual_content = actual_file.read()

        return self._actual_content == self._expected_content

    def describe(self, actual_file_name):
        return "Actual file '{0}' has content '{1}' but expected '{2}'.".format(actual_file_name,
                                                                                self._actual_content,
                                                                                self._expected_content)
