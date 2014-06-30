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
#
# Based on http://typophile.com/node/13081
# Also see http://typophile.com/node/13081
from __future__ import print_function
import argparse
import collections
import os
import sys
from fontTools import ttLib


class TextMetricsView(object):

    def __init__(self):
        self._its_metrics_header = ['Parameter          ']
        # first column has a length of largest parameter
        # named OS/2.sTypoDescender
        self._its_metrics = collections.OrderedDict([
            ('ymax', []),
            ('hhea.ascent', []),
            ('OS/2.sTypoAscender', []),
            ('OS/2.usWinAscent', []),
            ('ymin', []),
            ('hhea.descent', []),
            ('OS/2.sTypoDescender', []),
            ('OS/2.usWinDescent', []),
            ('hhea.lineGap', []),
            ('OS/2.sTypoLineGap', [])
        ])
        self._in_consistent = True
        self.glyphs = collections.OrderedDict()

    def add_to_table(self, key, value):
        self._its_metrics[key].append(value)

    @property
    def in_consistent(self):
        """ Check that groups of ascent, descent and linegaps are in
        consistent """
        pass

    def add_metric(self, font_name, vmet):
        ymin, ymax = vmet.get_bounding()
        self._its_metrics_header.append(font_name)
        self.add_to_table('hhea.ascent', vmet.ascent_hhea)
        self.add_to_table('OS/2.sTypoAscender', vmet.ascent_os2typo)
        self.add_to_table('OS/2.usWinAscent', vmet.ascent_os2win)
        self.add_to_table('hhea.descent', vmet.descent_hhea)
        self.add_to_table('OS/2.sTypoDescender', vmet.descent_os2typo)
        self.add_to_table('OS/2.usWinDescent', vmet.descent_os2win)
        self.add_to_table('hhea.lineGap', vmet.linegaps_hhea)
        self.add_to_table('OS/2.sTypoLineGap', vmet.linegaps_os2typo)
        self._its_metrics['ymax'].append(ymax)
        self._its_metrics['ymin'].append(ymin)

        self.glyphs[font_name] = vmet.get_highest_and_lowest()

    def print_metrics(self):
        if not self._in_consistent:
            print('Values are not in consistent', end='\n\n')
        formatstring = ''
        for k in self._its_metrics_header:
            print(('{:<%s}' % (len(k) + 4)).format(k), end='')
            formatstring += '{:<%s}' % (len(k) + 4)
        print()
        for k, values in self._its_metrics.items():
            print(formatstring.format(*([k] + values)))
        print()
        print('High Glyphs')
        for font, glyphs in self.glyphs.items():
            if glyphs[0]:
                print(font + ':', ' '.join(glyphs[0]))
        print()
        print('Low Glyphs')
        for font, glyphs in self.glyphs.items():
            if glyphs[1]:
                print(font + ':', ' '.join(glyphs[1]))


def is_none_protected(func):

    def f(self, value):
        if value is None:
            return
        func(self, value)

    return f


