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


def is_none_protected(func):

    def f(self, value):
        if value is None:
            return
        func(self, value)

    return f


class AscentGroup(object):

    def __init__(self, ttfont):
        self.ttfont = ttfont

    def set(self, value):
        self.hhea = value
        self.os2typo = value
        self.os2win = value

    def get_max(self):
        return max(self.hhea, self.os2typo, self.os2win)

    def hhea():
        doc = "Ascent value in 'Horizontal Header' (hhea.ascent)"

        def fget(self):
            return self.ttfont['hhea'].ascent

        @is_none_protected
        def fset(self, value):
            self.ttfont['hhea'].ascent = value

        return locals()
    hhea = property(**hhea())

    def os2typo():
        doc = "Ascent value in 'Horizontal Header' (OS/2.sTypoAscender)"

        def fget(self):
            return self.ttfont['OS/2'].sTypoAscender

        @is_none_protected
        def fset(self, value):
            self.ttfont['OS/2'].sTypoAscender = value

        return locals()
    os2typo = property(**os2typo())

    def os2win():
        doc = "Ascent value in 'Horizontal Header' (OS/2.usWinAscent)"

        def fget(self):
            return self.ttfont['OS/2'].usWinAscent

        @is_none_protected
        def fset(self, value):
            self.ttfont['OS/2'].usWinAscent = value

        return locals()
    os2win = property(**os2win())


class DescentGroup(object):

    def __init__(self, ttfont):
        self.ttfont = ttfont

    def set(self, value):
        self.hhea = value
        self.os2typo = value
        self.os2win = value

    def get_min(self):
        return min(self.hhea, self.os2typo, self.os2win)

    def hhea():
        doc = "Descent value in 'Horizontal Header' (hhea.descent)"

        def fget(self):
            return self.ttfont['hhea'].descent

        @is_none_protected
        def fset(self, value):
            self.ttfont['hhea'].descent = value

        return locals()
    hhea = property(**hhea())

    def os2typo():
        doc = "Descent value in 'Horizontal Header' (OS/2.sTypoDescender)"

        def fget(self):
            return self.ttfont['OS/2'].sTypoDescender

        @is_none_protected
        def fset(self, value):
            self.ttfont['OS/2'].sTypoDescender = value

        return locals()
    os2typo = property(**os2typo())

    def os2win():
        doc = "Descent value in 'Horizontal Header' (OS/2.usWinDescent)"

        def fget(self):
            return self.ttfont['OS/2'].usWinDescent

        @is_none_protected
        def fset(self, value):
            self.ttfont['OS/2'].usWinDescent = abs(value)

        return locals()
    os2win = property(**os2win())


