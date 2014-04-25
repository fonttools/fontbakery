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

import sys
# TODO DC can the following 2 lines be removed?
# hardcoded for OSX
# sys.path.append('/usr/local/lib/python2.7/site-packages/')
print "Input: %s, Output: %s %s" % (sys.argv[1], sys.argv[2], sys.argv[3])

import fontforge

font = fontforge.open(sys.argv[1])

if sys.argv[3]:
    otf = font.generate(sys.argv[3])

# Convert curves to quadratic
font.layers["Fore"].is_quadratic = True
# Select all glyphs
font.selection.all()
#   Add Extrema
font.addExtrema()
#   Simplify
try:
    font.simplify(1,('setstarttoextremum','removesingletonpoints'))
except:
    print "Error: Could not simplify"
    pass
#   Correct Directions
font.correctDirection()

ttf = font.generate(sys.argv[2])
