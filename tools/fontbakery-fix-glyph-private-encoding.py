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
import os

import fontTools.ttLib
from bakery_cli.scripts import encode_glyphs


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='Font file to fix encoding')
    parser.add_argument('--autofix', action="store_true",
                        help='Apply autofix. '
                             'Otherwise just check if there are unencoded glyphs')

    args = parser.parse_args()
    assert os.path.exists(args.filename)

    ttx = fontTools.ttLib.TTFont(args.filename, 0)
    if args.autofix:
        unencoded_glyphs = encode_glyphs.get_unencoded_glyphs(ttx)
        encode_glyphs.add_spua_by_glyph_id_mapping_to_cmap(ttx, args.filename, unencoded_glyphs)
    else:
        print(encode_glyphs.get_unencoded_glyphs(ttx))
