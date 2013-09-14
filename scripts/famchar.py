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
"""
Script to find the character set coverage and misses for fonts in the given dir
"""
import sys, os, glob, pprint
from fontaine.font import Font

pp = pprint.PrettyPrinter(indent=4)

if len(sys.argv) < 2:
    print __doc__
    sys.exit()

workingDir = sys.argv[1]

if os.path.exists(workingDir):
    os.chdir(workingDir)
else:
    print __doc__
    sys.exit()
fonts = {}
result = {}
for filename in glob.glob("*.ttf"):
    fontaine = Font(filename)
    fonts[filename] = fontaine
for font in fonts.iteritems():
    fontfilename = font[0]
    result[fontfilename] = {}
    for charset, coverage, percentcomplete, missingchars in font[1].get_orthographies():
        charsetname = charset.common_name
        result[fontfilename][charsetname] = {}
        import ipdb; ipdb.set_trace()
        if charset.common_name == 'GWF latin':
            result[fontfilename][charsetname]['percentcomplete'] = percentcomplete
            result[fontfilename][charsetname]['missingchars'] = missingchars
        elif charset.common_name == 'Adobe Latin 3':
            result[fontfilename][charsetname]['percentcomplete'] = percentcomplete
            result[fontfilename][charsetname]['missingchars'] = missingchars
        else:
            del result[fontfilename][charsetname]
pp.pprint(result)