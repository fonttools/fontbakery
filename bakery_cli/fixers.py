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

import copy
import fontTools.ttLib
import logging
import os
import shutil

from fontTools import ttLib
from fontTools.ttLib.tables.D_S_I_G_ import SignatureRecord
from fontTools.ttLib.tables._n_a_m_e import NameRecord

from bakery_cli.ttfont import Font


class Fixer(object):

    def __init__(self, fontpath):
        self.logging = logging.getLogger('bakery_cli.fixers')
        self.font = ttLib.TTFont(fontpath)
        self.fontpath = fontpath
        self.fixfont_path = '{}.fix'.format(fontpath)

    def fix(self):
        """ Make a concrete fix for the font.

        Implemented in inherited classes.

        Returns:
            :bool: false if fixes will not be saved into new file

        """
        raise NotImplementedError

    def apply(self, *args, **kwargs):
        override_origin = kwargs.pop('override_origin', None)
        if not self.fix(*args, **kwargs):
            return False

        self.font.save(self.fixfont_path)

        if override_origin and os.path.exists(self.fixfont_path):
            command = "$ mv {} {}".format(self.fixfont_path, self.fontpath)
            self.logging.debug(command)
            shutil.move(self.fixfont_path, self.fontpath)

        return True


class CharacterSymbolsFixer(Fixer):
    """ Converts special characters like copyright, trademark signs to ascii
    name """

    def get_shell_command(self):
        return 'fontbakery-fix-ascii-fontmetadata.py {}'.format(self.fontpath)

    @staticmethod
    def normalizestr(string):
        for mark, ascii_repl in CharacterSymbolsFixer.unicode_marks(string):
            string = string.replace(mark, ascii_repl)
        return string

    @staticmethod
    def unicode_marks(string):
        unicodemap = [(u'©', '(c)'), (u'®', '(r)'), (u'™', '(tm)')]
        return filter(lambda char: char[0] in string, unicodemap)

    def fix(self):
        for name in self.font['name'].names:
            title = Font.bin2unistring(name)
            title = CharacterSymbolsFixer.normalizestr(title)
            if name.platformID == 3:
                name.string = title.encode('utf-16-be')
            else:
                name.string = title
        return True


class CreateDSIGFixer(Fixer):
    """ Create DSIG table in font if it does not exist """

    def get_shell_command(self):
        return "fontbakery-fix-dsig.py {}".format(self.fontpath)

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

    def get_shell_command(self):
        return "fontbakery-fix-fstype.py --autofix {}".format(self.fontpath)

    def fix(self):
        self.font['OS/2'].fsType = 0


class AddSPUAByGlyphIDToCmap(Fixer):

    def get_shell_command(self):
        SCRIPTPATH = 'fontbakery-fix-glyph-private-encoding.py'
        return "{0} --autofix {1}".format(SCRIPTPATH, self.fontpath)

    def fix(self):
        unencoded_glyphs = get_unencoded_glyphs(self.font)
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
        for glyphID, glyph in enumerate(self.font.getGlyphOrder()):
            if glyph in unencoded_glyphs:
                ucs4cmap.cmap[0xF0000 + glyphID] = glyph
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


class NbspAndSpaceSameWidth(Fixer):

    def get_shell_command(self):
        return "fontbakery-fix-nbsp.py {}".format(self.fontpath)

    def getGlyph(self, uchar):
        for table in self.font['cmap'].tables:
            if not (table.platformID == 3 and table.platEncID in [1, 10]):
                continue
            if uchar in table.cmap:
                return table.cmap[uchar]
        return None

    def addGlyph(self, uchar, glyph):
        # Add to glyph list
        glyphOrder = self.font.getGlyphOrder()
        assert glyph not in glyphOrder
        glyphOrder.append(glyph)
        self.font.setGlyphOrder(glyphOrder)

        # Add horizontal metrics (to zero)
        self.font['hmtx'][glyph] = [0, 0]

        # Add to cmap
        for table in self.font['cmap'].tables:
            if not (table.platformID == 3 and table.platEncID in [1, 10]):
                continue
            if not table.cmap:  # Skip UVS cmaps
                continue
            assert uchar not in table.cmap
            table.cmap[uchar] = glyph

        # Add empty glyph outline
        self.font['glyf'].glyphs[glyph] = ttLib.getTableModule('glyf').Glyph()
        return glyph

    def getWidth(self, glyph):
        return self.font['hmtx'][glyph][0]

    def setWidth(self, glyph, width):
        self.font['hmtx'][glyph] = (width, self.font['hmtx'][glyph][1])

    def fix(self):
        space = self.getGlyph(0x0020)
        nbsp = self.getGlyph(0x00A0)
        if not nbsp:
            self.logging.info("No nbsp glyph")
            nbsp = self.addGlyph(0x00A0, 'nbsp')

        spaceWidth = self.getWidth(space)
        nbspWidth = self.getWidth(nbsp)

        self.logging.info("spaceWidth is    " + str(spaceWidth))
        self.logging.info("nbspWidth is     " + str(nbspWidth))
        if spaceWidth != nbspWidth or nbspWidth < 0:
            width = max(abs(spaceWidth), abs(nbspWidth))
            self.setWidth(nbsp, width)
            self.setWidth(space, width)
            self.logging.info("spaceWidth and nbspWidth of {}".format(width))
            return True
        return


