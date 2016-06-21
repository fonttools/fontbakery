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
import unicodedata
from unidecode import unidecode
from fontTools import ttLib

def unicode_marks(string):
    unicodemap = [(u'©', '(c)'), (u'®', '(r)'), (u'™', '(tm)')]
    return filter(lambda char: char[0] in string, unicodemap)

def normalizestr(string):
    """ Converts special characters like copyright,
        trademark signs to ascii name """
    #print("input: '{}'".format(string))
    input_string = string
    for mark, ascii_repl in unicode_marks(string):
        string = string.replace(mark, ascii_repl)

    rv = []
#    for c in unicodedata.normalize('NFKC', smart_text(string)):
    for c in unicodedata.normalize('NFKC', string):
        #cat = unicodedata.category(c)[0]
        #if cat in 'LN' or c in ok:
        rv.append(c)

    new = ''.join(rv).strip()
    result = unidecode(new)
    if result != input_string:
        print("Fixed string: '{}'".format(result))
    return result

description = 'Fixes TTF NAME table strings to be ascii only'
parser = argparse.ArgumentParser(description=description)
parser.add_argument('ttf_font', nargs='+',
                    help="Font in OpenType (TTF/OTF) format")

args = parser.parse_args()
for path in args.ttf_font:
    font = ttLib.TTFont(path)
    for name in font['name'].names:
        title = name.string.decode(name.getEncoding())
        title = normalizestr(title)
        name.string = title.encode(name.getEncoding())

