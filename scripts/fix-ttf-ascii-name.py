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

import os
from fontTools import ttLib


def fix_ascii(string):
    if b'\000' in string:
        string = string.decode('utf-16-be').encode('utf-8')
    else:
        string = string

    string = string.replace(u'©', '(C)')
    string = string.replace(u'™', '(TM)')
    string = string.replace(u'®', '(R)')
    return string.encode('utf-16-be')


def fix_name_table(fontfile):
    font = ttLib.TTFont(fontfile)
    for name_record in font['name'].names:
        name_record.string = fix_ascii(name_record.string)
    font.save(fontfile)


def show_name_table(fontfile):
    pass


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--autofix', action="store_true", help="Autofix font ascii name")
    parser.add_argument('filename', help="Font file in TTF format")

    args = parser.parse_args()
    assert os.path.exists(args.filename)
    if args.autofix:
        fix_name_table(args.filename)
    else:
        show_name_table(args.filename)
