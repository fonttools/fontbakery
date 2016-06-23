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
#
# Convert a source font into OpenType-TTF and optionally also OpenType-CFF
#
# $ fontbakery-build-font2ttf.py font.sfd font.ttf font.otf
# $ fontbakery-build-font2ttf.py font.sfdir font.ttf font.otf
# $ fontbakery-build-font2ttf.py font.ufo font.ttf font.otf
# $ fontbakery-build-font2ttf.py font.otf font.ttf
from __future__ import print_function

import argparse
import fontforge
import logging
import os
import sys

log_format = '%(levelname)-8s %(message)s'
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(log_format)
handler.setFormatter(formatter)
logger.addHandler(handler)


def convert(sourceFont, ttf, otf=None):
    try:
        font = fontforge.open(sourceFont)
    except:
        logger.error("Error: Could not open font (%s)" % sourceFont)
        return

    font.selection.all()

    # Remove overlap
    try:
        font.removeOverlap()
    except:
        logger.error("Error: Could not remove overlaps")

    if otf:
        try:
            font.generate(otf)
            logger.info("OK: Generated OpenType-CFF (%s)" % otf)
        except:
            logger.error("Error: Could not generate OpenType-CFF (%s)" % otf)

    # Convert curves to quadratic (TrueType)
    try:
        font.layers["Fore"].is_quadratic = True
    except:
        logger.error("Error: Could not convert to quadratic TrueType curves")
        return

    # Simplify
    try:
        font.simplify(1, ('setstarttoextremum',
                          'removesingletonpoints',
                          'mergelines'))
    except:
        logger.error("Error: Could not simplify")

    # Correct Directions
    try:
        font.correctDirection()
    except:
        logger.error("Error: Could not correct directions")

    # Generate with DSIG and OpenType tables
    try:
        flags = ('dummy-dsig', 'opentype')
        font.generate(ttf, flags=flags)
        logger.info("Success: Generated OpenType-TTF (%s)" % ttf)
    except:
        logger.error("Error: Could not generate OpenType-TTF (%s)" % ttf)
        return


parser = argparse.ArgumentParser()
parser.add_argument('--with-otf', action="store_true",
                    help='Generate otf file')
parser.add_argument('source', nargs='+', type=str)

args = parser.parse_args()

for src in args.source:
    if not os.path.exists(src):
        print('\nError: {} does not exists\n'.format(src), file=sys.stderr)
        continue

    basename, _ = os.path.splitext(src)

    otffile = None
    if args.with_otf:
        otffile = '{}.otf'.format(basename)

    convert(src, '{}.ttf'.format(basename), otffile)
