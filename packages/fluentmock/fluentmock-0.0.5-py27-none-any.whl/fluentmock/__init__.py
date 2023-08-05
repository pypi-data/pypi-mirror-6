#   fluentmock
#   Copyright 2013 Michael Gruber
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

__author__ = 'Michael Gruber'
__version__ = '0.0.5'


from logging import getLogger
from unittest import TestCase

LOGGER = getLogger(__name__)


MESSAGE_COULD_NOT_VERIFY = 'Could not verify {target_name}.{attribute_name}()'
MESSAGE_INVALID_ATTRIBUTE = 'The target "{target_name}" has no attribute called "{attribute_name}".'
MESSAGE_NO_CALLS = """
Expected: call {target_name}.{attribute_name}()
     Got: no stubbed function has been called.
"""

_configurators = {}
_stubs = []
_calls = []


class UnitTests(TestCase):

    def setUp(self):
        self.set_up()

    def tearDown(self):
        self.tear_down()
        unstub()

    def set_up(self):
        """ Override this method to set up your unit test environment """
        pass

    def tear_down(self):
        """ Override this method to tear down your unit test environment """
        pass


class Answer(object):

    def __init__(self, arguments):
        self.arguments = arguments
        self._values = []

    def next(self):
        if len(self._values) == 0:
            return None

        if len(self._values) > 1:
            return self._values.pop(0)

        return self._values[0]

    def then_return(self, value):
        self._values.append(value)
        return self

    def __repr__(self):
        return "Answer(argument={argument}, values={values})".format(argument=self.arguments, values=self._values)


class StubEntry(object):

    def __init__(self, target, attribute, original):
        self._target = target
        self._attribute = attribute
        self._original = original

    def unstub(self):
        setattr(self._target, self._attribute, self._original)


class CallEntry(object):
    def __init__(self, target, attribute):
        self._target = target
        self._target_name = target.__name__
        self._attribute_name = attribute

    def verify(self, target, attribute_name):
        if self._target == target and self._attribute_name == attribute_name:
            return True
        return False

    def __repr__(self):
        return 'call {target_name}.{attribute_name}()'.format(target_name=self._target_name,
                                                              attribute_name=self._attribute_name)


class Mock(object):

    def __init__(self, target, attribute_name):
        self._target_name = target.__name__
        self._target = __import__(self._target_name)
        self._attribute_name = attribute_name
        self._answers = []

    def __call__(self, *arguments):
        _calls.append(CallEntry(self._target, self._attribute_name))

        if not self._answers:
            return None

        for answer in self._answers:
            if answer.arguments == arguments:
                return answer.next()

        return None

    def append_new_answer(self, answer):
        self._answers.append(answer)

    def __str__(self):
        return "Mock(" + str(self._answers) + ")"


class MockConfigurator(object):

    def __init__(self, mock):
        self._mock = mock
        self._arguments = None
        self._answer = None

    def __call__(self, *arguments):
        self._arguments = arguments
        self._answer = Answer(self._arguments)
        self._mock.append_new_answer(self._answer)
        return self._answer


class Mocker(object):

    def __init__(self, target):
        self._target_name = target.__name__
        self._target = __import__(self._target_name)

    def __getattr__(self, name):
        if not hasattr(self._target, name):
            raise FluentMockException(MESSAGE_INVALID_ATTRIBUTE.format(target_name=self._target_name,
                                                                       attribute_name=name))

        original = getattr(self._target, name)
        _stubs.append(StubEntry(self._target, name, original))

        key = (self._target, name)
        if not key in _configurators:
            mock = Mock(self._target, name)
            mock_configurator = MockConfigurator(mock)
            setattr(self._target, name, mock)
            _configurators[key] = mock_configurator

        return _configurators[key]


class Verifier(object):

    def __init__(self, target):
        self._target_name = target.__name__
        self._target = target
        self._attribute_name = None

    def __getattr__(self, name):
        self._attribute_name = name

        if not hasattr(self._target, name):
            raise FluentMockException(self.format_message(MESSAGE_INVALID_ATTRIBUTE))

        return self

    def __call__(self):
        if not _calls:
            raise AssertionError(self.format_message(MESSAGE_NO_CALLS))

        for call in _calls:
            if call.verify(self._target, self._attribute_name):
                return

        raise AssertionError(self.format_message(MESSAGE_COULD_NOT_VERIFY))

    def format_message(self, message):
        return message.format(target_name=self._target_name, attribute_name=self._attribute_name)


class FluentMockException(Exception):
    pass


def when(target):
    return Mocker(target)


def unstub():
    global _calls, _stubs, _configurators

    for stub in _stubs:
        stub.unstub()

    _calls = []
    _stubs = []
    _configurators = {}


def get_stubs():
    return _stubs


def verify(target):
    return Verifier(target)
