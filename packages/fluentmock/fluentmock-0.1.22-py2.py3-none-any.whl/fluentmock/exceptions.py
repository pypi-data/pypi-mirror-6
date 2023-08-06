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


class CouldNotVerifyCallError(AssertionError):

    MESSAGE_FORMAT = 'Could not verify {expected}'

    def __init__(self, expected_call_entry):
        error_message = self.MESSAGE_FORMAT.format(expected=expected_call_entry)
        super(CouldNotVerifyCallError, self).__init__(error_message)


class InvalidAttributeError(Exception):

    MESSAGE_FORMAT = 'The target "{target_name}" has no attribute called "{attribute_name}".'

    def __init__(self, target_name, attribute_name):
        error_message = self.MESSAGE_FORMAT.format(target_name=target_name, attribute_name=attribute_name)
        super(InvalidAttributeError, self).__init__(error_message)


class InvalidUseOfAnyArgumentsError(AssertionError):

    MESSAGE_FORMAT = """Do not use ANY_ARGUMENTS together with other arguments!
Use ANY_ARGUMENT as a wildcard for single arguments."""

    def __init__(self):
        super(InvalidUseOfAnyArgumentsError, self).__init__(self.MESSAGE_FORMAT)


class HasBeenCalledAtLeastOnceError(AssertionError):

    MESSAGE_FORMAT = """{call_entry} should NEVER have been called,
but has been called at least once."""

    def __init__(self, call_entry):
        error_message = self.MESSAGE_FORMAT.format(call_entry=call_entry)
        super(HasBeenCalledAtLeastOnceError, self).__init__(error_message)


class HasBeenCalledWithUnexpectedArgumentsError(AssertionError):

    MESSAGE_FORMAT = """
Expected: {expected}
 but was: {actual}
"""
    ADDITIONAL_CALL_ENTRIES = ' ' * 10 + '{actual}\n'

    def __init__(self, expected_call_entry, found_calls):

        error_message = self.MESSAGE_FORMAT.format(expected=expected_call_entry, actual=found_calls[0])
        if len(found_calls) > 1:
            for call_entry in found_calls[1:]:
                error_message += self.ADDITIONAL_CALL_ENTRIES.format(actual=call_entry)

        super(HasBeenCalledWithUnexpectedArgumentsError, self).__init__(error_message)


class NoCallsStoredError(AssertionError):

    MESSAGE_FORMAT = """
Expected: {expected}
 but was: no patched function has been called.
"""

    def __init__(self, expected_call_entry):
        error_message = self.MESSAGE_FORMAT.format(expected=expected_call_entry)
        super(NoCallsStoredError, self).__init__(error_message)


class FoundMatcherInNativeVerificationError(AssertionError):

    MESSAGE_FORMAT = """
You were trying to verify {expected_call_entry}
fluentmock.verify will call Mock.assert_called_with for verification
when the Mock has not been configured using fluentmock.when
Therefore it is not possible to use matchers when verifying
a Mock without configuring it with fluentmock.when,
because Mock.assert_called_with does not support matchers.
Please configure your mock in order to be able to use a matcher.
"""

    def __init__(self, expected_call_entry):
        error_message = self.MESSAGE_FORMAT.format(expected_call_entry=expected_call_entry)
        super(FoundMatcherInNativeVerificationError, self).__init__(error_message)
