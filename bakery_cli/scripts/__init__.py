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
import copy
import fontTools.ttLib

from fontTools import ttLib
from fontTools.ttLib.tables.D_S_I_G_ import SignatureRecord

from bakery_cli.ttfont import Font
from bakery_cli.utils import normalizestr


class Fixer(object):

    def __init__(self, fontpath):
        self.font = ttLib.TTFont(fontpath)
        self.fixfont_path = '{}.fix'.format(fontpath)

    def fix(self):
        """ Make a concrete fix for the font.

        Implemented in inherited classes.

        Returns:
            :bool: false if fixes will not be saved into new file

        """
        raise NotImplementedError

    def apply(self, *args, **kwargs):
        if not self.fix(*args, **kwargs):
            return False
        self.font.save(self.fixfont_path)
        return True


class SpecCharsForASCIIFixer(Fixer):
    """ Converts special characters like copyright, trademark signs to ascii
    name """

    def fix(self):
        for name in self.font['name'].names:
            title = Font.bin2unistring(name)
            title = normalizestr(title)
            if name.platformID == 3:
                name.string = title.encode('utf-16-be')
            else:
                name.string = title
        return True


class CreateDSIGFixer(Fixer):
    """ Create DSIG table in font if it does not exist """

    def fix(self):
        if 'DSIG' in self.font:
            return False
        newDSIG = ttLib.newTable("DSIG")
        newDSIG.ulVersion = 1
        newDSIG.usFlag = 1
        newDSIG.usNumSigs = 1
        sig = SignatureRecord()
        sig.ulLength = 20
        sig.cbSignature = 12
        sig.usReserved2 = 0
        sig.usReserved1 = 0
        sig.pkcs7 = '\xd3M4\xd3M5\xd3M4\xd3M4'
        sig.ulFormat = 1
        sig.ulOffset = 20
        newDSIG.signatureRecords = [sig]
        self.font.tables["DSIG"] = newDSIG
        return True


class ResetFSTypeFlagFixer(Fixer):

    def fix(self):
        self.font['OS/2'].fsType = 0


class AddSPUAByGlyphIDToCmap(Fixer):

    def fix(self, unencoded_glyphs):

        if not unencoded_glyphs:
            return

        ucs2cmap = None
        cmap = self.font["cmap"]

        # Check if an UCS-2 cmap exists
        for ucs2cmapid in ((3, 1), (0, 3), (3, 0)):
            ucs2cmap = cmap.getcmap(ucs2cmapid[0], ucs2cmapid[1])
            if ucs2cmap:
                break
        # Create UCS-4 cmap and copy the contents of UCS-2 cmap
        # unless UCS 4 cmap already exists
        ucs4cmap = cmap.getcmap(3, 10)
        if not ucs4cmap:
            cmapModule = fontTools.ttLib.getTableModule('cmap')
            ucs4cmap = cmapModule.cmap_format_12(12)
            ucs4cmap.platformID = 3
            ucs4cmap.platEncID = 10
            ucs4cmap.language = 0
            if ucs2cmap:
                ucs4cmap.cmap = copy.deepcopy(ucs2cmap.cmap)
            cmap.tables.append(ucs4cmap)
        # Map all glyphs to UCS-4 cmap Supplementary PUA-A codepoints
        # by 0xF0000 + glyphID
        ucs4cmap = cmap.getcmap(3, 10)
        for glyphID, glyphName in enumerate(self.font.getGlyphOrder()):
            if glyphName in unencoded_glyphs:
                ucs4cmap.cmap[0xF0000 + glyphID] = glyphName
        self.font['cmap'] = cmap
        return True


def get_unencoded_glyphs(ttx):
    """ Check if font has unencoded glyphs """
    cmap = ttx['cmap']

    new_cmap = cmap.getcmap(3, 10)
    if not new_cmap:
        for ucs2cmapid in ((3, 1), (0, 3), (3, 0)):
            new_cmap = cmap.getcmap(ucs2cmapid[0], ucs2cmapid[1])
            if new_cmap:
                break

    assert new_cmap

    diff = list(set(ttx.glyphOrder) - set(new_cmap.cmap.values()) - {'.notdef'})
    return [g for g in diff[:] if g != '.notdef']
