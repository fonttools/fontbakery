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
import upstream_suite

from .base import make_suite, run_suite

def run_set(path):
    """ Return tests results for .ufo font in parameter """
    assert os.path.exists(path)
    return run_suite(make_suite(path))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ufo', default='')
    # parser.add_argument('filename', default='')
    parser.add_argument('unittest_args', nargs='*')

    args = parser.parse_args()
    # #@$%
    s = make_suite(args.ufo)
    run_suite(s)
