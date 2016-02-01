#!/usr/bin/env python
# coding: utf-8
# Copyright 2015 The Font Bakery Authors. All Rights Reserved.
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
import argparse
import os

from bakery_cli.fixers import VersionFixer


if __name__ == '__main__':
    description = 'Fixes version entries'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('otf_font', nargs='+',
                        help="Font whose version entries will be read and fixed")
    parser.add_argument('--increment-major', action='store_true', help='Increment version major values')
    parser.add_argument('--increment-minor', action='store_true', help='Increment version minor values')
    parser.add_argument('--set', nargs=1, help='Set version values')

    options = parser.parse_args()

    for path in options.otf_font:
        if not os.path.exists(path):
            continue
        fixer = VersionFixer(None, path)
        fixer.apply(options)
