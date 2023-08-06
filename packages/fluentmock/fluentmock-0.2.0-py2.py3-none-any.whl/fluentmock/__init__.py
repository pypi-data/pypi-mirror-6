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
__version__ = '0.2.0'

__all__ = ['ANY_ARGUMENT',
           'ANY_ARGUMENTS',
           'AT_LEAST_ONCE',
           'NEVER',
           'UnitTests',
           'create_mock',
           'verify',
           'when']

try:
    from importlib import import_module
except ImportError as import_error:
    print(str(import_error))
    print('fluentmock does not define importlib as a dependency,')
    print('because importlib is part of the standard library')
    print('starting with Python version 2.7')
    print('')
    print('Please install importlib using "pip install importlib".')

from mock import Mock, call, patch
from logging import getLogger
from unittest import TestCase
from types import ModuleType

from fluentmock.exceptions import (CouldNotVerifyCallError,
                                   FoundMatcherInNativeVerificationError,
                                   HasBeenCalledAtLeastOnceError,
                                   InvalidAttributeError,
                                   InvalidUseOfAnyArgumentsError,
                                   NoCallsStoredError,
                                   HasBeenCalledWithUnexpectedArgumentsError)
from fluentmock.matchers import FluentMatcher, FluentAnyArguments, FluentAnyArgument

LOGGER = getLogger(__name__)

ANY_ARGUMENT = FluentAnyArgument()
ANY_ARGUMENTS = FluentAnyArguments()
AT_LEAST_ONCE = 'AT-LEAST-ONCE'
NEVER = 'NEVER'

_configurators = {}
_patch_entries = []
_call_entries = []


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


class FluentTarget(object):

    def __init__(self, target, attribute_name=None):
        if isinstance(target, str):
            self.name = target
            self.object = import_module(self.name)
        elif isinstance(target, ModuleType):
            self.name = target.__name__
            self.object = import_module(self.name)
        else:
            target_type = type(target)
            self.name = target_type.__module__ + '.' + target_type.__name__
            self.object = target

        if attribute_name is not None and not hasattr(self.object, attribute_name):
            raise InvalidAttributeError(self.name, attribute_name)

        self.attribute_name = attribute_name

    @property
    def full_qualified_target_name(self):
        return self.name + '.' + self.attribute_name

    def is_equal_to(self, target, attribute_name):
        return self.object == target and self.attribute_name == attribute_name

    def __repr__(self):
        return self.full_qualified_target_name


class FluentCallEntry(object):

    def __init__(self, target, attribute_name, arguments, keyword_arguments):
        self.target = FluentTarget(target, attribute_name)
        self.arguments = arguments
        self.keyword_arguments = keyword_arguments

    def matches(self, target, attribute_name, arguments, keyword_arguments):
        if not self.target.is_equal_to(target, attribute_name):
            return False

        if self.arguments and self.arguments[0] is ANY_ARGUMENTS:
            return True

        if self.arguments == arguments and self.keyword_arguments == keyword_arguments:
            return True

        if len(self.arguments) != len(arguments):
            return False

        if len(self.keyword_arguments) != len(keyword_arguments):
            return False

        for index, argument in enumerate(arguments):
            value = self.arguments[index]
            if isinstance(value, FluentMatcher):
                if not value.matches(argument):
                    return False
            elif isinstance(argument, FluentMatcher):
                if not argument.matches(value):
                    return False
            elif value != argument:
                return False

        if len(self.keyword_arguments) > 0:
            for key in self.keyword_arguments.keys():
                if key not in keyword_arguments:
                    return False

            for key in self.keyword_arguments.keys():
                if isinstance(self.keyword_arguments[key], FluentMatcher):
                    if not self.keyword_arguments[key].matches(keyword_arguments[key]):
                        return False
                elif self.keyword_arguments[key] != keyword_arguments[key]:
                    return False

        return True

    def __repr__(self):
        call_object = call(*self.arguments, **self.keyword_arguments)
        call_string = str(call_object)
        return call_string[:4] + ' ' + str(self.target) + call_string[4:]


class FluentAnswer(FluentCallEntry):

    class AnswerByReturning(object):

        def __init__(self, value):
            self._value = value

        def __call__(self):
            return self._value

    class AnswerByRaising(object):

        def __init__(self, value):
            self._value = value

        def __call__(self):
            raise self._value

    def __init__(self, target, attribute_name, arguments, keyword_arguments):
        FluentCallEntry.__init__(self, target, attribute_name, arguments, keyword_arguments)
        self.arguments = arguments
        self.keyword_arguments = keyword_arguments
        self._answers = []

    def next(self):
        if len(self._answers) == 0:
            return None
        elif len(self._answers) == 1:
            answer = self._answers[0]
        else:
            answer = self._answers.pop(0)

        return answer()

    def then_return(self, value):
        answer = self.AnswerByReturning(value)
        self._answers.append(answer)
        return self

    def then_raise(self, value):
        answer = self.AnswerByRaising(value)
        self._answers.append(answer)
        return self


class FluentPatchEntry(object):

    def __init__(self, target, attribute_name):
        self.target = FluentTarget(target, attribute_name)

        self._patch = None

    def patch_away_with(self, fluent_mock):
        if isinstance(self.target.object, Mock):
            setattr(self.target.object, self.target.attribute_name, fluent_mock)
        else:
            self._patch = patch(self.target.full_qualified_target_name)
            mock = self._patch.__enter__()
            mock.side_effect = fluent_mock

    def undo(self):
        if self._patch:
            self._patch.__exit__()


