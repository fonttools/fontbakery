#!/usr/bin/env python
# Copyright 2016 The Fontbakery Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import glyphsLib
import os


parent_dir = '/Users/marc/Documents/googlefonts/manual_font_cleaning/'
possible_var_fonts = []
almost_possible_var_fonts = []

for root, dirs, files in os.walk(parent_dir, topdown=False):
    for f in files:
        if '.glyphs' in f:
            try:
                with open(os.path.join(root, f)) as glyphs_file:
                    glyphs_source = glyphsLib.load(glyphs_file)

                    master_count = len(glyphs_source['fontMaster'])
                    instance_count = len(glyphs_source['instances'])

                    if master_count >= 2 and instance_count >= 3:
                        possible_var_fonts.append(
                            (glyphs_source['familyName'],
                             len(glyphs_source['fontMaster']),
                             len(glyphs_source['instances']))
                        )
                    elif master_count >= 2 and instance_count == master_count:
                        almost_possible_var_fonts.append(
                            (glyphs_source['familyName'],
                             len(glyphs_source['fontMaster']),
                             len(glyphs_source['instances']))
                        )
            except:
                all


text = []
text.append('POSSIBLE VARIABLE FONTS')
for family in set([i[0] for i in possible_var_fonts]):
    text.append(family)

text.append('\n')
text.append('ALMOST POSSIBLE VARIABLE FONTS')
for family in set([i[0] for i in almost_possible_var_fonts]):
    text.append(family)


with open('possible_variable_fonts', 'w') as doc:
    doc.write('\n'.join(text))
