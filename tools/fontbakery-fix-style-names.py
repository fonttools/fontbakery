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
import argparse
import os


from bakery_cli.scripts import stylenames


parser = argparse.ArgumentParser()
parser.add_argument('font',
                    help="Font file in OpenType (TTF/OTF) format")
parser.add_argument('--autofix', action="store_true",
                    help="Autofix font metrics")

args = parser.parse_args()
assert os.path.exists(args.font)
if args.autofix:
    stylenames.fix_style_names(args.font)
else:
    stylenames.show_stylenames(args.font)
