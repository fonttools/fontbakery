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
        """ Retrieve length of glyf table

            >>> font = Font("tests/fixtures/ttf/Font-Regular.ttf")
            >>> font.get_glyf_length()
            21804
        """
        return self.ttfont.reader.tables['glyf'].length

    def get_loca_glyph_offset(self, num):
        """ Retrieve offset of glyph in font tables

            >>> font = Font("tests/fixtures/ttf/Font-Regular.ttf")
            >>> font.get_loca_glyph_offset(0)
            0L
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
