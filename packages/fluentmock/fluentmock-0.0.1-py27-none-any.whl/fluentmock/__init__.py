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
__version__ = '0.0.1'


from logging import getLogger
from mock import MagicMock

LOGGER = getLogger(__name__)


class Answer(object):

    def __init__(self, parent):
        self.value = None
        self._parent = parent
        self._already_configured_answer = False

    def then_return(self, value):
        if not self._already_configured_answer:
            self._already_configured_answer = True
            self.value = value
            return self
        else:
            return self._parent.new_answer().then_return(value)

    def __repr__(self):
        return "Answer(value=%s)" % self.value


class MockWrapper(object):

    def __init__(self, target_module):
        self._target_module = __import__(target_module.__name__)
        self._mocks = {}
        self._answers = []

    def __getattr__(self, name):
        mock = MagicMock()
        mock.side_effect = self._side_effect
        setattr(self._target_module, name, mock)
        self._mocks[name] = mock
        return self

    def new_answer(self):
        answer = Answer(self)
        self._answers.append(answer)
        return answer

    def __call__(self, *args, **kwargs):
        return self.new_answer()

    def _side_effect(self, *args, **kwargs):
        if len(self._answers) > 1:
            answer = self._answers.pop(0)
        else:
            answer = self._answers[0]
        return answer.value

    def __repr__(self):
        return "MockWrapper(answers=" + str(self._answers) + ")"


def when(target):
    return MockWrapper(target)
