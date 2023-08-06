#   fluentmock
#   Copyright 2013-2014 Michael Gruber
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


class FluentMatcher(object):

    def matches(self, value):
        raise NotImplementedError()

    def __repr__(self):
        raise NotImplementedError()


class FluentAnyArguments(FluentMatcher):

    def matches(self, value):
        return True

    def __repr__(self):
        return '<< ANY_ARGUMENTS >>'


class FluentAnyArgument(FluentMatcher):

    def matches(self, value):
        return True

    def __repr__(self):
        return '<< ANY_ARGUMENT >>'


class ContainsMatcher(FluentMatcher):

    def __init__(self, substring):
        self._substring = substring

    def matches(self, value):
        return value.find(self._substring) >= 0

    def __repr__(self):
        return '<< a string containing "{substring}" >>'.format(substring=self._substring)


def contains(substring):
    return ContainsMatcher(substring)