class FluentMock(FluentTarget):

    def __init__(self, target, attribute_name):
        FluentTarget.__init__(self, target, attribute_name)
        self._answers = []

    def __call__(self, *arguments, **keyword_arguments):
        call_entry = FluentCallEntry(self.object, self.attribute_name, arguments, keyword_arguments)
        _call_entries.append(call_entry)

        for answer in self._answers:
            if answer.matches(self.object, self.attribute_name, arguments, keyword_arguments):
                return answer.next()

        return None

    def append_new_answer(self, answer):
        self._answers.append(answer)


class FluentMockConfigurator(object):

    def __init__(self, fluent_mock):
        self._fluent_mock = fluent_mock

    def __call__(self, *arguments, **keyword_arguments):
        if len(arguments) > 1 and ANY_ARGUMENTS in arguments:
            raise InvalidUseOfAnyArgumentsError()

        answer = FluentAnswer(self._fluent_mock.object, self._fluent_mock.attribute_name, arguments, keyword_arguments)
        self._fluent_mock.append_new_answer(answer)
        return answer


class FluentWhen(FluentTarget):

    def __init__(self, target):
        FluentTarget.__init__(self, target)

    def __getattr__(self, attribute_name):
        patch_entry = FluentPatchEntry(self.object, attribute_name)
        _patch_entries.append(patch_entry)

        configurator_key = (self.object, attribute_name)
        if not configurator_key in _configurators:
            fluent_mock = FluentMock(self.object, attribute_name)
            mock_configurator = FluentMockConfigurator(fluent_mock)
            patch_entry.patch_away_with(fluent_mock)
            _configurators[configurator_key] = mock_configurator

        return _configurators[configurator_key]


class Verifier(FluentTarget):

    def __init__(self, target, times):
        FluentTarget.__init__(self, target)
        self._times = times

        if times not in [NEVER, AT_LEAST_ONCE]:
            error_message = 'Argument times can be "{never}" or "{once}".'.format(never=NEVER, once=AT_LEAST_ONCE)
            raise ValueError(error_message)

    def __getattr__(self, attribute_name):
        self.attribute_name = attribute_name

        if not hasattr(self.object, attribute_name):
            raise InvalidAttributeError(self.name, attribute_name)

        return self

    def __call__(self, *arguments, **keyword_arguments):
        method_of_mock = getattr(self.object, self.attribute_name)
        if isinstance(self.object, Mock) and isinstance(method_of_mock, Mock):
            call_entry = call(*arguments, **keyword_arguments)
            call_entry_string = str(call_entry).replace('call', self.full_qualified_target_name)

            for argument in arguments:
                if isinstance(argument, FluentMatcher):
                    raise FoundMatcherInNativeVerificationError(call_entry_string)

            for key in keyword_arguments:
                if isinstance(keyword_arguments[key], FluentMatcher):
                    raise FoundMatcherInNativeVerificationError(call_entry_string)

            if self._times == NEVER:
                if call_entry in method_of_mock.call_args_list:
                    raise HasBeenCalledAtLeastOnceError(call_entry_string)
            else:
                method_of_mock.assert_called_with(*arguments, **keyword_arguments)
        else:
            if self._times == NEVER:
                self._assert_never_called(*arguments, **keyword_arguments)
            else:
                self._assert_called(*arguments, **keyword_arguments)

    def _assert_never_called(self, *arguments, **keyword_arguments):
        for call_entry in _call_entries:
            if call_entry.matches(self.object, self.attribute_name, arguments, keyword_arguments):
                raise HasBeenCalledAtLeastOnceError(call_entry)

    def _assert_called(self, *arguments, **keyword_arguments):
        expected_call_entry = FluentCallEntry(self.object, self.attribute_name, arguments, keyword_arguments)

        if not _call_entries:
            raise NoCallsStoredError(expected_call_entry)

        for call_entry in _call_entries:
            if call_entry.matches(self.object, self.attribute_name, arguments, keyword_arguments):
                return

        found_calls = self._find_calls_to_same_target()

        if found_calls:
            if arguments and ANY_ARGUMENTS in arguments:
                if len(arguments) > 1:
                    raise InvalidUseOfAnyArgumentsError()
                return
            raise HasBeenCalledWithUnexpectedArgumentsError(expected_call_entry, found_calls)

        raise CouldNotVerifyCallError(expected_call_entry)

    def _find_calls_to_same_target(self):
        found_calls = []

        for call_entry in _call_entries:
            target = call_entry.target
            if target.is_equal_to(self.object, self.attribute_name):
                found_calls.append(call_entry)

        return found_calls


def create_mock(*arguments, **keyword_arguments):
    if len(arguments) > 0:
        specification = arguments[0]
        mock = Mock(specification)
    else:
        mock = Mock()

    for property_name in keyword_arguments.keys():
        setattr(mock, property_name, keyword_arguments[property_name])

    return mock


def undo_patches():
    global _call_entries, _patch_entries, _configurators

    for patch_entry in _patch_entries:
        patch_entry.undo()

    _call_entries = []
    _patch_entries = []
    _configurators = {}


def get_patches():
    return _patch_entries


def when(target):
    return FluentWhen(target)


def verify(target, times=AT_LEAST_ONCE):
    return Verifier(target, times)
