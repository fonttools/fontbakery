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
import os

from fontTools.ttLib import TTFont


class Discover:

    def __init__(self, ottfile):
        self.ttfont = TTFont(ottfile)

    @staticmethod
    def license(contents):
        return discover_license(contents)

    @staticmethod
    def trademark_permission(filelist):
        trademarks = filter(lambda fn: os.path.basename(fn) in ['TRADEMARKS.txt'], filelist)
        if not trademarks:
            return False

        contents = open(trademarks[0], 'r').read()
        return yesno(contents.find("Permission") >= 0)

    def copyright_notice(self):
        # NameID : 0 : Copyright License
        return yesno(nameTableRead(self.ttfont, 0))

    def trademark_notice(self):
        # NameID : 7 : Trademark
        return yesno(nameTableRead(self.ttfont, 7))

    def rfn_asserted(self):
        contents = self.copyright_license()
        return yesno(contents.find("Reserved Font Name") >= 0)


def yesno(value):
    return 'yes' if bool(value) else 'no'


def discover_license(contents):
    copyright_license = ''
    if contents.find('OPEN FONT LICENSE Version 1.1'):
        copyright_license = 'ofl'
    elif contents.find('Apache License, Version 2.0'):
        copyright_license = 'apache'
    elif contents.find('UBUNTU FONT LICENCE Version 1.0'):
        copyright_license = 'ufl'
    return copyright_license


def discover_copyright_notice(fontfile):
    return nameTableRead(TTFont(fontfile), 0)


def nameTableRead(font, NameID, fallbackNameID=False):
    for record in font['name'].names:
        if record.nameID == NameID:
            if b'\000' in record.string:
                return record.string.decode('utf-16-be').encode('utf-8')
            else:
                return record.string

    if fallbackNameID:
        return nameTableRead(font, fallbackNameID)
