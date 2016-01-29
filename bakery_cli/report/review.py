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
from collections import defaultdict, OrderedDict
import os.path as op
from markdown import markdown
from bakery_cli.report import utils as report_utils
from bakery_cli.utils import UpstreamDirectory
from fontaine.cmap import Library
from fontaine.font import FontFactory


TAB = 'Review'
TEMPLATE_DIR = op.join(op.dirname(__file__), 'templates')

t = lambda templatefile: op.join(TEMPLATE_DIR, templatefile)


def get_orthography_old(fontaineFonts):
    library = Library(collections=['subsets'])
    result = []
    for font, fontaine in fontaineFonts:
        for f1, f2, f3, f4 in fontaine.get_orthographies(_library=library):
            result.append([font, f1, f2, f3, f4])
    return sorted(result, key=lambda x: x[3], reverse=True)


def get_orthography(fontaineFonts):
    result = []
    library = Library(collections=['subsets'])
    for font, fontaine in fontaineFonts:
        orthographies = fontaine.get_orthographies(_library=library)
        for info in orthographies:
            result.append(dict(name=font, support=info.support_level,
                               coverage=info.coverage,
                               missing_glyphs=info.missing,
                               glyphs=info.charmap.glyphs))
    return sorted(result, key=lambda x: x['coverage'], reverse=True)


def get_weight_name(value):
    return {
        100: 'Thin',
        200: 'ExtraLight',
        300: 'Light',
        400: '',
        500: 'Medium',
        600: 'SemiBold',
        700: 'Bold',
        800: 'ExtraBold',
        900: 'Black'
    }.get(value, '')


def get_FamilyProto_Message(path):
    metadata = FamilyProto()
    text_data = open(path, "rb").read()
    text_format.Merge(text_data, metadata)
    return metadata


def generate(config, outfile='review.html'):
    directory = UpstreamDirectory(config['path'])
    fonts = [(path, FontFactory.openfont(op.join(config['path'], path)))
             for path in directory.BIN]

    metadata_file_path = op.join(config['path'], 'METADATA.pb')
    family_metadata = get_FamilyProto_Message(metadata_file_path)
    faces = []
    for f in family_metadata.fonts:
        faces.append({'name': f.full_name,
                      'basename': f.post_script_name,
                      'path': f.filename,
                      'meta': f})

    report_app = report_utils.BuildInfo(config)
    
    #temporarily disable broken orthography code
    if False:
        fonts_orthography = get_orthography(fonts)

        report_app.review_page.dump_file(fonts_orthography, 'orthography.json')
