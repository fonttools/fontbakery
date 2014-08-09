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
import fontforge
import robofab.world
from cli.ttfont import Font


class PiFont(object):

    def __init__(self, path):
        """ Supplies common API interface to several font formats """
        self.font = PiFont.open(path)

    @staticmethod
    def open(path):
        """ Return file instance depending on font format

        >>> PiFont.open('tests/fixtures/src/Font-Italic.ufo')
        [PiFontUfo "tests/fixtures/src/Font-Italic.ufo"]
        >>> PiFont.open('tests/fixtures/ttf/Font-Italic.ttf')
        [PiFontFontTools "tests/fixtures/ttf/Font-Italic.ttf"]
        >>> PiFont.open('tests/fixtures/src/Font-Light.sfd')
        [PiFontSFD "tests/fixtures/src/Font-Light.sfd"]
         """
        if path[-4:] == '.ufo':
            return PiFontUfo(path)
        if path[-4:] in ['.ttf', '.otf', '.ttx']:
            return PiFontFontTools(path)
        if path[-4:] == '.sfd':
            return PiFontSFD(path)

    def get_glyphs(self):
        """ Retrieves glyphs list with their names

        Returns:
            :list: List of tuples describing glyphs sorted by glyph code
        """
        return self.font.get_glyphs()

    def get_contours_count(self, glyphname):
        """ Retrieves count of contours, including composites glyphs like "AE"

        Arguments:

            :glyphname string: glyph unicode name

        Returns:
            :int: count of contours
        """
        return self.font.get_contours_count(glyphname)

    def get_points_count(self, glyphname):
        """ Retrieves count of points, including composites glyphs like "AE"

        Arguments:
            :glyphname string: glyph unicode name

        Returns:
            :int: count of points
        """
        return self.font.get_points_count(glyphname)


class PiFontSFD:
    """ Supplies methods used by PiFont class to access SFD """

    def __init__(self, path):
        self.path = path
        self.font = fontforge.open(path)

    def __repr__(self):
        return '[PiFontSFD "%s"]' % self.path

    def get_glyphs(self):
        """ Retrieves glyphs list with their names

        >>> f = PiFont('tests/fixtures/src/Font-Light.sfd')
        >>> f.get_glyphs()[:3]
        [(-1, 'caron.alt'), (-1, 'foundryicon'), (2, 'uni0002')]
        """
        ll = self.font.glyphs()
        return sorted(map(lambda x: (x.unicode, x.glyphname), ll))


class PiFontUfo:
    """ Supplies methods used by PiFont class to access UFO """

    def __init__(self, path):
        self.path = path
        self.font = robofab.world.OpenFont(path)

    def __repr__(self):
        return '[PiFontUfo "%s"]' % self.path

    def get_glyphs(self):
        """ Retrieves glyphs list with their names

        >>> f = PiFont('tests/fixtures/src/Font-Italic.ufo')
        >>> f.get_glyphs()[:3]
        [(2, 'uni0002'), (9, 'uni0009'), (10, 'uni000A')]
        """
        ll = zip(self.font.getCharacterMapping(),
                 map(lambda x: x[0],
                     self.font.getCharacterMapping().values()))
        return sorted(ll)

    def get_contours_count(self, glyphname):
        """ Retrieves count of glyph contours

        >>> f = PiFont('tests/fixtures/src/Font-Italic.ufo')
        >>> f.get_contours_count('AEacute')
        3
        """
        value = 0
        components = self.font[glyphname].getComponents()
        if components:
            for component in components:
                value += self.get_contours_count(component.baseGlyph)

        contours = self.font[glyphname].contours
        if contours:
            value += len(contours)
        return value

    def get_points_count(self, glyphname):
        """ Retrieves count of glyph points in contours

        >>> f = PiFont('tests/fixtures/src/Font-Italic.ufo')
        >>> f.get_points_count('AEacute')
        24
        """
        value = 0
        components = self.font[glyphname].getComponents()
        if components:
            for component in components:
                value += self.get_points_count(component.baseGlyph)

        contours = self.font[glyphname].contours
        if contours:
            for contour in contours:
                value += len(contour.segments)
        return value


class PiFontFontTools:
    """ Supplies methods used by PiFont class to access TTF """

    def __init__(self, path):
        self.path = path
        self.font = Font.get_ttfont(path)

    def __repr__(self):
        return '[PiFontFontTools "%s"]' % self.path

    def get_glyphs(self):
        """ Retrieves glyphs list with their names

        >>> f = PiFont('tests/fixtures/ttf/Font-Italic.ttf')
        >>> f.get_glyphs()[:3]
        [(32, 'space'), (33, 'exclam'), (34, 'quotedbl')]
        """
        cmap4 = self.font.retrieve_cmap_format_4().cmap
        ll = zip(cmap4, cmap4.values())
        return sorted(ll)
