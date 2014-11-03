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


description = 'Fixes TTF NAME table style names to be canonical'

parser = argparse.ArgumentParser(description=description)
parser.add_argument('ttf_font', nargs='+',
                    help="Font file in OpenType (TTF/OTF) format")
parser.add_argument('--autofix', action="store_true")

args = parser.parse_args()


for path in args.ttf_font:
    if not os.path.exists(path):
        continue
    if args.autofix:
        stylenames.fix_style_names(path)
    else:
        stylenames.show_stylenames(path)
