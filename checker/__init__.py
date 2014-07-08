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
import tests

from .base import run_suite, make_suite


def run_set(path, target, test_method=None, log=None):
    """ Return tests results for font file, target """
    import os
    assert os.path.exists(path), '%s does not exists' % path
    tests_suite = make_suite(path, target, test_method=test_method, log=log)
    return run_suite(tests_suite)


def parse_test_results(result):
    failures = map(lambda x: (x._testMethodName, x._err_msg),
                   result.get('failure', []))
    error = map(lambda x: (x._testMethodName, x._err_msg),
                result.get('error', []))
    success = map(lambda x: (x._testMethodName, 'ok'),
                  result.get('success', []))

    return {'success': success, 'error': error, 'failure': failures}
