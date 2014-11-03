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
import os

from bakery_cli.scripts import nbsp


parser = argparse.ArgumentParser()
parser.add_argument('font', help='Font in OpenType (TTF/OTF) format')
parser.add_argument('--autofix', action='store_true', help='Apply autofix')

args = parser.parse_args()
assert os.path.exists(args.font)
nbsp.run(args.font)
