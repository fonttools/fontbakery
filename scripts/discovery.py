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

import argparse
import yaml
import os
import glob
from fontTools.ttLib import TTFont


def nameTableRead(font, NameID, fallbackNameID=False):
    for record in font['name'].names:
        if record.nameID == NameID:
            if b'\000' in record.string:
                return record.string.decode('utf-16-be').encode('utf-8')
            else:
                return record.string

    if fallbackNameID:
        return nameTableRead(font, fallbackNameID)


def run(folder, bakery_file):
    with open(bakery_file, 'r') as f:
        bakery = yaml.load(f.read())
    # local = yaml.load(open(local, 'r').read())

    # 'copyright_license': {
    #     'ofl': 'Open Font Licence v1.1',
    #     'apache': 'Apache Licence v2.0',
    #     'ufl': 'Ubuntu Font Licence v1.0',
    # },

    license_file = open(os.path.join(folder, bakery['license_file']), 'r').read()
    copyright_license = 'undetected'
    if license_file.find('OPEN FONT LICENSE Version 1.1'):
        copyright_license = 'ofl'
    elif license_file.find('Apache License, Version 2.0'):
        copyright_license = 'apache'
    elif license_file.find('UBUNTU FONT LICENCE Version 1.0'):
        copyright_license = 'ufl'

    bakery['copyright_license'] = copyright_license

    # Family name

    ttx_regular = [fn for fn in os.listdir("{folder}/sources/".format(folder=folder))
                    if fn.endswith('-Regular.ttx') or fn.endswith('-Regular.ttf.ttx') or fn.endswith('-Regular.otf.ttx')]

    if ttx_regular and len(ttx_regular) == 1:
        regular_font = TTFont(None, lazy=False, recalcBBoxes=True,
            verbose=False, allowVID=False)
        regular_font.importXML("{folder}/sources/{file}".format(folder=folder, file=ttx_regular[0]), quiet=True)

    ttx_family_name = nameTableRead(regular_font, 1)
    bakery['familyname'] = ttx_family_name

    # 'copyright_notice': {
    # - NameID0 in name table
    # It must exsits and contains "Copyright *(.) DDDD *(.) email" for each "Copyright"
    # there is should be YYYY and email.
    # Example: "Copyright (c) 2013, Dave Crossland (dave@lab6.com)".
    #         'icon': 'file-o',
    #         },

    ttx_copyright = nameTableRead(regular_font, 0)

    if ttx_copyright:
        # XXX: additional checks here
        bakery['copyright_notice'] = True

    # 'trademark_notice': {
    # - NameID7
    #         'yes': _('<i class="fa fa-exclamation-triangle"></i> Trademark is asserted'),
    #         'no': _('<i class="fa fa-thumbs-up"></i> Trademark not asserted'),
    #         },

    if nameTableRead(regular_font, 7):
        bakery['trademark_notice'] = True
    else:
        bakery['trademark_notice'] = False

    # *    'trademark_permission': {
    # Example https://github.com/davelab6/aclonica-ttx-test/blob/master/TRADEMARKS.txt
    # Make tests for this file
    # TRADEMARKS.txt should contains word "Permission"
    # Add TRADEMARKS.txt to list on setup page to copy as txt file.
    #
    # 'yes': _('<i class="fa fa-thumbs-up"></i> Trademark use is permitted'),
    # 'no': _('<i class="fa fa-thumbs-down"></i> Trademark use not permitted'),

    if os.path.exists(os.path.join(folder, 'TRADEMARKS.txt')):
        trademarks = open(os.path.join(folder, 'TRADEMARKS.txt'), 'r').read()
        if trademarks.find("Permission"):
            bakery['trademark_permission'] = True
        else:
            bakery['trademark_permission'] = False
    else:
        bakery['trademark_permission'] = False

    # *    'rfn_asserted': {
    # https://github.com/xen/bakery-testfont-merriweather/blob/master/OFL.txt#L1
    # Look for "Reserved Font Name" in NameID0
    #         'True': _('Y'),
    #         'False': _('N'),
    #         },

    rfn_table = nameTableRead(regular_font, 0)
    if rfn_table:
        if rfn_table.find("Reserved Font Name"):
            bakery['rfn_asserted'] = True
        else:
            bakery['rfn_asserted'] = True
    else:
        bakery['rfn_asserted'] = True

    # *    'source_cff_filetype': {
    # for each ttf file in .out folder look for .otf.ttx or .otf then True
    #         'True': _('Y'),
    #         'False': _('N'),
    #         },

    out_ttf = [os.path.basename(x) for x in glob.glob("{folder}/*.ttf".format(folder=folder))]
    out_files = os.listdir("{folder}/sources/".format(folder=folder))
    bakery['source_cff_filetype'] = True
    for x in out_ttf:
        name = os.path.splitext(x)[0]
        if "{}.otf.ttx".format(name) or "{}.otf".format(name) not in out_files:
            bakery['source_cff_filetype'] = False
            break

    # XXX: can source_ttf_filetype discovered the same way?

    # *    'hinting_level': {
    # Ask Dave for example
    #         'icon': 'search-plus',
    #         '1': '-',
    #         '2': _('N'),
    #         '3': _('A'),
    #         '4': _('T'),
    #         '5': _('H'),
    #         },
    # XXX: Need more info

    with open(bakery_file, 'w') as f:
        f.write(yaml.safe_dump(bakery))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('folder', help="Folder with data")
    parser.add_argument('bakery', help="bakery.yaml file")
    # parser.add_argument('local', help="local.yaml file")
    args = parser.parse_args()

    run(folder=args.folder,
        bakery_file=args.bakery)
