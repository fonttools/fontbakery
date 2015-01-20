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

from bakery_cli.scripts.vmet import metricview
from bakery_cli.ttfont import Font, getSuggestedFontNameValues
from bakery_cli.utils import UpstreamDirectory, fix_all_names, \
    clean_name_values, nameTableRead


class Fixer(object):

    def loadfont(self, fontpath):
        return ttLib.TTFont(fontpath)

    def __init__(self, testcase, fontpath):
        self.logging = logging.getLogger('fontbakery')
        self.font = self.loadfont(fontpath)
        self.fontpath = fontpath
        self.fixfont_path = '{}.fix'.format(fontpath)
        self.testcase = testcase

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
            if name.platformID == 3 and name.isUnicode():
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

    def fix(self, check=False):
        val = self.font['OS/2'].fsType

        if val == 0:
            self.logging.info('OK: {}'.format(os.path.basename(self.fontpath)))
            return

        if check:
            msg = 'ER: {} {}: Change to 0'.format(os.path.basename(self.fontpath), val)
            self.logging.info(msg)
        else:
            msg = 'ER: {} {}: Fixed to 0'
            msg = msg.format(os.path.basename(self.fontpath), val)
            self.logging.info(msg)
            self.font['OS/2'].fsType = 0
        return True


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

    def fix(self, check=False):
        space = self.getGlyph(0x0020)
        nbsp = self.getGlyph(0x00A0)
        isNbspAdded = False
        if not nbsp:
            # self.logging.info("No nbsp glyph")
            isNbspAdded = True
            nbsp = self.addGlyph(0x00A0, 'nbsp')

        spaceWidth = self.getWidth(space)
        nbspWidth = self.getWidth(nbsp)

        fontfile = os.path.basename(self.fontpath)
        if spaceWidth != nbspWidth or nbspWidth < 0:
            width = max(abs(spaceWidth), abs(nbspWidth))
            self.setWidth(nbsp, width)
            self.setWidth(space, width)

            if isNbspAdded:
                if check:
                    msg = 'ER: {} space {} nbsp N: Add nbsp'
                    msg = msg.format(fontfile, spaceWidth)
                else:
                    msg = 'ER: {} space {} nbsp {}: Fixed nbsp to {}'
                    msg = msg.format(fontfile, spaceWidth, nbspWidth, width)
            else:
                if check:
                    msg = 'ER: {} space {} nbsp {}: Change nbsp to {}'
                    msg = msg.format(fontfile, spaceWidth, nbspWidth, width)
                else:
                    msg = 'ER: {} space {} nbsp {}: Fixed nbsp to {}'
                    msg = msg.format(fontfile, spaceWidth, nbspWidth, width)
            self.logging.info(msg)
            return True

        msg = 'OK: {}'.format(fontfile)
        self.logging.info(msg)
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

    SCRIPTPATH = 'fontbakery-fix-vertical-metrics.py'

    def loadfont(self, fontpath):
        return ttLib.TTFont()  # return for this fixer empty TTFont

    def __init__(self, testcase, fontpath):
        super(Vmet, self).__init__(testcase, fontpath)
        d = os.path.dirname(fontpath)
        directory = UpstreamDirectory(d)
        self.fonts = [os.path.join(d, f) for f in directory.BIN]

    def get_shell_command(self):
        return "{} --autofix {}".format(Vmet.SCRIPTPATH, ' '.join(self.fonts))

    def apply(self, override_origin=False):
        from bakery_cli.ttfont import Font
        ymin = 0
        ymax = 0

        for f in self.fonts:
            metrics = Font(f)
            font_ymin, font_ymax = metrics.get_bounding()
            ymin = min(font_ymin, ymin)
            ymax = max(font_ymax, ymax)

        for f in self.fonts:
            fixer = VmetFixer(self.testcase, f)
            fixer.apply(ymin, ymax, override_origin=override_origin)

        command = "$ {0} {1}".format(Vmet.SCRIPTPATH, ' '.join(self.fonts))

        self.logging.debug(command)

        import StringIO
        for l in StringIO.StringIO(metricview(self.fonts)):
            self.logging.debug(l)


class VmetFixer(Fixer):

    def fix(self, ymin, ymax):
        from bakery_cli.ttfont import AscentGroup, DescentGroup, LineGapGroup
        AscentGroup(self.font).set(ymax)
        DescentGroup(self.font).set(ymin)
        LineGapGroup(self.font).set(0)
        self.font['head'].unitsPerEm = ymax
        return True


