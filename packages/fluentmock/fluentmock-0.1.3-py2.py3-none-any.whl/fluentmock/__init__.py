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

__author__ = 'Michael Gruber'
__version__ = '0.1.3'

from importlib import import_module
from mock import Mock, patch
from logging import getLogger
from unittest import TestCase
from types import ModuleType

LOGGER = getLogger(__name__)


MESSAGE_COULD_NOT_VERIFY = 'Could not verify {target_name}.{attribute_name}{arguments}'
MESSAGE_COULD_NOT_VERIFY_NEVER = 'Could not verify {target_name}.{attribute_name}{arguments} has never been called.'
MESSAGE_HAS_BEEN_CALLED_AT_LEAST_ONCE = """{target_name}.{attribute_name}{arguments} should NEVER have been called, but
has been called at least once."""
MESSAGE_INVALID_ATTRIBUTE = 'The target "{target_name}" has no attribute called "{attribute_name}".'
MESSAGE_NO_CALLS = """
Expected: call {target_name}.{attribute_name}()
 but was: no patched function has been called.
"""
MESSAGE_EXPECTED_BUT_WAS = """
Expected: {expected}
 but was: {actual}
"""

NEVER = 0

_configurators = {}
_patches = []
_calls = []


class UnitTests(TestCase):

    def setUp(self):
        self.set_up()

    def tearDown(self):
        self.tear_down()
        undo_patches()

    def set_up(self):
        """ Override this method to set up your unit test environment """
        pass

    def tear_down(self):
        """ Override this method to tear down your unit test environment """
        pass


class FluentAnyArguments(object):
    pass


ANY_ARGUMENTS = FluentAnyArguments()


class FluentTargeting(object):

    def __init__(self, target):
        if isinstance(target, ModuleType):
            self._target_name = target.__name__
            self._target = import_module(self._target_name)
        else:
            target_type = type(target)
            self._target_name = target_type.__module__ + '.' + target_type.__name__
            self._target = target


class FluentAnswer(object):

    RETURN_ANSWER = 0
    RAISE_ANSWER = 1

    def __init__(self, arguments):
        self.arguments = arguments
        self._answers = []

    def next(self):
        if len(self._answers) == 0:
            return None

        if len(self._answers) == 1:
            value = self._answers[0]

        if len(self._answers) > 1:
            value = self._answers.pop(0)

        return self.give_answer(value)

    def give_answer(self, answer):
        answer_type = answer[1]
        answer_value = answer[0]
        if answer_type == self.RETURN_ANSWER:
            return answer_value

        if answer_type == self.RAISE_ANSWER:
            raise answer_value

        raise NotImplementedError('The answer type %s is not implemented')

    def then_return(self, value):
        self._answers.append((value, self.RETURN_ANSWER))
        return self

    def then_raise(self, value):
        self._answers.append((value, self.RAISE_ANSWER))
        return self

    def __repr__(self):
        return "Answer(arguments={arguments}, values={values})".format(arguments=self.arguments, values=self._answers)


class FluentPatchEntry(FluentTargeting):

    def __init__(self, target, attribute_name, original):
        FluentTargeting.__init__(self, target)
        self._attribute_name = attribute_name
        self._original = original
        self._patch = None
        self._mock = None
        self._full_qualified_target_name = None

    def patch_away_with(self, fluent_mock):
        if isinstance(self._target, Mock):
            setattr(self._target, self._attribute_name, fluent_mock)
        else:
            self._full_qualified_target_name = self._target_name + '.' + self._attribute_name
            self._patch = patch(self._full_qualified_target_name)
            self._mock = self._patch.__enter__()
            self._mock.side_effect = fluent_mock

    def undo(self):
        if self._patch:
            self._patch.__exit__()


class FluentCallEntry(FluentTargeting):
    def __init__(self, target, attribute, arguments):
        FluentTargeting.__init__(self, target)
        self._attribute_name = attribute
        self._arguments = arguments

    def verify(self, target, attribute_name, arguments):
        if self._target == target and self._attribute_name == attribute_name and self._arguments == arguments:
            return True
        return False

    def __repr__(self):
        arguments_as_strings = []
        for argument in self._arguments:
            if type(argument) == str:
                arguments_as_strings.append("'{argument}'".format(argument=argument))
            else:
                arguments_as_strings.append(str(argument))

        arguments = ", ".join(arguments_as_strings)
        return 'call {target_name}.{attribute_name}({arguments})'.format(target_name=self._target_name,
                                                                         attribute_name=self._attribute_name,
                                                                         arguments=arguments)


