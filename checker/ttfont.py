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
import os.path as op

from fontTools import ttLib


class Font(object):

    @staticmethod
    def get_ttfont_from_metadata(path, font_metadata, is_menu=False):
        path = op.join(op.dirname(path), font_metadata.filename)
        if is_menu:
            path = path.replace('.ttf', '.menu')
        return Font(path)

    @staticmethod
    def get_ttfont(path):
        return Font(path)

    def __init__(self, fontpath):
        self.ttfont = ttLib.TTFont(fontpath)

        self.ascents = AscentGroup(self.ttfont)
        self.descents = DescentGroup(self.ttfont)
        self.linegaps = LineGapGroup(self.ttfont)

    @property
    def macStyle(self):
        return self.ttfont['head'].macStyle

    @property
    def italicAngle(self):
        return self.ttfont['post'].italicAngle

    @property
    def names(self):
        return self.ttfont['name'].names

    @property
    def OS2_usWeightClass(self):
        """ OS/2.usWeightClass property value

        >>> font = Font("tests/fixtures/ttf/Font-Regular.ttf")
        >>> font.OS2_usWeightClass
        400
        """
        return self.ttfont['OS/2'].usWeightClass

    @property
    def OS2_usWidthClass(self):
        """ Returns OS/2.usWidthClass property value

        >>> font = Font("tests/fixtures/ttf/Font-Regular.ttf")
        >>> font.OS2_usWidthClass
        5
        """
        return self.ttfont['OS/2'].usWidthClass

    @property
    def familyname(self):
        windows_entry = None

        for entry in self.names:
            if entry.nameID != 6:
                continue
            # macintosh platform
            if entry.platformID == 1 and entry.langID == 0:
                return Font.bin2unistring(entry)
            if entry.platformID == 3 and entry.langID == 0x409:
                windows_entry = entry

        return windows_entry

    def retrieve_cmap_format_4(self):
        for cmap in self.ttfont['cmap'].tables:
            if cmap.format == 4:
                return cmap.cmap

    def advanceWidth(self, glyph_id):
        """ AdvanceWidth of glyph from "hmtx" table

        >>> font = Font("tests/fixtures/ttf/Font-Regular.ttf")
        >>> font.advanceWidth("a")
        572
        """
        try:
            return self.ttfont['hmtx'].metrics[glyph_id][0]
        except KeyError:
            return None

    @staticmethod
    def bin2unistring(record):
        if b'\000' in record.string:
            string = record.string.decode('utf-16-be')
            return string.encode('utf-8')
        else:
            return record.string

    def get_glyf_length(self):
        """ Length of "glyf" table

            >>> font = Font("tests/fixtures/ttf/Font-Regular.ttf")
            >>> font.get_glyf_length()
            21804
        """
        return self.ttfont.reader.tables['glyf'].length

    def get_loca_length(self):
        """ Length of "loca" table

        >>> font = Font("tests/fixtures/ttf/Font-Regular.ttf")
        >>> font.get_loca_length()
        1006
        """
        return self.ttfont.reader.tables['loca'].length

    def get_loca_glyph_offset(self, num):
        """ Retrieve offset of glyph in font tables

        >>> font = Font("tests/fixtures/ttf/Font-Regular.ttf")
        >>> font.get_loca_glyph_offset(15)
        836L
        >>> font.get_loca_glyph_offset(16)
        904L
        """
        return self.ttfont['loca'].locations[num]

    def get_loca_glyph_length(self, num):
        """ Retrieve length of glyph in font loca table

        >>> font = Font("tests/fixtures/ttf/Font-Regular.ttf")
        >>> font.get_loca_glyph_length(15)
        68L
        """
        return self.get_loca_glyph_offset(num + 1) - self.get_loca_glyph_offset(num)

    def get_loca_num_glyphs(self):
        """ Retrieve number of glyph in font loca table

        >>> font = Font("tests/fixtures/ttf/Font-Regular.ttf")
        >>> font.get_loca_num_glyphs()
        503
        """
        return len(self.ttfont['loca'].locations)

    def get_hmtx_max_advanced_width(self):
        """ AdvanceWidthMax from "hmtx" table

        >>> font = Font("tests/fixtures/ttf/Font-Regular.ttf")
        >>> font.get_hmtx_max_advanced_width()
        1409
        """
        advance_width_max = 0
        for g in self.ttfont['hmtx'].metrics.values():
            advance_width_max = max(g[0], advance_width_max)
        return advance_width_max

    @property
    def advance_width_max(self):
        """ AdvanceWidthMax from "hhea" table

        >>> font = Font("tests/fixtures/ttf/Font-Regular.ttf")
        >>> font.advance_width_max
        1409
        """
        return self.ttfont['hhea'].advanceWidthMax


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
        """ Returns largest value of ascents

        >>> font = Font("tests/fixtures/ttf/Font-Regular.ttf")
        >>> font.ascents.get_max()
        1178
        """
        return max(self.hhea, self.os2typo, self.os2win)

    def hhea():
        doc = """Ascent value in 'Horizontal Header' (hhea.ascent)

        >>> font = Font("tests/fixtures/ttf/Font-Regular.ttf")
        >>> font.ascents.hhea
        1178
        """

        def fget(self):
            return self.ttfont['hhea'].ascent

        @is_none_protected
        def fset(self, value):
            self.ttfont['hhea'].ascent = value

        return locals()
    hhea = property(**hhea())

    def os2typo():
        doc = """Ascent value in 'Horizontal Header' (OS/2.sTypoAscender)

        >>> font = Font("tests/fixtures/ttf/Font-Regular.ttf")
        >>> font.ascents.os2typo
        1178
        """

        def fget(self):
            return self.ttfont['OS/2'].sTypoAscender

        @is_none_protected
        def fset(self, value):
            self.ttfont['OS/2'].sTypoAscender = value

        return locals()
    os2typo = property(**os2typo())

    def os2win():
        doc = """Ascent value in 'Horizontal Header' (OS/2.usWinAscent)

        >>> font = Font("tests/fixtures/ttf/Font-Regular.ttf")
        >>> font.ascents.os2win
        1178
        """

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
        """ Returns least value of descents.

        >>> font = Font("tests/fixtures/ttf/Font-Regular.ttf")
        >>> font.descents.get_min()
        -384
        """
        return min(self.hhea, self.os2typo, self.os2win)

    def hhea():
        doc = """ Descent value in 'Horizontal Header' (hhea.descent)

        >>> font = Font("tests/fixtures/ttf/Font-Regular.ttf")
        >>> font.descents.hhea
        -384
        """

        def fget(self):
            return self.ttfont['hhea'].descent

        @is_none_protected
        def fset(self, value):
            self.ttfont['hhea'].descent = value

        return locals()
    hhea = property(**hhea())

    def os2typo():
        doc = """Descent value in 'Horizontal Header' (OS/2.sTypoDescender)

        >>> font = Font("tests/fixtures/ttf/Font-Regular.ttf")
        >>> font.descents.os2typo
        -384
        """

        def fget(self):
            return self.ttfont['OS/2'].sTypoDescender

        @is_none_protected
        def fset(self, value):
            self.ttfont['OS/2'].sTypoDescender = value

        return locals()
    os2typo = property(**os2typo())

    def os2win():
        doc = """Descent value in 'Horizontal Header' (OS/2.usWinDescent)

        >>> font = Font("tests/fixtures/ttf/Font-Regular.ttf")
        >>> font.descents.os2win
        384
        """

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


class FontTool:

    @staticmethod
    def get_tables(path):
        """ Retrieves tables names existing in font

        >>> FontTool.get_tables("tests/fixtures/ttf/Font-Regular.ttf")
        ['GDEF', 'gasp', 'loca', 'name', 'post', 'OS/2', 'maxp', 'head', \
'kern', 'FFTM', 'GSUB', 'glyf', 'GPOS', 'cmap', 'hhea', 'hmtx', 'DSIG']
        """
        font = ttLib.TTFont(path)
        return font.reader.tables.keys()