class FamilyAndStyleNameFixer(Fixer):

    def get_shell_command(self):
        return "fontbakery-fix-opentype-names.py {}".format(self.fontpath)

    def getOrCreateNameRecord(self, nameId, val):
        result_namerec = self.font['name'].getName(nameId, 3, 1)
        if result_namerec:
            return result_namerec

        ot_namerecord = NameRecord()
        ot_namerecord.nameID = nameId
        ot_namerecord.platformID = 3
        ot_namerecord.langID = 0x409
        if ot_namerecord.isUnicode():
            ot_namerecord.string = (val or '').encode("utf-16-be")
        else:
            ot_namerecord.string = val or ''

        # When building a Unicode font for Windows, the platform ID
        # should be 3 and the encoding ID should be 1
        ot_namerecord.platEncID = 1

        self.font['name'].names.append(ot_namerecord)
        return ot_namerecord

    def fix(self):
        # Convert huge and complex fontTools to config python dict
        fontdata = {
            'names': [
                {'nameID': rec.nameID,
                 'platformID': rec.platformID,
                 'langID': rec.langID,
                 'string': rec.string.decode("utf_16_be")
                 if rec.isUnicode() else rec.string,
                 'platEncID': rec.platEncID} for rec in self.font['name'].names
            ],
            'OS/2': {
                'fsSelection': self.font['OS/2'].fsSelection,
                'usWeightClass': self.font['OS/2'].usWeightClass,
            },
            'head': {
                'macStyle': self.font['head'].macStyle,
            },
            'CFF': {
                'Weight': self.font.get('CFF ', {}).get('Weight'),
            }
        }

        fontdata = clean_name_values(fontdata)
        familyname = ''
        for rec in fontdata['names']:
            if rec['nameID'] == 1:
                familyname = rec['string']
                break
        fontdata = fix_all_names(fontdata, familyname)

        for field in fontdata['names']:
            value = nameTableRead(self.font, field['nameID'])
            if not value:
                self.getOrCreateNameRecord(field['nameID'], value)
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
        return True


DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'Data')
DATA_DIR = os.path.abspath(DATA_DIR)


class ReplaceLicenseURL(Fixer):

    def get_licenseurl_filename(self):
        return None

    def get_licensecontent_filename(self):
        return None

    def validate(self):
        path = os.path.join(DATA_DIR, self.get_licensecontent_filename())
        licenseText = open(path).read()

        path = os.path.join(DATA_DIR, self.get_licenseurl_filename())
        placeholder = open(path).read().strip()

        for field in self.font['name'].names:
            if field.nameID == 14:
                if field.isUnicode():
                    string = field.string.decode('utf-16-be')
                else:
                    string = field.string

                if string != placeholder:
                    return placeholder

            if field.nameID == 13:
                if field.isUnicode():
                    string = field.string.decode('utf-16-be')
                else:
                    string = field.string
                if licenseText.strip() in string:
                    return placeholder

        return

    def fix(self):
        placeholder = self.validate()
        if not placeholder:
            return

        for nameRecord in self.font['name'].names:
            if nameRecord.nameID == 14:
                if nameRecord.isUnicode():
                    nameRecord.string = placeholder.encode('utf-16-be')
                else:
                    nameRecord.string = placeholder
        return True


class ReplaceOFLLicenseURL(ReplaceLicenseURL):

    def get_licenseurl_filename(self):
        return 'OFL.url'

    def get_licensecontent_filename(self):
        return 'OFL.license'


class ReplaceApacheLicenseURL(ReplaceLicenseURL):

    def get_licenseurl_filename(self):
        return 'APACHE.url'

    def get_licensecontent_filename(self):
        return 'APACHE.license'


class ReplaceLicenseWithShortline(Fixer):

    def get_placeholder(self):
        path = self.get_placeholder_filename()
        with open(os.path.join(DATA_DIR, path)) as fp:
            return fp.read().strip()

    def fix(self):
        placeholder = self.get_placeholder()
        for nameRecord in self.font['name'].names:
            if nameRecord.nameID == 13:
                if nameRecord.isUnicode():
                    nameRecord.string = placeholder.encode('utf-16-be')
                else:
                    nameRecord.string = placeholder
        return True


class ReplaceOFLLicenseWithShortLine(ReplaceLicenseWithShortline):

    def get_placeholder_filename(self):
        return 'OFL.placeholder'


class ReplaceApacheLicenseWithShortLine(ReplaceLicenseWithShortline):

    def get_placeholder_filename(self):
        return 'APACHE.placeholder'


class RenameFileWithSuggestedName(Fixer):

    def validate(self):
        suggestedvalues = getSuggestedFontNameValues(self.font)

        family_name = suggestedvalues['family']
        subfamily_name = suggestedvalues['subfamily']

        expectedname = '{0}-{1}'.format(family_name.replace(' ', ''),
                                        subfamily_name.replace(' ', ''))
        actualname, extension = os.path.splitext(self.fontpath)

        return '{0}{1}'.format(expectedname, extension)

    def fix(self):
        new_targetpath = os.path.join(os.path.dirname(self.fontpath),
                                      self.validate())
        shutil.move(self.fontpath, new_targetpath, log=self.logging)
        self.testcase.operator.path = new_targetpath
        return True