class FluentMock(FluentTargeting):

    def __init__(self, target, attribute_name):
        FluentTargeting.__init__(self, target)
        self._attribute_name = attribute_name
        self._answers = []

    def __call__(self, *arguments):
        _calls.append(FluentCallEntry(self._target, self._attribute_name, arguments))

        if not self._answers:
            return None

        for answer in self._answers:
            if answer.arguments == arguments:
                return answer.next()
            if answer.arguments and answer.arguments[0] == ANY_ARGUMENTS:
                return answer.next()

        return None

    def append_new_answer(self, answer):
        self._answers.append(answer)

    def __str__(self):
        return "Mock(" + str(self._answers) + ")"


class FluentMockConfigurator(object):

    def __init__(self, mock):
        self._mock = mock
        self._arguments = None
        self._answer = None

    def __call__(self, *arguments):
        self._arguments = arguments
        self._answer = FluentAnswer(self._arguments)
        self._mock.append_new_answer(self._answer)
        return self._answer


class FluentWhen(FluentTargeting):

    def __init__(self, target):
        FluentTargeting.__init__(self, target)

    def _get_original_attribute(self, name):

        if not hasattr(self._target, name):
            error_message = MESSAGE_INVALID_ATTRIBUTE.format(target_name=self._target_name, attribute_name=name)
            raise FluentMockException(error_message)

        return getattr(self._target, name)

    def __getattr__(self, name):
        original = self._get_original_attribute(name)
        patch_entry = FluentPatchEntry(self._target, name, original)
        _patches.append(patch_entry)

        key = (self._target, name)
        if not key in _configurators:
            fluent_mock = FluentMock(self._target, name)
            mock_configurator = FluentMockConfigurator(fluent_mock)
            patch_entry.patch_away_with(fluent_mock)
            _configurators[key] = mock_configurator

        return _configurators[key]


class Verifier(FluentTargeting):

    def __init__(self, target, times):
        FluentTargeting.__init__(self, target)
        self._attribute_name = None
        self._times = times

        if times not in [0, 1]:
            raise NotImplementedError('Times can be 0 or 1.')

    def __getattr__(self, name):
        self._attribute_name = name

        if not hasattr(self._target, name):
            raise FluentMockException(self.format_message(MESSAGE_INVALID_ATTRIBUTE))

        return self

    def _assert_called(self, *arguments):
        if not _calls:
            raise AssertionError(self.format_message(MESSAGE_NO_CALLS))

        for call in _calls:
            if call.verify(self._target, self._attribute_name, arguments):
                return

        found_calls = []

        for call in _calls:
            if call._target == self._target and call._attribute_name == self._attribute_name:
                found_calls.append(call)

        number_of_found_calls = len(found_calls)
        if number_of_found_calls > 0:
            expected_call_entry = FluentCallEntry(self._target, self._attribute_name, arguments)
            error_message = MESSAGE_EXPECTED_BUT_WAS.format(expected=expected_call_entry, actual=found_calls[0])
            if number_of_found_calls > 1:
                for call in found_calls[1:]:
                    error_message += '          {call}\n'.format(call=call)
            raise AssertionError(error_message)

        raise AssertionError(self.format_message(MESSAGE_COULD_NOT_VERIFY, arguments))

    def __call__(self, *arguments):
        if self._times == 0:
            if not _calls:
                return

            for call in _calls:
                if call.verify(self._target, self._attribute_name, arguments):
                    raise AssertionError(self.format_message(MESSAGE_HAS_BEEN_CALLED_AT_LEAST_ONCE, arguments))

            return
        else:
            self._assert_called(*arguments)

    def format_message(self, message, arguments='()'):
        return message.format(target_name=self._target_name, attribute_name=self._attribute_name, arguments=arguments)


class FluentMockException(Exception):
    pass


def when(target):
    return FluentWhen(target)


def undo_patches():
    global _calls, _patches, _configurators

    for _patch in _patches:
        _patch.undo()

    _calls = []
    _patches = []
    _configurators = {}


def get_patches():
    return _patches


def verify(target, times=1):
    return Verifier(target, times)
