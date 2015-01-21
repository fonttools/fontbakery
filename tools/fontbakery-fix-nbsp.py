#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013, Google Inc.
#
# Author: Behdad Esfahbod (behdad a google com)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# A script for generating a HTML file containing copyright notices
# for all fonts found in a directory tree, using fontTools
import argparse
import logging
import sys
import os

from bakery_cli.fixers import NbspAndSpaceSameWidth
from bakery_cli.bakery import WhitespaceRemovingFormatter

description = ('Fixes TTF non-breaking-space glyph to exist'
               ' with same advanceWidth as space')
parser = argparse.ArgumentParser(description=description)
parser.add_argument('ttf_font', nargs='+',
                    help='Font in OpenType (TTF/OTF) format')
parser.add_argument('--autofix', action='store_true', help='Apply autofix')

args = parser.parse_args()


logger = logging.getLogger('fontbakery')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler(stream=sys.stdout)
ch.setLevel(logging.DEBUG)

# create formatter
formatter = WhitespaceRemovingFormatter('%(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

for path in args.ttf_font:
    if not os.path.exists(path):
        continue

    fixer = NbspAndSpaceSameWidth(None, path)

    if args.autofix:
        fixer.apply()
    else:
        fixer.fix(check=True)  # this will print only