class GaspFixer(Fixer):

    def get_shell_command(self):
        SCRIPTPATH = 'fontbakery-fix-gasp.py'
        return "$ {0} --set={1} {2}".format(SCRIPTPATH, 15, self.fontpath)

    def fix(self, value=15):
        if 'gasp' not in self.font.tables:
            self.logging.error('no table gasp')
            return

        self.font['gasp'].gaspRange[65535] = value
        return True

    def show(self):
        if 'gasp' not in self.font.tables:
            self.logging.error('no table gasp')
            return

        try:
            self.logging.info(self.font['gasp'].gaspRange[65535])
        except IndexError:
            self.logging.error('no index 65535')


class Vmet(Fixer):

    @staticmethod
    def fix(fonts):
        from bakery_cli.ttfont import Font
        ymin = 0
        ymax = 0

        for f in fonts:
            metrics = Font(f)
            font_ymin, font_ymax = metrics.get_bounding()
            ymin = min(font_ymin, ymin)
            ymax = max(font_ymax, ymax)

        for f in fonts:
            VmetFixer(f).apply(ymin, ymax)


class VmetFixer(Fixer):

    def fix(self, ymin, ymax):
        from bakery_cli.ttfont import AscentGroup, DescentGroup, LineGapGroup
        AscentGroup(self.font).set(ymax)
        DescentGroup(self.font).set(ymin)
        LineGapGroup(self.font).set(0)
        return True


mapping = {
    'Thin': 'Regular',
    'Extra Light': 'Regular',
    'Light': 'Regular',
    'Regular': 'Regular',
    'Medium': 'Regular',
    'SemiBold': 'Regular',
    'Extra Bold': 'Regular',
    'Black': 'Regular',

    'Thin Italic': 'Italic',
    'Extra Light Italic': 'Italic',
    'Light Italic': 'Italic',
    'Italic': 'Italic',
    'Medium Italic': 'Italic',
    'SemiBold Italic': 'Italic',
    'Extra Bold Italic': 'Italic',
    'Black Italic': 'Bold Italic',

    'Bold': 'Bold',
    'Bold Italic': 'Bold Italic'
}


class FamilyAndStyleNameFixer(Fixer):

    def get_shell_command(self):
        return "fontbakery-fix-opentype-names.py {}".format(self.fontpath)

    def suggestNameValues(self):
        from bakery_cli.ttfont import getSuggestedFontNameValues
        return getSuggestedFontNameValues(self.font)

    def getOrCreateNameRecord(self, nameId, val):
        result_namerec = self.font['name'].getName(nameId, 3, 1)
        if result_namerec:
            return result_namerec

        ot_namerecord = NameRecord()
        ot_namerecord.nameID = nameId
        ot_namerecord.platformID = 3
        ot_namerecord.langID = 0x409
        ot_namerecord.string = val.encode("utf_16_be")

        # When building a Unicode font for Windows, the platform ID
        # should be 3 and the encoding ID should be 1
        ot_namerecord.platEncID = 1

        self.font['name'].names.append(ot_namerecord)
        return ot_namerecord

    def fix(self):
        values = self.suggestNameValues()

        family_name = values['family']

        subfamily_name = values['subfamily']

        for pair in [[4, 3, 1], [4, 1, 0]]:
            name = self.font['name'].getName(*pair)
            if name:
                name.string = ' '.join([family_name.replace(' ', ''),
                                        subfamily_name]).encode('utf_16_be')

        for pair in [[6, 3, 1], [6, 1, 0]]:
            name = self.font['name'].getName(*pair)
            if name:
                name.string = '-'.join([family_name.replace(' ', ''),
                                        subfamily_name.replace(' ', '')])
                name.string = name.string.encode('utf_16_be')

        for pair in [[1, 3, 1], [1, 1, 0]]:
            name = self.font['name'].getName(*pair)
            if name:
                name.string = family_name.replace(' ', '').encode('utf_16_be')

        for pair in [[2, 3, 1], [2, 1, 0]]:
            name = self.font['name'].getName(*pair)
            if name:
                name.string = subfamily_name.encode('utf_16_be')

        self.getOrCreateNameRecord(16, family_name.replace(' ', ''))
        self.getOrCreateNameRecord(17, mapping.get(subfamily_name, 'Regular'))

        value = ' '.join([family_name.replace(' ', ''),
                          mapping.get(subfamily_name, 'Regular')])
        self.getOrCreateNameRecord(18, value)
        return True


class RemoveNameRecordWithOpyright(Fixer):

    def containsSubstr(self, namerecord, substr):
        if namerecord.isUnicode():
            string = namerecord.string.decode('utf-16-be')
        else:
            string = namerecord.string
        return bool(substr in string)

    def fix(self):
        records = []
        for record in self.font['name'].names:
            if self.containsSubstr(record, 'opyright') and record.nameID == 10:
                continue
            records.append(record)
        self.font['name'].names = records
