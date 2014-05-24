#!/usr/bin/python
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

from fontTools import ttLib


def set_fstype(fontpath):
    font = ttLib.TTFont(fontpath)
    font['OS/2'].fsType = 0
    font.save(fontpath + '.fix')


def show_fstype(fontpath):
    font = ttLib.TTFont(fontpath)
    print(font['OS/2'].fsType)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help="Font file in OpenType (TTF/OTF) format")
    parser.add_argument('--autofix', action="store_true", help="Autofix font metrics")

    args = parser.parse_args()
    assert os.path.exists(args.filename)
    if args.autofix:
        set_fstype(args.filename)
    else:
        show_fstype(args.filename)
