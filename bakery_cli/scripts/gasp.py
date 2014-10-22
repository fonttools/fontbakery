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
import sys

from bakery_cli.ttfont import Font


def set(fontpath, value):
    ttfont = Font.get_ttfont(fontpath)

    try:
        ttfont['gasp']
    except:
        print('no table gasp', file=sys.stderr)
        return

    ttfont['gasp'].gaspRange[65535] = value

    ttfont.save(fontpath + '.fix')


def show(fontpath):
    ttfont = Font.get_ttfont(fontpath)

    try:
        ttfont['gasp']
    except:
        print('no table gasp', file=sys.stderr)
        return

    try:
        print(ttfont['gasp'].gaspRange[65535])
    except IndexError:
        print('no index 65535', file=sys.stderr)