class FontVerticalMetrics(object):

    def __init__(self, fontpath):
        self.ttfont = ttLib.TTFont(fontpath)
        self.bounded_lowest_glyphs = []
        self.bounded_highest_glyphs = []

    def set_ascents(self, value):
        self.ascent_hhea = value
        self.ascent_os2typo = value
        self.ascent_os2win = value

    def set_descents(self, value):
        self.descent_hhea = value
        self.descent_os2typo = value
        self.descent_os2win = value

    def set_linegaps(self, value):
        self.linegaps_hhea = value
        self.linegaps_os2typo = value

    def get_min_descents(self):
        return min(self.descent_hhea,
                   self.descent_os2typo,
                   self.descent_os2win)

    def get_max_ascents(self):
        return max(self.ascent_hhea,
                   self.ascent_os2typo,
                   self.ascent_os2win)

    def get_highest_and_lowest(self):
        high = []
        low = []
        maxval = self.get_max_ascents()
        minval = self.get_min_descents()
        for glyph, params in self.ttfont['glyf'].glyphs.items():
            if hasattr(params, 'yMax') and params.yMax == maxval:
                high.append(glyph)
            if hasattr(params, 'yMin') and params.yMin == minval:
                low.append(glyph)
        return high, low

    def ascent_hhea():
        doc = "Ascent value in 'Horizontal Header' (hhea.ascent)"

        def fget(self):
            return self.ttfont['hhea'].ascent

        @is_none_protected
        def fset(self, value):
            self.ttfont['hhea'].ascent = value

        return locals()
    ascent_hhea = property(**ascent_hhea())

    def ascent_os2typo():
        doc = "Ascent value in 'Horizontal Header' (OS/2.sTypoAscender)"

        def fget(self):
            return self.ttfont['OS/2'].sTypoAscender

        @is_none_protected
        def fset(self, value):
            self.ttfont['OS/2'].sTypoAscender = value

        return locals()
    ascent_os2typo = property(**ascent_os2typo())

    def ascent_os2win():
        doc = "Ascent value in 'Horizontal Header' (OS/2.usWinAscent)"

        def fget(self):
            return self.ttfont['OS/2'].usWinAscent

        @is_none_protected
        def fset(self, value):
            self.ttfont['OS/2'].usWinAscent = value

        return locals()
    ascent_os2win = property(**ascent_os2win())

    def descent_hhea():
        doc = "Descent value in 'Horizontal Header' (hhea.descent)"

        def fget(self):
            return self.ttfont['hhea'].descent

        @is_none_protected
        def fset(self, value):
            self.ttfont['hhea'].descent = value

        return locals()
    descent_hhea = property(**descent_hhea())

    def descent_os2typo():
        doc = "Descent value in 'Horizontal Header' (OS/2.sTypoDescender)"

        def fget(self):
            return self.ttfont['OS/2'].sTypoDescender

        @is_none_protected
        def fset(self, value):
            self.ttfont['OS/2'].sTypoDescender = value

        return locals()
    descent_os2typo = property(**descent_os2typo())

    def descent_os2win():
        doc = "Descent value in 'Horizontal Header' (OS/2.usWinDescent)"

        def fget(self):
            return self.ttfont['OS/2'].usWinDescent

        @is_none_protected
        def fset(self, value):
            self.ttfont['OS/2'].usWinDescent = abs(value)

        return locals()
    descent_os2win = property(**descent_os2win())

    def linegaps_hhea():
        doc = "The hhea.lineGap property"

        def fget(self):
            return self.ttfont['hhea'].lineGap

        @is_none_protected
        def fset(self, value):
            self.ttfont['hhea'].lineGap = value

        return locals()
    linegaps_hhea = property(**linegaps_hhea())

    def linegaps_os2typo():
        doc = "The OS/2.sTypoLineGap property"

        def fget(self):
            return self.ttfont['OS/2'].sTypoLineGap

        @is_none_protected
        def fset(self, value):
            self.ttfont['OS/2'].sTypoLineGap = value

        return locals()
    linegaps_os2typo = property(**linegaps_os2typo())

    def get_bounding(self):
        ymin = 0
        ymax = 0
        # .OTF fonts do not contain a `glyf` table,
        # but have a precomputed value in the `head` table
        if self.ttfont.sfntVersion == 'OTTO':
            if hasattr(self.ttfont['head'], 'yMin'):
                ymin = self.ttfont['head'].yMin
            if hasattr(self.ttfont['head'], 'yMax'):
                ymax = self.ttfont['head'].yMax
        else:
            for g in self.ttfont['glyf'].glyphs:
                char = self.ttfont['glyf'][g]
                if hasattr(char, 'yMin') and ymin > char.yMin:
                    ymin = char.yMin
                if hasattr(char, 'yMax') and ymax < char.yMax:
                    ymax = char.yMax
        if ymin != 0 and ymax != 0:
            return(ymin, ymax)
        else:
            sys.exit("Unable to detect y values")

    def save(self, fontpath):
        self.ttfont.save(fontpath)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # ascent parameters
    parser.add_argument('-a', '--ascents', type=int,
                        help=("Set new ascents value in 'Horizontal Header'"
                              " table"))

    parser.add_argument('-ah', '--ascents-hhea', type=int,
                        help=("Set new ascents value in 'Horizontal Header'"
                              " table ('hhea'). This argument"
                              " cancels --ascents."))
    parser.add_argument('-at', '--ascents-typo', type=int,
                        help=("Set new ascents value in 'Horizontal Header'"
                              " table ('OS/2'). This argument"
                              " cancels --ascents."))
    parser.add_argument('-aw', '--ascents-win', type=int,
                        help=("Set new ascents value in 'Horizontal Header'"
                              " table ('OS/2.Win'). This argument"
                              " cancels --ascents."))

    # descent parameters
    parser.add_argument('-d', '--descents', type=int,
                        help=("Set new descents value in 'Horizontal Header'"
                              " table"))
    parser.add_argument('-dh', '--descents-hhea', type=int,
                        help=("Set new descents value in 'Horizontal Header'"
                              " table ('hhea'). This argument"
                              " cancels --descents."))
    parser.add_argument('-dt', '--descents-typo', type=int,
                        help=("Set new descents value in 'Horizontal Header'"
                              " table ('OS/2'). This argument"
                              " cancels --descents."))
    parser.add_argument('-dw', '--descents-win', type=int,
                        help=("Set new descents value in 'Horizontal Header'"
                              " table ('OS/2.Win'). This argument"
                              " cancels --descents."))

    # linegaps parameters
    parser.add_argument('-l', '--linegaps', type=int,
                        help=("Set new linegaps value in 'Horizontal Header'"
                              " table"))
    parser.add_argument('-lh', '--linegaps-hhea', type=int,
                        help=("Set new linegaps value in 'Horizontal Header'"
                              " table ('hhea')"))
    parser.add_argument('-lt', '--linegaps-typo', type=int,
                        help=("Set new linegaps value in 'Horizontal Header'"
                              " table ('OS/2')"))

    parser.add_argument('--autofix', action="store_true",
                        help="Autofix font metrics")
    parser.add_argument('fonts', nargs='+', metavar='font',
                        help="Font file in OpenType (TTF/OTF) format")

    options = parser.parse_args()

    fonts = options.fonts

    if (options.ascents or options.descents or options.linegaps
            or options.ascents_hhea or options.ascents_typo
            or options.ascents_win or options.descents_hhea
            or options.descents_typo or options.descents_win
            or options.linegaps_hhea or options.linegaps_typo):
        for f in fonts:
            metrics = FontVerticalMetrics(f)

            # set ascents, descents and linegaps. FontVerticalMetrics will
            # not set those values if None, and overwrite them if concrete
            # argument has been passed
            metrics.set_ascents(options.ascents)
            metrics.set_descents(options.descents)
            metrics.set_linegaps(options.linegaps)

            metrics.ascent_hhea = options.ascents_hhea
            metrics.ascent_os2typo = options.ascents_typo
            metrics.ascent_os2win = options.ascents_win

            metrics.descent_hhea = options.descents_hhea
            metrics.descent_os2typo = options.descents_typo
            metrics.descent_os2win = options.descents_win

            metrics.linegaps_hhea = options.linegaps_hhea
            metrics.linegaps_os2typo = options.linegaps_typo
            metrics.save(f + '.fix')

    elif options.autofix:
        ymin = 0
        ymax = 0

        for f in fonts:
            metrics = FontVerticalMetrics(f)
            font_ymin, font_ymax = metrics.get_bounding()
            ymin = min(font_ymin, ymin)
            ymax = max(font_ymax, ymax)

        for f in fonts:
            metrics = FontVerticalMetrics(f)
            metrics.set_ascents(ymax)
            metrics.set_descents(ymin)
            metrics.set_linegaps(0)
            metrics.save(f + '.fix')
    else:
        view = TextMetricsView()
        for f in fonts:
            metrics = FontVerticalMetrics(f)
            view.add_metric(os.path.basename(f), metrics)
        view.print_metrics()