class LineGapGroup(object):

    def __init__(self, ttfont):
        self.ttfont = ttfont

    def set(self, value):
        self.hhea = value
        self.os2typo = value

    def hhea():
        doc = "The hhea.lineGap property"

        def fget(self):
            return self.ttfont['hhea'].lineGap

        @is_none_protected
        def fset(self, value):
            self.ttfont['hhea'].lineGap = value

        return locals()
    hhea = property(**hhea())

    def os2typo():
        doc = "The OS/2.sTypoLineGap property"

        def fget(self):
            return self.ttfont['OS/2'].sTypoLineGap

        @is_none_protected
        def fset(self, value):
            self.ttfont['OS/2'].sTypoLineGap = value

        return locals()
    os2typo = property(**os2typo())


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
            ('OS/2.sTypoLineGap', []),
            ('UPM:Heights', []),
            ('UPM:Heights %', [])
        ])
        self._inconsistent = set()
        self._inconsistent_table = {}

        self.glyphs = collections.OrderedDict()

    def add_to_table(self, fontname, key, value):
        if self._its_metrics[key] and value not in self._its_metrics[key]:
                self._inconsistent.add(key)

        if key not in self._inconsistent_table:
            self._inconsistent_table[key] = []

        # lookup row with value and append fontname to `fonts` key, eg.:
        # {'hhea.ascent': [{'value': 390,
        #                   'fonts': ['fontname.ttf', 'fontname2.ttf']}]}
        #
        # It looks like json groupped by metrics key
        row = {}
        for r in self._inconsistent_table[key]:
            if r['value'] == value:
                row = r

        if not row:
            row = {'value': value, 'fonts': []}
            self._inconsistent_table[key].append(row)

        row['fonts'].append(fontname)

        self._its_metrics[key].append(value)

    def add_metric(self, font_name, vmet):
        ymin, ymax = vmet.get_bounding()
        self._its_metrics_header.append(font_name)
        self.add_to_table(font_name, 'hhea.ascent', vmet.ascents.hhea)
        self.add_to_table(font_name, 'OS/2.sTypoAscender', vmet.ascents.os2typo)
        self.add_to_table(font_name, 'OS/2.usWinAscent', vmet.ascents.os2win)
        self.add_to_table(font_name, 'hhea.descent', vmet.descents.hhea)
        self.add_to_table(font_name, 'OS/2.sTypoDescender', vmet.descents.os2typo)
        self.add_to_table(font_name, 'OS/2.usWinDescent', vmet.descents.os2win)
        self.add_to_table(font_name, 'hhea.lineGap', vmet.linegaps.hhea)
        self.add_to_table(font_name, 'OS/2.sTypoLineGap', vmet.linegaps.os2typo)
        self._its_metrics['ymax'].append(ymax)
        self._its_metrics['ymin'].append(ymin)

        value = vmet.ascents.get_max() + abs(vmet.descents.get_min())
        upm = '%s:%s' % (vmet.get_upm_heights(), value)
        self._its_metrics['UPM:Heights'].append(upm)

        value = (value / float(vmet.get_upm_heights())) * 100
        self._its_metrics['UPM:Heights %'].append('%d %%' % value)

        self.glyphs[font_name] = vmet.get_highest_and_lowest()

    def print_metrics(self):
        if self._inconsistent:
            _ = 'WARNING: Inconsistent {}'
            print(_.format(' '.join([str(x) for x in self._inconsistent])),
                  end='\n\n')
        formatstring = ''
        for k in self._its_metrics_header:
            print(('{:<%s}' % (len(k) + 4)).format(k), end='')
            formatstring += '{:<%s}' % (len(k) + 4)

        print()
        for k, values in self._its_metrics.items():
            print(formatstring.format(*([k] + values)))

        header_printed = False
        for font, glyphs in self.glyphs.items():
            if glyphs[0]:
                if not header_printed:
                    print()
                    print('High Glyphs')
                    header_printed = True
                print(font + ':', ' '.join(glyphs[0]))

        header_printed = False
        for font, glyphs in self.glyphs.items():
            if glyphs[1]:
                if not header_printed:
                    print()
                    print('Low Glyphs')
                    header_printed = True
                print(font + ':', ' '.join(glyphs[1]))

        for metrickey, row in self._inconsistent_table.items():
            value = self.find_max_occurs_from_metrics_key(row)

            tbl = {}
            for r in row:
                if r['value'] == value:
                    continue
                if metrickey not in tbl:
                    tbl[metrickey] = []
                tbl[metrickey] += r['fonts']

            for k, r in tbl.items():
                print('Inconsistent %s:' % k, ', '.join(r))

    def find_max_occurs_from_metrics_key(self, metricvalues):
        result = 0
        occurs = 0
        for v in metricvalues:
            if len(v['fonts']) > occurs:
                occurs = len(v['fonts'])
                result = v['value']
        return result


class FontVerticalMetrics(object):

    def __init__(self, fontpath):
        self.ttfont = ttLib.TTFont(fontpath)

        self.ascents = AscentGroup(self.ttfont)
        self.descents = DescentGroup(self.ttfont)
        self.linegaps = LineGapGroup(self.ttfont)

    def get_upm_heights(self):
        return self.ttfont['head'].unitsPerEm

    def get_highest_and_lowest(self):
        high = []
        low = []
        maxval = self.ascents.get_max()
        minval = self.descents.get_min()
        for glyph, params in self.ttfont['glyf'].glyphs.items():
            if hasattr(params, 'yMax') and params.yMax > maxval:
                high.append(glyph)
            if hasattr(params, 'yMin') and params.yMin < minval:
                low.append(glyph)
        return high, low

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
            metrics.ascents.set(options.ascents)
            metrics.descents.set(options.descents)
            metrics.linegaps.set(options.linegaps)

            metrics.ascents.hhea = options.ascents_hhea
            metrics.ascents.os2typo = options.ascents_typo
            metrics.ascents.os2win = options.ascents_win

            metrics.descents.hhea = options.descents_hhea
            metrics.descents.os2typo = options.descents_typo
            metrics.descents.os2win = options.descents_win

            metrics.linegaps.hhea = options.linegaps_hhea
            metrics.linegaps.os2typo = options.linegaps_typo
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
            metrics.ascents.set(ymax)
            metrics.descents.set(ymin)
            metrics.linegaps.set(0)
            metrics.save(f + '.fix')
    else:
        view = TextMetricsView()
        for f in fonts:
            metrics = FontVerticalMetrics(f)
            view.add_metric(os.path.basename(f), metrics)
        view.print_metrics()
