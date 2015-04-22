#!/usr/bin/env python
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
from __future__ import print_function
import argparse
import sys

from bakery_lint import run_set


if __name__ == '__main__':
    description = 'Runs checks or tests on specified METADATA.json file(s)'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('file', nargs="+", help="Test files, can be a list")
    parser.add_argument('--verbose', '-v', action='count',
                        help="Verbosity level", default=False)

    args = parser.parse_args()

    if not args.file:
        print("Missing files to test", file=sys.stderr)
        sys.exit(1)

    for x in args.file:

        if not x.lower().endswith('METADATA.json'):
            print('ER: {} is not METADATA.json'.format(x), file=sys.stderr)
            continue

        failures = []
        success = []
        error = []

        result = run_set('metadata', test)
        failures += [(testklass._testMethodName, testklass._err_msg)
                     for testklass in result.get('failure', [])]
        error += [(testklass._testMethodName, testklass._err_msg)
                  for testklass in result.get('error', [])]
        success += [(testklass._testMethodName, 'OK')
                    for testklass in result.get('success', [])]

        if not bool(failures + error):
            if args.verbose:
                for testmethod, dummyvar in success:
                    print('OK: {}'.format(testmethod))
        else:
            for testmethod, errormessage in error:
                print('ER: {}: {}'.format(testmethod, errormessage))
            if args.verbose:
                for testmethod, dummyvar in success:
                    print('OK: {}'.format(testmethod))
            for testmethod, errormessage in failures:
                print('FAIL: {}: {}'.format(testmethod, errormessage))
