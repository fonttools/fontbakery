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
import argparse

from fontTools.ttLib import TTLibError

from bakery_cli.ttfont import Font
from bakery_cli.scripts import vmet, Vmet


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
parser.add_argument('ttf_font', nargs='+', metavar='ttf_font',
                    help="Font file in OpenType (TTF/OTF) format")

options = parser.parse_args()

fonts = options.ttf_font

if (options.ascents or options.descents or options.linegaps
        or options.ascents_hhea or options.ascents_typo
        or options.ascents_win or options.descents_hhea
        or options.descents_typo or options.descents_win
        or options.linegaps_hhea or options.linegaps_typo):
    for f in fonts:
        try:
            metrics = Font(f)
        except TTLibError as ex:
            print('Error: {0}: {1}'.format(f, ex))
            continue

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
    Vmet.fix(fonts)
else:
    print(vmet.metricview(fonts))
