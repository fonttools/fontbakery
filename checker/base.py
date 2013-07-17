# coding: utf-8
# Copyright 2013 The Font Bakery Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# See AUTHORS.txt for the list of Authors and LICENSE.txt for the License.

import unittest

class TestRegistry(object):
    """ Singleton class to collect all available tests """
    tests = []

    @classmethod
    def register(cls, test):
        if not test in TestRegistry.tests:
            TestRegistry.tests.append(test)

    @classmethod
    def list(cls):
        return TestRegistry.tests

class MetaTest(type):
    """
    Class for all tests
    """
    def __new__(mcs, name, bases, attrs):
        abstract = attrs.pop('__abstract__', None)
        newbornclass = super(MetaTest, mcs).__new__(mcs, name, bases, attrs)
        if not abstract:
            TestRegistry.register(newbornclass)
        return newbornclass

class BakeryTestCase(unittest.TestCase):
    __metaclass__ = MetaTest
    # because we don't want to register this base class as test case
    __abstract__ = True


class BakeryTestResult(unittest.TestResult):

    def __init__(self, stream=None, descriptions=None, verbosity=None,
            success_list=None, error_list=None, failure_list=None):
        self.sl = success_list
        self.el = error_list
        self.fl = failure_list
        super(BakeryTestResult, self).__init__(self)

    def startTest(self, test):
        super(BakeryTestResult, self).startTest(test)

    def addSuccess(self, test):
        super(BakeryTestResult, self).addSuccess(test)
        if hasattr(self.sl, 'append'):
            self.sl.append(test)

    def addError(self, test, err):
        super(BakeryTestResult, self).addError(test, err)
        if hasattr(self.el, 'append'):
            self.el.append(test)

    def addFailure(self, test, err):
        super(BakeryTestResult, self).addFailure(test, err)
        if hasattr(self.fl, 'append'):
            self.fl.append(test)

class BakeryTestRunner(unittest.TextTestRunner):
    def __init__(self, descriptions=True, verbosity=1, resultclass=None,
            success_list=None, error_list=None, failure_list=None):

        self.sl = success_list
        self.el = error_list
        self.fl = failure_list

        self.results = []
        self.descriptions = descriptions
        self.verbosity = verbosity
        if resultclass is not None:
            self.resultclass = resultclass
        super(BakeryTestRunner, self).__init__(self)

    def _makeResult(self):
        return self.resultclass(self.stream, self.descriptions,
            self.verbosity, self.sl, self.el, self.fl)

    def run(self, test):
        "Run the given test case or test suite."
        result = self._makeResult()
        test(result)
        self.results.append(result)
        return result

