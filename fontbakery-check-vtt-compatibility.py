#!/usr/bin/env python
# Copyright 2013,2016 The Font Bakery Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# See AUTHORS.txt for the list of Authors and LICENSE.txt for the License.
import argparse
import logging
from argparse import RawTextHelpFormatter
from fontTools.ttLib import TTFont
import ntpath

description = """

fontbakery-check-vtt-compatibility.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Check a hinted font will successfully transfer vtt instructions to an
unhinted font

$ python fontbakery-check-vtt-compatibility.py hinted.ttf unhinted.ttf
"""


def font_glyphs(font):
  '''return a dict of glyphs objects for font

  {'a': <glyf object>, 'b': <glyf object>}'''
  return {g: font['glyf'][g] for g in font['glyf'].glyphs}


def glyphs_points(font):
  '''return a dict of glyphs coordinates/composites for each font

  {'a': [(0,0), (10,10)], 'b': [(10,10, (20,20))]},
  '''
  for glyph in font:
    if hasattr(font[glyph], 'coordinates'):
      font[glyph] = font[glyph].coordinates
    elif font[glyph].isComposite():
      font[glyph] = [c.glyphName for c in font[glyph]]
    else:
      font[glyph] = None
  return font


def compare_glyph_count(font1, name1, name2):
  if font1:
    logging.warning('%s missing glyphs against %s:\n%s' % (
      name1,
      name2,
      ', '.join(font1)
    ))
  else:
    logging.info('%s %s glyphs match' % (name1, name2))


parser = argparse.ArgumentParser(
  description=description,
  formatter_class=RawTextHelpFormatter)
parser.add_argument('hinted', help='Hinted font')
parser.add_argument('unhinted', help='Unhinted font')
parser.add_argument('--count', action="store_true", default=True,
                    help="Check fonts have the same glyph count")
parser.add_argument('--compatible', action="store_true", default=True,
                    help="Check glyphs share same coordinates and composites")

logging.getLogger().setLevel(logging.DEBUG)


def main():
  args = parser.parse_args()

  hinted = TTFont(args.hinted)
  unhinted = TTFont(args.unhinted)

  hinted_glyphs = font_glyphs(hinted)
  unhinted_glyphs = font_glyphs(unhinted)

  if args.count:
    logging.debug('Comparing glyph counts:')

    hinted_missing = set(unhinted_glyphs.keys()) - set(hinted_glyphs.keys())
    unhinted_missing = set(hinted_glyphs.keys()) - set(unhinted_glyphs.keys())

    compare_glyph_count(hinted_missing, args.hinted, args.unhinted)
    compare_glyph_count(unhinted_missing, args.unhinted, args.hinted)

  if args.compatible:
    logging.debug('Check glyph structures match')

    hinted_glyph_points = glyphs_points(hinted_glyphs)
    unhinted_glyph_points = glyphs_points(unhinted_glyphs)

    shared_glyphs = set(unhinted_glyphs) & set(hinted_glyphs.keys())

    incompatible_glyphs = []
    for glyph in shared_glyphs:
      if unhinted_glyph_points[glyph] != hinted_glyph_points[glyph]:
        incompatible_glyphs.append(glyph)

    if incompatible_glyphs:
      logging.warning('Incompatible glyphs between %s & %s:\n%s' % (
        args.hinted,
        args.unhinted,
        ', '.join(incompatible_glyphs)
        )
      )
    else:
      logging.info('Glyph sets are compatible')


if __name__ == '__main__':
  main()
