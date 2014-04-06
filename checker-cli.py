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

import argparse, os
import unittest
import sys

from checker.base import make_suite, run_suite, tests_report
from checker import run_set

def run_set1(path):
    """ Return tests results for .ttf font in parameter """
    assert os.path.exists(path)
    return run_suite(make_suite(path, 'result'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action',
        help="Action or target test suite",
        choices=['list', 'result', 'upstream', 'upstream-ttx', 'metadata'],)
    parser.add_argument('file', nargs="*", help="Test files, can be a list")
    parser.add_argument('--verbose', '-v', action='count', help="Verbosity level", default=1)

    args = parser.parse_args()
    if args.action == 'list':
        tests_report()
        sys.exit()

    if not args.file:
        print("Missing files to test")
        sys.exit(1)

    for x in args.file:
        print(x)
        run_set(x, 'metadata')
        # s = make_suite(x, args.action)
        # runner = unittest.TextTestRunner(verbosity=args.verbose)
        # # run_suite(s)
        # runner.run(s)
