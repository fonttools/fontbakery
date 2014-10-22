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

from __future__ import print_function
import logging

import fontforge


log = logging.getLogger(__name__)


def convert(sourceFont, ttf, otf=None, log=log):
    try:
        font = fontforge.open(sourceFont)
    except:
        log.info("Error: Could not open font (%s)" % sourceFont)
        return

    font.selection.all()

    # Remove overlap
    try:
        font.removeOverlap()
    except:
        log.info("Error: Could not remove overlaps")

    if otf:
        try:
            font.generate(otf)
            log.info("OK: Generated OpenType-CFF (%s)" % otf)
        except:
            log.info("Error: Could not generate OpenType-CFF (%s)" % otf)

    # Convert curves to quadratic (TrueType)
    try:
        font.layers["Fore"].is_quadratic = True
    except:
        log.info("Error: Could not convert to quadratic TrueType curves")
        return

    # Simplify
    try:
        font.simplify(1, ('setstarttoextremum',
                          'removesingletonpoints',
                          'mergelines'))
    except:
        log.info("Error: Could not simplify")

    # Correct Directions
    try:
        font.correctDirection()
    except:
        log.info("Error: Could not correct directions")

    # Generate with DSIG and OpenType tables
    try:
        flags = ('dummy-dsig', 'opentype')
        font.generate(ttf, flags=flags)
        log.info("Success: Generated OpenType-TTF (%s)" % ttf)
    except:
        log.info("Error: Could not generate OpenType-TTF (%s)" % ttf)
        return
