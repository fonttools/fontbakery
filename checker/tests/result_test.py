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

from checker.base import BakeryTestCase as TestCase, tags
import fontforge
import unicodedata
import yaml
import os
import re
import subprocess
import sys
import magic

from fontTools import ttLib
from bakery.app import app


weights = {
    'Thin': 100,
    'ThinItalic': 100,
    'ExtraLight': 200,
    'ExtraLightItalic': 200,
    'Light': 300,
    'LightItalic': 300,
    'Regular': 400,
    'Italic': 400,
    'Medium': 500,
    'MediumItalic': 500,
    'SemiBold': 600,
    'SemiBoldItalic': 600,
    'Bold': 700,
    'BoldItalic': 700,
    'ExtraBold': 800,
    'ExtraBoldItalic': 800,
    'Black': 900,
    'BlackItalic': 900,
}


weights_styles_map = {
    'normal': ['Thin', 'ExtraLight', 'Light', 'Regular', 'Medium', 'SemiBold',
               'Bold', 'ExtraBold', 'Black'],
    'italic': ['ThinItalic', 'ExtraLightItalic', 'LightItalic', 'Italic',
               'MediumItalic', 'SemiBoldItalic', 'BoldItalic',
               'ExtraBoldItalic', 'BlackItalic']
}


valid_styles = weights_styles_map['normal'] + weights_styles_map['italic']

italics_styles = {
    'ThinItalic': 'Thin Italic',
    'ExtraLight': 'Extra Light',
    'ExtraLightItalic': 'Extra Light Italic',
    'LightItalic': 'Light Italic',
    'Italic': 'Italic',
    'MediumItalic': 'Medium Italic',
    'SemiBoldItalic': 'Semi Bold Italic',
    'BoldItalic': 'Bold Italic',
    'ExtraBoldItalic': 'Extra Bold Italic',
    'BlackItalic': 'Black Italic',
}


normal_styles = {
    'Thin': 'Thin',
    'ExtraLight': 'Extra Light',
    'Light': 'Light',
    'Regular': 'Regular',
    'Italic': 'Italic',
    'Medium': 'Medium',
    'SemiBold': 'Semi Bold',
    'Bold': 'Bold',
    'ExtraBold': 'Extra Bold',
    'Black': 'Black'
}


def prun(command, cwd, log=None):
    """
    Wrapper for subprocess.Popen that capture output and return as result

        :param command: shell command to run
        :param cwd: current working dir
        :param log: loggin object with .write() method

    """
    env = os.environ.copy()
    env.update({'PYTHONPATH': os.pathsep.join(sys.path)})
    p = subprocess.Popen(command, shell=True, cwd=cwd,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         close_fds=True, env=env)
    stdout = p.communicate()[0]
    if log:
        log.write('$ %s' % command)
        log.write(stdout)
    return stdout


class OTSTest(TestCase):

    targets = ['result']
    tool = 'OTS'
    name = __name__
    path = '.'

    @tags('required',)
    def test_ots(self):
        """ Is TTF file correctly sanitized for Firefox and Chrome """
        stdout = prun('{0} {1}'.format(app.config['OTS_BINARY_PATH'],
                                       self.path),
                      app.config['ROOT'])
        self.assertEqual('', stdout.replace('\n', '. '))


class FontToolsTest(TestCase):
    targets = ['result']
    tool = 'FontTools'
    name = __name__
    path = '.'

    def setUp(self):
        self.font = ttLib.TTFont(self.path)

    def test_camelcase_in_fontname(self):
        """ Font family is not CamelCase'd """
        metadata = self.get_metadata()
        self.assertTrue(bool(re.match(r'([A-Z][a-z]+){2,}', metadata['name'])),
                        msg='May be you have to use space in family')

    def test_prep_magic_code(self):
        """ Font contains in PREP table magic code """
        magiccode = '\xb8\x01\xff\x85\xb0\x04\x8d'
        try:
            bytecode = self.font['prep'].program.getBytecode()
        except KeyError:
            bytecode = ''
        self.assertTrue(bytecode == magiccode,
                        msg='PREP does not contain magic code')

    @tags('required')
    def test_macintosh_platform_names_matches_windows_platform(self):
        """ Font names are equal for Macintosh and Windows
            specific-platform """
        result_string_dicts = {}
        for name in self.font['name'].names:
            if name.nameID not in result_string_dicts:
                result_string_dicts[name.nameID] = {'mac': '', 'win': ''}
            if name.platformID == 3:  # Windows platform-specific
                result_string_dicts[name.nameID]['win'] = name.string
                if b'\000' in name.string:
                    result_string_dicts[name.nameID]['win'] = name.string.decode('utf-16-be').encode('utf-8')
            if name.platformID == 1:  # Macintosh platform-specific
                result_string_dicts[name.nameID]['mac'] = name.string
                if b'\000' in name.string:
                    result_string_dicts[name.nameID]['mac'] = name.string.decode('utf-16-be').encode('utf-8')
        for row in result_string_dicts.values():
            self.assertEqual(row['win'], row['mac'])

    def test_tables(self):
        """ List of tables that shoud be in font file """
        # xen: actually I take this list from most popular open font Open Sans,
        # belive that it is most mature.
        # This list should be reviewed
        tables = ['GlyphOrder', 'head', 'hhea', 'maxp', 'OS/2', 'hmtx',
                  'cmap', 'fpgm', 'prep', 'cvt ', 'loca', 'glyf', 'name',
                  'post', 'gasp', 'GDEF', 'GPOS', 'GSUB', 'DSIG']

        for x in self.font.keys():
            self.assertIn(x, tables, msg="%s does not exist in font" % x)

    @tags('required')
    def test_license_url_is_included_and_correct(self):
        """ License URL is included and correct url """
        licenseurl = self.font['name'].names[13].string
        if b'\000' in licenseurl:
            licenseurl = licenseurl.decode('utf-16-be').encode('utf-8')

        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
            r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        self.assertTrue(regex.match(licenseurl))

    def get_postscript_name(self):
        fontname = self.font['name'].names[6].string
        if b'\000' in fontname:
            return fontname.decode('utf-16-be').encode('utf-8')
        return fontname

    def get_font_fullname(self):
        fontname = self.font['name'].names[4].string
        if b'\000' in fontname:
            return fontname.decode('utf-16-be').encode('utf-8')
        return fontname

    def test_metadata_weight_matches_postscriptname(self):
        """ Metadata weight matches postScriptName """
        metadata = self.get_metadata()
        pair = []
        for k, weight in weights.items():
            if weight == metadata['weight']:
                pair.append(k)
        self.assertTrue(metadata['postScriptName'].endswith('-%s' % pair[0]) or metadata['postScriptName'].endswith('-%s' % pair[1]))

    @tags(['required', 'info'])
    def test_metadata_copyright_contains_rfn(self):
        """ Copyright string should contains 'Reserved Font Name' substring """
        metadata = self.get_metadata()
        self.assertIn('Reserved Font Name', metadata['copyright'])

    @tags('required')
    def test_metadata_copyright_matches_pattern(self):
        """ Copyright string matches to Copyright * 20\d\d * (*@*.*) """
        metadata = self.get_metadata()
        self.assertRegexpMatches(metadata['copyright'],
                                 r'Copyright\s+\(c\)\s+20\d{2}.*\(.*@.*.*\)')

    @tags('required')
    def test_metadata_weight_in_range(self):
        """ Font weight should be in range from 100 to 900, step 100 """
        metadata = self.get_metadata()
        self.assertTrue(metadata.get('weight', 0) in range(100, 1000, 100))

    # TODO: Ask Dave about "Check that font.weight keys match the style names"
    # @tags('required')
    # def test_font_weight_matches_italic_style(self):
    #     font_metadata = self.get_metadata()
    #     for k, weight in weights.items():
    #         if weight == font_metadata.get('weight'):
    #             self.assertIn(k, weights_styles_map[font_metadata['style']])

    @tags('required')
    def test_metadata_fonts_fields(self):
        """ METADATA.json "fonts" property items should have
            "name", "postScriptName", "fullName", "style", "weight",
            "filename", "copyright" keys """
        keys = ["name", "postScriptName", "fullName", "style", "weight",
                "filename", "copyright"]
        metadata = self.get_metadata()
        for j in keys:
            self.assertTrue(j in metadata)

    def test_fontname_is_equal_to_macstyle(self):
        """ Is internal fontname is equal to macstyle flags """
        fontname = self.get_postscript_name()
        macStyle = self.font['head'].macStyle
        weight_style = fontname.split('-')[1]
        if 'Italic' in weight_style:
            self.assertTrue(macStyle & 0b10)
        if 'Bold' in weight_style:
            self.assertTrue(macStyle & 0b01)

    def get_metadata(self):
        medatata_path = os.path.join(os.path.dirname(self.path),
                                     'METADATA.json')
        metadata = yaml.load(open(medatata_path, 'r').read())
        font_metadata = {}
        for font in metadata.get('fonts', []):
            if os.path.basename(self.path) == font['filename']:
                font_metadata = font
                print font_metadata
                break
        self.assertTrue(font_metadata)
        return font_metadata

    def test_font_italic_style_matches_internal_font_properties_values(self):
        """ Check metadata.json font.style `italic` matches font internal """
        font_metadata = self.get_metadata()
        psname = self.get_postscript_name()
        fullname = self.get_font_fullname()
        if font_metadata['style'] != 'italic':
            return
        self.assertTrue(self.font['head'].macStyle & 0b10)
        self.assertTrue(any([psname.endswith('-' + x)
                             for x in italics_styles.keys()]))
        self.assertTrue(any([fullname.endswith(' ' + x)
                             for x in italics_styles.values()]))

    def test_font_normal_style_matches_internal_font_properties_values(self):
        """ Check metadata.json font.style `normal` matches font internal """
        font_metadata = self.get_metadata()
        psname = self.get_postscript_name()
        fullname = self.get_font_fullname()
        if font_metadata['style'] != 'normal':
            return
        self.assertTrue(any([psname.endswith('-' + x)
                             for x in normal_styles.keys()]))
        self.assertTrue(any([fullname.endswith(' ' + x)
                             for x in normal_styles.values()]))
        self.assertFalse(self.font['head'].macStyle & 0b10)

    @tags('required')
    def test_metadata_font_keys_types(self):
        """ METADATA.json fonts items dicts items should have proper types """
        metadata = self.get_metadata()
        self.assertEqual(type(metadata.get("name", None)), type(""))
        self.assertEqual(type(metadata.get("postScriptName", None)), type(""))
        self.assertEqual(type(metadata.get("fullName", None)), type(""))
        self.assertEqual(type(metadata.get("style", None)), type(""))
        self.assertEqual(type(metadata.get("weight", None)), type(0))
        self.assertEqual(type(metadata.get("filename", None)), type(""))
        self.assertEqual(type(metadata.get("copyright", None)), type(""))

    @tags('required')
    def test_metadata_fonts_no_unknown_keys(self):
        """ METADATA.json fonts don't have unknown top keys """
        fonts_keys = ["name", "postScriptName", "fullName", "style", "weight",
                      "filename", "copyright"]
        metadata = self.get_metadata()
        for i in metadata.keys():
            self.assertIn(i, fonts_keys, msg="`%s` is unknown key in json" % i)

    @tags('required')
    def test_font_has_dsig_table(self):
        """ Check that font has DSIG table """
        self.assertIn('DSIG', self.font.keys(),
                      msg="`dsig` does not exist in font")

    def test_font_gpos_table_has_kerning_info(self):
        """ GPOS table has kerning information """
        self.assertIn('GPOS', self.font.keys(),
                      msg="`gpos` does not exist in font")
        flaglookup = False
        for lookup in self.font['GPOS'].table.LookupList.Lookup:
            if lookup.LookupType == 2:  # Adjust position of a pair of glyphs
                flaglookup = lookup
        self.assertTrue(flaglookup, msg='GPOS doesnt have kerning information')
        self.assertGreater(flaglookup.SubTableCount, 0)
        self.assertGreater(flaglookup.SubTable[0].PairSetCount, 0)

    def test_metadata_family_matches_fullname_psname_family_part(self):
        """ Check that METADATA.json family matches fullName
            and postScriptName family part"""
        font_metadata = self.get_metadata()
        psname = self.get_postscript_name()
        fullname = self.get_font_fullname()
        self.assertTrue(psname.startswith(font_metadata['name'] + '-'))
        self.assertTrue(fullname.startswith(font_metadata['name'] + ' '))

    def test_no_kern_table_exists(self):
        """ Check that no KERN table exists """
        self.assertNotIn('kern', self.font.keys())

    def test_table_gasp_type(self):
        """ Font table gasp should be 15 """
        keys = self.font.keys()
        self.assertIn('gasp', keys, msg="GASP table not found")
        self.assertEqual(type({}), type(self.font['gasp'].gaspRange),
            msg="GASP table: gaspRange method value have wrong type")
        self.assertTrue(65535 in self.font['gasp'].gaspRange)
        # XXX: Needs review
        self.assertEqual(self.font['gasp'].gaspRange[65535], 15)

    def test_metrics_linegaps_are_zero(self):
        """ All values for linegap in 'hhea' and 'OS/2' tables
        should be equal zero """
        self.assertEqual(self.font['hhea'].lineGap, 0)
        self.assertEqual(self.font['OS/2'].sTypoLineGap, 0)

    def test_metrics_ascents_equal_max_bbox(self):
        """ Value for ascents in 'hhea' and 'OS/2' tables should be equal
        to value of glygh with biggest yMax"""

        ymax = 0
        for g in self.font['glyf'].glyphs:
            char = self.font['glyf'][g]
            if hasattr(char, 'yMax') and ymax < char.yMax:
                ymax = char.yMax

        self.assertEqual(self.font['hhea'].ascent, ymax)
        self.assertEqual(self.font['OS/2'].sTypoAscender, ymax)
        self.assertEqual(self.font['OS/2'].usWinAscent, ymax)

    def test_metrics_descents_equal_min_bbox(self):
        """ Value for descents in 'hhea' and 'OS/2' tables should be equal
        to value of glygh with smallest yMin"""

        ymin = 0
        for g in self.font['glyf'].glyphs:
            char = self.font['glyf'][g]
            if hasattr(char, 'yMin') and ymin > char.yMin:
                ymin = char.yMin

        self.assertEqual(self.font['hhea'].descent, ymin)
        self.assertEqual(self.font['OS/2'].sTypoDescender, ymin)
        self.assertEqual(self.font['OS/2'].usWinDescent, ymin)

    def test_non_ascii_chars_in_names(self):
        """ NAME and CFF tables must not contain non-ascii characters """
        for name_record in self.font['name'].names:
            string = name_record.string
            if b'\000' in string:
                string = string.decode('utf-16-be').encode('utf-8')
            else:
                string = string
            try:
                string.encode('ascii')
            except UnicodeEncodeError:
                self.fail("%s contain non-ascii chars" % name_record.nameID)


class FontForgeSimpleTest(TestCase):
    targets = ['result']
    tool = 'FontForge'
    name = __name__
    path = '.'

    def setUp(self):
        self.font = fontforge.open(self.path)
        self.fname = os.path.splitext(self.path)[0]
        # You can use ipdb here to interactively develop tests!
        # Uncommand the next line, then at the iPython prompt: print(self.path)
        # import ipdb; ipdb.set_trace()

    # TODO: Ask Dave about this test
    # def test_pfm_family_style_is_correct(self):
    #     """ PFM Family Style is valid. Valid value are: Serif, Sans-Serif,
    #         Monospace, Decorative """
    #     self.assertIn(self.font.os2_pfm_family,
    #                   ['Serif', 'Sans-Serif', 'Monospace', 'Decorative'],
    #                   'PFM Family Style is not valid.')

    def get_metadata(self):
        medatata_path = os.path.join(os.path.dirname(self.path),
                                     'METADATA.json')
        metadata = yaml.load(open(medatata_path, 'r').read())
        return metadata

    def test_metrics_maximum_advanced_width_in_hhea(self):
        """ Actual maximum advanced width is consistent to
            hhea.advanceWidthMax """
        maxwidth = 0
        ttfont = ttLib.TTFont(self.path)
        for g in self.font.glyphs():
            if hasattr(g, 'width') and maxwidth < g.width:
                maxwidth = g.width
        self.assertEqual(ttfont['hhea'].advanceWidthMax, maxwidth)

    def test_metrics_advance_width_in_glyphs_same_if_monospace(self):
        """ Monospace font has hhea.advanceWidthMax equal to each
            glyph advanceWidth """
        metadata = self.get_metadata()
        if metadata.get('category') != 'Monospace':
            return
        ttfont = ttLib.TTFont(self.path)
        advance_width = None
        for g in self.font.glyphs():
            if not advance_width:
                advance_width = g.width
            self.assertEqual(advance_width, g.width)
        self.assertEqual(ttfont['hhea'].advanceWidthMax, advance_width)

    @tags('required')
    def test_font_italicangle_is_zero_or_negative(self):
        """ font.italicangle property can be zero or negative """
        if self.font.italicangle == 0:
            self.assertEqual(self.font.italicangle, 0)
        else:
            self.assertLess(self.font.italicangle, 0)

    @tags('required')
    def test_is_fsType_not_set(self):
        """Is the OS/2 table fsType set to 0?"""
        self.assertEqual(self.font.os2_fstype, 0)

    @tags('required',)
    def test_nbsp(self):
        """Check if 'NO-BREAK SPACE' exsist in font glyphs"""
        self.assertTrue(ord(unicodedata.lookup('NO-BREAK SPACE')) in self.font)

    @tags('required',)
    def test_space(self):
        """Check if 'SPACE' exsist in font glyphs"""
        self.assertTrue(ord(unicodedata.lookup('SPACE')) in self.font)

    @tags('required',)
    def test_nbsp_and_space_glyphs_width(self):
        """ Nbsp and space glyphs should have the same width"""
        space = 0
        nbsp = 0
        for x in self.font.glyphs():
            if x.unicode == ord(unicodedata.lookup('NO-BREAK SPACE')):
                nbsp = x.width
            elif x.unicode == ord(unicodedata.lookup('SPACE')):
                space = x.width
        self.assertEqual(space, nbsp)

    def test_euro(self):
        """Check if 'EURO SIGN' exsist in font glyphs"""
        self.assertTrue(ord(unicodedata.lookup('EURO SIGN')) in self.font)

    def test_font_weight_is_canonical(self):
        """ Font weight property is from canonical styles list"""
        self.assertIn(self.font.weight, valid_styles,
                      'Font weight does not match for any valid styles')

    def test_font_name_canonical(self):
        """ Font name is canonical """
        self.assertTrue(any([self.font.fontname.endswith(x)
                             for x in valid_styles]))

    def test_font_file_name_canonical(self):
        """ Font name is canonical """
        name = os.path.basename(self.path)
        canonic_name = "%s-%s.ttf" % (self.font.familyname, self.font.weight)
        self.assertEqual(name, canonic_name)

    @tags('required')
    def test_menu_file_exists(self):
        """ Menu file have font-name-style.menu format """
        self.assertTrue(os.path.exists("%s.menu" % self.fname))

    @tags('required')
    def test_latin_file_exists(self):
        """ Menu file have font-name-style.menu format """
        self.assertTrue(os.path.exists("%s.latin" % self.fname))

    def test_menu_file_is_canonical(self):
        """ Menu file should be [font.familyname]-[font.weight].menu """
        name = "%s.menu" % self.fname
        canonic_name = "%s-%s.menu" % (self.font.familyname, self.font.weight)
        self.assertEqual(os.path.basename(name), canonic_name)

    @tags('required')
    def test_menu_file_is_font(self):
        """ Menu file have font-name-style.menu format """
        self.assertTrue(os.path.exists("%s.menu" % self.fname))
        self.assertTrue(magic.from_file("%s.menu" % self.fname),
                        'TrueType font data')

    @tags('required')
    def test_file_is_font(self):
        """ Menu file have font-name-style.menu format """
        self.assertTrue(os.path.exists(self.path))
        self.assertTrue(magic.from_file(self.path), 'TrueType font data')

    @tags('required')
    def test_em_is_1000(self):
        """ Font em should be equal 1000 """
        self.assertEqual(self.font.em, 1000)

    @tags('required')
    def test_font_italicangle_limits(self):
        """ font.italicangle maximum abs(value) can be between 0 an 20 degree """
        # VV: This test will passed only in case of italicAngle is zero.
        self.assertTrue(abs(self.font.italicangle) >= 0
                        and abs(self.font.italicangle) <= 20)

    @tags('required')
    def test_font_is_font(self):
        """ File provided as parameter is TTF font file """
        self.assertTrue(magic.from_file(self.path, mime=True),
                        'application/x-font-ttf')

    @tags('required')
    def test_copyrighttxt_exists(self):
        """ Font folder should contains COPYRIGHT.txt """
        self.assertTrue(os.path.exists(os.path.join(
            os.path.dirname(self.path), 'COPYRIGHT.txt')))

    @tags('required')
    def test_description_exists(self):
        """ Font folder should contains DESCRIPTION.en_us.html """
        self.assertTrue(os.path.exists(os.path.join(
            os.path.dirname(self.path), 'DESCRIPTION.en_us.html')))

    @tags('required')
    def test_licensetxt_exists(self):
        """ Font folder should contains LICENSE.txt """
        # TODO: This should be OFL.txt or LICENSE.txt
        self.assertTrue(os.path.exists(os.path.join(
            os.path.dirname(self.path), 'LICENSE.txt')))

    def test_fontlogtxt_exists(self):
        """ Font folder should contains FONTLOG.txt """
        self.assertTrue(os.path.exists(os.path.join(
            os.path.dirname(self.path), 'FONTLOG.txt')))


class FontForgeValidateStateTest(TestCase):

    targets = ['result']
    tool = 'FontForge'
    name = __name__
    path = '.'
    longMessage = True

    def setUp(self):
        font = fontforge.open(self.path)
        self.validation_state = font.validate()

    def test_validation_open_contours(self):
        """ Glyphs do not have opened contours """
        self.assertFalse(bool(self.validation_state & 0x2))

    def test_validation_glyph_intersect(self):
        """ Glyphs do not intersect somewhere """
        self.assertFalse(bool(self.validation_state & 0x4))

    def test_wrong_direction_in_glyphs(self):
        """ Contours do not have wrong direction """
        self.assertFalse(bool(self.validation_state & 0x8))

    def test_flipped_reference_in_glyphs(self):
        """ Reference in the glyph haven't been flipped """
        self.assertFalse(bool(self.validation_state & 0x10))

    def test_missing_extrema_in_glyphs(self):
        """ Glyphs do not have missing extrema """
        self.assertFalse(bool(self.validation_state & 0x20))

    def test_referenced_glyphs_are_present(self):
        """ Glyph names referred to from glyphs present in the font """
        self.assertFalse(bool(self.validation_state & 0x40))

    def test_points_are_not_too_far_apart(self):
        """ Points (or control points) are not too far apart """
        self.assertFalse(bool(self.validation_state & 0x40000))

    def test_postscript_hasnt_limit_points_in_glyphs(self):
        """ PostScript has not a limit of 1500 points in glyphs """
        self.assertFalse(bool(self.validation_state & 0x80))

    def test_postscript_hasnt_limit_hints_in_glyphs(self):
        """ PostScript hasnt a limit of 96 hints in glyphs """
        self.assertFalse(bool(self.validation_state & 0x100))

    def test_valid_glyph_names(self):
        """ Font doesn't have invalid glyph names """
        self.assertFalse(bool(self.validation_state & 0x200))

    def test_allowed_numbers_points_in_glyphs(self):
        """ Glyphs have allowed numbers of points defined in maxp """
        self.assertFalse(bool(self.validation_state & 0x400))

    def test_allowed_numbers_paths_in_glyphs(self):
        """ Glyphs have allowed numbers of paths defined in maxp """
        self.assertFalse(bool(self.validation_state & 0x800))

    def test_allowed_numbers_points_in_composite_glyphs(self):
        """ Composite glyphs have allowed numbers of points defined in maxp """
        self.assertFalse(bool(self.validation_state & 0x1000))

    def test_allowed_numbers_paths_in_composite_glyphs(self):
        """ Composite glyphs have allowed numbers of paths defined in maxp """
        self.assertFalse(bool(self.validation_state & 0x2000))

    def test_valid_length_instructions(self):
        """ Glyphs instructions have valid lengths """
        self.assertFalse(bool(self.validation_state & 0x4000))

    def test_points_are_integer_aligned(self):
        """ Points in glyphs are integer aligned """
        self.assertFalse(bool(self.validation_state & 0x80000))

    def test_missing_anchors(self):
        """ Glyphs have not missing anchor.

            According to the opentype spec, if a glyph contains an anchor point
            for one anchor class in a subtable, it must contain anchor points
            for all anchor classes in the subtable. Even it, logically,
            they do not apply and are unnecessary. """
        self.assertFalse(bool(self.validation_state & 0x100000))

    def test_duplicate_glyphs(self):
        """ Font does not have duplicated glyphs.

            Two (or more) glyphs in this font have the same name. """
        self.assertFalse(bool(self.validation_state & 0x200000))

    def test_duplicate_unicode_codepoints(self):
        """ Glyphs do not have duplicate unicode code points.

            Two (or more) glyphs in this font have the code point. """
        self.assertFalse(bool(self.validation_state & 0x400000))

    def test_overlapped_hints(self):
        """ Glyphs do not have overlapped hints """
        self.assertFalse(bool(self.validation_state & 0x800000))


class MetadataJSONTest(TestCase):
    targets = ['result']
    tool = 'FontForge'
    name = __name__
    path = '.'
    longMessage = True

    def setUp(self):
        self.font = fontforge.open(self.path)
        medatata_path = os.path.join(os.path.dirname(self.path),
                                     'METADATA.json')
        self.metadata = yaml.load(open(medatata_path, 'r').read())
        self.fname = os.path.splitext(self.path)[0]
        self.root_dir = os.path.dirname(self.path)

    def test_the_same_number_of_glyphs_across_family(self):
        """ The same number of glyphs across family? """
        numbers_of_glyphs = 0
        for resultdata in self.metadata.get('fonts', []):
            font = fontforge.open(os.path.join(self.root_dir, resultdata['filename']))
            if not numbers_of_glyphs:
                numbers_of_glyphs = len(list(font.glyphs()))
            self.assertEqual(numbers_of_glyphs, len(list(font.glyphs())))
            font.close()

    def test_the_same_names_of_glyphs_across_family(self):
        """ The same names of glyphs across family? """
        glyphs = None
        for resultdata in self.metadata.get('fonts', []):
            font = fontforge.open(os.path.join(self.root_dir, resultdata['filename']))
            if not glyphs:
                glyphs = map(lambda g: g.glyphname, font.glyphs())
            self.assertEqual(glyphs, map(lambda g: g.glyphname, font.glyphs()))

    def test_the_same_encodings_of_glyphs_across_family(self):
        """ The same unicode encodings of glyphs across family? """
        glyphs = None
        for resultdata in self.metadata.get('fonts', []):
            font = fontforge.open(os.path.join(self.root_dir, resultdata['filename']))
            if not glyphs:
                glyphs = map(lambda g: g.encoding, font.glyphs())
            self.assertEqual(glyphs, map(lambda g: g.encoding, font.glyphs()))

    def test_family_is_listed_in_gwf(self):
        """ Fontfamily is listed in Google Font Directory """
        import requests
        url = 'http://fonts.googleapis.com/css?family=%s' % self.metadata['name'].replace(' ', '+')
        fp = requests.get(url)
        self.assertTrue(fp.status_code == 200, 'No family found in GWF in %s' % url)
        self.assertEqual(self.metadata.get('visibility'), 'External')

    def test_metadata_family_matches_font_filenames(self):
        """ Check that METADATA family value matches font filenames """
        family = ''
        for x in self.metadata.get('fonts', []):
            if os.path.basename(self.path) == x['filename']:
                family = x['name']
                break
        self.assertTrue(family)
        self.assertTrue(os.path.basename(self.path).startswith(family))

    def test_metadata_family_values_are_all_the_same(self):
        """ Check that METADATA family values are all the same """
        families_names = set([x['name'] for x in self.metadata.get('fonts')])
        self.assertEqual(len(set(families_names)), 1)

    @tags('required',)
    def test_metadata_family(self):
        """ Font and METADATA.json have the same name """
        self.assertEqual(self.font.familyname, self.metadata.get('name', None))

    def test_metadata_font_have_regular(self):
        """ According GWF standarts font should have Regular style. """
        # this tests will appear in each font
        have = False
        for i in self.metadata['fonts']:
            if i['fullName'].endswith('Regular'):
                have = True

        self.assertTrue(have)

    @tags('required',)
    def test_metadata_regular_is_400(self):
        """ Usually Regular should be 400 """
        have = False
        for i in self.metadata['fonts']:
            if i['fullName'].endswith('Regular') \
                    and int(i.get('weight', 0)) == 400:
                have = True

        self.assertTrue(have)

    def test_metadata_regular_is_normal(self):
        """ Usually Regular should be normal style """
        have = False
        for x in self.metadata.get('fonts', None):
            if x.get('fullName', '').endswith('Regular') \
                    and x.get('style', '') == 'normal':
                have = True
        self.assertTrue(have)

    styles = ['Thin', 'ThinItalic', 'ExtraLight',
              'ExtraLightItalic', 'Light', 'LightItalic', 'Regular', 'Italic',
              'Medium', 'MediumItalic', 'SemiBold', 'SemiBoldItalic', 'Bold',
              'BoldItalic', 'ExtraBold', 'ExtraBoldItalic',
              'Black', 'BlackItalic']

    # test each key for font item:
    # {
    #   "name": "Merritest", --- doesn't incule style name
    #   "postScriptName": "Merritest-Bold", ---
    #   "fullName": "Merritest Bold", ---
    #   "style": "normal",
    #   "weight": 700,
    #   "filename": "Merritest-Bold.ttf", ---
    #   "copyright": "Merriweather is a medium contrast semi condesed typeface
    #         designed to be readable at very small sizes. Merriweather is
    #         traditional in feeling despite a the modern shapes it has adopted
    #         for screens."
    # },

    def test_metadata_fonts_exists(self):
        """ METADATA.json font propery should exists """
        self.assertTrue(self.metadata.get('fonts', False))

    def test_metadata_fonts_list(self):
        """ METADATA.json font propery should be list """
        self.assertEqual(type(self.metadata.get('fonts', False)), type([]))

    def test_metadata_font_name_canonical(self):
        """ METADATA.json fonts 'name' property should be
            same as font familyname """
        self.assertTrue(all([x['name'] == self.font.familyname
                             for x in self.metadata.get('fonts', None)]))

    @tags('required')
    def test_metadata_postScriptName_canonical(self):
        """ METADATA.json fonts postScriptName should be
            [font familyname]-[style].

            Alowed styles are: 'Thin', 'ThinItalic', 'ExtraLight',
            'ExtraLightItalic', 'Light', 'LightItalic', 'Regular', 'Italic',
            'Medium', 'MediumItalic', 'SemiBold', 'SemiBoldItalic', 'Bold',
            'BoldItalic', 'ExtraBold', 'ExtraBoldItalic', 'Black',
            'BlackItalic' """
        self.assertTrue(all(
            [any([x['postScriptName'].endswith("-" + i)
             for i in valid_styles]) for x in self.metadata.get('fonts', None)]
        ))

    @tags('required')
    def test_metadata_style_matches_postScriptName(self):
        """ METADATA.json `style` is matched to `postScriptName` property """
        sn_italic = ['ThinItalic', 'ExtraLightItalic', 'LightItalic',
                     'Italic', 'MediumItalic', 'SemiBoldItalic', 'BoldItalic',
                     'ExtraBoldItalic', 'BlackItalic']
        for x in self.metadata.get("fonts", None):
            post_script_name = x.get('postScriptName', '')
            style = x.get('style', '')
            if style == 'italic':
                self.assertTrue(any([post_script_name.endswith("-" + i)
                                     for i in sn_italic]))
            else:
                self.assertEqual(style, 'normal')

    @tags('required')
    def test_metadata_filename_matches_postScriptName(self):
        """ METADATA.json `filename` is matched to `postScriptName`
            property """
        for x in self.metadata.get("fonts", None):
            post_script_name = x.get('postScriptName', '')
            filename = x.get('filename', '')
            self.assertEqual(os.path.splitext(filename)[0], post_script_name)

    @tags('required')
    def test_metadata_fullname_matches_postScriptName(self):
        """ METADATA.json `fullName` is matched to `postScriptName`
            property """
        for x in self.metadata.get("fonts", None):
            post_script_name = x.get('postScriptName', '').replace('-', ' ')
            fullname = x.get('fullName', '')
            self.assertEqual(fullname, post_script_name)

    @tags('required')
    def test_metadata_postScriptName_matches_internal_fontname(self):
        """ Checks that METADATA.json 'postScriptName' value matches
            font internal 'fontname' metadata """
        for font in self.metadata.get('fonts', []):
            if font['filename'] != os.path.basename(self.fname):
                continue
            self.assertEqual(font['postScriptName'], self.font.fontname)

    @tags('required')
    def test_metadata_postScriptName_matches_font_filename(self):
        """ Checks that METADATA.json 'postScriptName' value matches
            font internal 'fontname' metadata """
        for font in self.metadata.get('fonts', []):
            font_filename = os.path.basename(self.fname)
            if font['filename'] != font_filename:
                continue
            self.assertEqual(font['postScriptName'],
                             os.path.splitext(font_filename)[0])

    def test_metadata_font_fullname_canonical(self):
        """ METADATA.json fonts fullName property should be
            '[font.familyname] [font.style]' format (w/o quotes)"""
        for x in self.metadata.get("fonts", None):
            style = None
            fn = x.get('fullName', None)
            for i in valid_styles:
                if fn.endswith(i):
                    style = i
                    break
            self.assertTrue(style)
            self.assertEqual("%s %s" % (self.font.familyname, style), fn)

    @tags('required')
    def test_metadata_font_filename_canonical(self):
        """ METADATA.json fonts filename property should be
            [font.familyname]-[font.style].ttf format."""
        for x in self.metadata.get("fonts", None):
            style = None
            fn = x.get('filename', None)
            for i in valid_styles:
                if fn.endswith("-%s.ttf" % i):
                    style = i
                    break
            self.assertTrue(style, msg="%s not in canonical format" % x.get('filename', None))
            self.assertEqual("%s-%s.ttf" % (self.font.familyname, style), fn)

    def test_metadata_fonts_no_dupes(self):
        """ METADATA.json fonts propery only should have uniq values """
        fonts = {}
        for x in self.metadata.get('fonts', None):
            self.assertFalse(x.get('fullName', '') in fonts)
            fonts[x.get('fullName', '')] = x

        self.assertEqual(len(set(fonts.keys())),
                         len(self.metadata.get('fonts', None)))

    def test_metadata_contains_current_font(self):
        """ METADATA.json should contains testing font, under canonic name"""
        font = None
        current_font = "%s %s" % (self.font.familyname, self.font.weight)
        for x in self.metadata.get('fonts', None):
            if x.get('fullName', None) == current_font:
                font = x
                break

        self.assertTrue(font)

    def test_metadata_fullname_is_equal_to_internal_font_fullname(self):
        """ METADATA.json 'fullname' value matches internal 'fullname' """
        metadata_fullname = ''
        for font in self.metadata.get('fonts', []):
            if font['filename'] == os.path.basename(self.path):
                metadata_fullname = font['fullName']
                break
        self.assertEqual(self.font.fullname, metadata_fullname)

    def test_metadata_fonts_fields_have_fontname(self):
        """ METADATA.json fonts items fields "name", "postScriptName",
            "fullName", "filename" contains font name right format """
        for x in self.metadata.get('fonts', None):
            self.assertIn(self.font.familyname, x.get('name', ''))
            self.assertIn(self.font.familyname, x.get('fullName', ''))
            self.assertIn("".join(str(self.font.familyname).split()),
                          x.get('filename', ''))
            self.assertIn("".join(str(self.font.familyname).split()),
                          x.get('postScriptName', ''))

    def test_metadata_style_value_matches_font_italicAngle_value(self):
        """ METADATA.json fonts style property should be italic
            if font is italic """
        font = None
        current_font = "%s %s" % (self.font.familyname, self.font.weight)
        for x in self.metadata.get('fonts', None):
            if x.get('fullName', None) == current_font:
                font = x
                break
        self.assertTrue(font)
        if int(self.font.italicangle) == 0:
            self.assertEqual(font.get('style', None), 'normal')
        else:
            self.assertEqual(font.get('style', None), 'italic')

    def test_metadata_have_subset(self):
        """ METADATA.json shoyld have 'subsets' property """
        self.assertTrue(self.metadata.get('subsets', None))

    # VV TODO: Subset list must be selected from pyFontaine
    subset_list = ['menu', 'latin', 'latin_ext', 'vietnamese', 'greek',
                   'cyrillic', 'cyrillic_ext', 'arabic']

    def test_metadata_subsets_names_are_correct(self):
        """ METADATA.json 'subset' property can have only allowed values
            from list: ['menu', 'latin','latin_ext', 'vietnamese', 'greek',
            'cyrillic', 'cyrillic_ext', 'arabic'] """
        self.assertTrue(all([x in self.subset_list
                             for x in self.metadata.get('subsets', None)]))

    def test_font_subsets_exists(self):
        """ Each font file should have its own set of subsets
            defined in METADATA.json """
        for i in self.metadata.get('subsets', []):
            name = "%s.%s" % (self.fname, i)
            self.assertTrue(os.path.exists(name), msg="'%s' not found" % name)
            self.assertEqual(magic.from_file(name, mime=True),
                             'application/x-font-ttf')

    def test_subsets_exists_opentype(self):
        """ Each font file should have its own set of opentype file format
        subsets defined in METADATA.json """
        for x in self.metadata.get('fonts', None):
            for i in self.metadata.get('subsets', None):
                name = "%s.%s-opentype" % (self.fname, i)
                self.assertTrue(os.path.exists(name))
                self.assertEqual(magic.from_file(name, mime=True),
                                 'application/x-font-ttf')

    def test_menu_have_chars_for_family_key(self):
        """ Test does .menu file have chars needed for METADATA family key """
        family = ''
        for x in self.metadata.get('fonts', []):
            if os.path.basename(self.path) == x['filename']:
                family = x['name']
                break
        self.assertTrue(family)

        self.assertTrue("%s.menu" % self.fname)
        font = fontforge.open("%s.menu" % self.fname)
        self.assertTrue(all([i in font for i in set(map(ord, family))]))

    def test_subset_file_smaller_font_file(self):
        """ Subset files should be smaller than font file """
        for x in self.metadata.get('subsets', None):
            name = "%s.%s" % (self.fname, x)
            self.assertLess(os.path.getsize(name), os.path.getsize(self.path))

    def test_metadata_value_match_font_weight(self):
        """Check that METADATA font.weight keys match font internal metadata"""
        fonts = {}
        for x in self.metadata.get('fonts', None):
            fonts[x.get('fullName', '')] = x
        self.assertEqual(weights.get(self.font.weight, 0),
                         fonts.get(self.font.fullname, {'weight': ''}).get('weight', 0))

    def test_metadata_font_style_same_all_fields(self):
        """ METADATA.json fonts properties "name" "postScriptName" "fullName"
        "filename" should have the same style """
        weights_table = {
            'Thin': 'Thin',
            'ThinItalic': 'Thin Italic',
            'ExtraLight': 'Extra Light',
            'ExtraLightItalic': 'Extra Light Italic',
            'Light': 'Light',
            'LightItalic': 'Light Italic',
            'Regular': 'Regular',
            'Italic': 'Italic',
            'Medium': 'Medium',
            'MediumItalic': 'Medium Italic',
            'SemiBold': 'Semi Bold',
            'SemiBoldItalic': 'Semi Bold Italic',
            'Bold': 'Bold',
            'BoldItalic': 'Bold Italic',
            'ExtraBold': 'Extra Bold',
            'ExtraBoldItalic': 'Extra Bold Italic',
            'Black': 'Black',
            'BlackItalic': 'Black Italic',
        }

        for x in self.metadata.get('fonts', None):
            if x.get('postScriptName', '') != self.font.familyname:
                # this is not regular style
                _style = x["postScriptName"].split('-').pop(-1)
                self.assertIn(_style, weights_table.keys(),
                              msg="Style name not from expected list")
                self.assertEqual("%s %s" % (self.font.familyname,
                                            weights_table.get(_style)),
                                 x.get("fullName", ''))
            else:
                _style = 'Regular'

            self.assertEqual("%s-%s.ttf" % (self.font.familyname,
                                            _style), x.get("filename", ''))

    def test_metadata_font_style_italic_correct(self):
        """ METADATA.json fonts properties "name" "postScriptName" "fullName"
        "filename" should have the same style """
        for x in self.metadata.get('fonts', None):
            if x.get('postScriptName', '') != self.font.familyname:
                # this is not regular style
                _style = x["postScriptName"].split('-').pop(-1)
                if _style in italics_styles.keys():
                    self.assertEqual(x.get('style', ''), 'italic')
                else:
                    self.assertEqual(x.get('style', ''), 'normal')

    @tags('required')
    def test_metadata_keys(self):
        """ METADATA.json should have top keys: ["name", "designer",
            "license", "visibility", "category", "size", "dateAdded",
            "fonts", "subsets"] """

        top_keys = ["name", "designer", "license", "visibility", "category",
                    "size", "dateAdded", "fonts", "subsets"]

        for x in top_keys:
            self.assertIn(x, self.metadata, msg="Missing %s key" % x)

    @tags('required')
    def test_metadata_designer_exists_in_profiles_csv(self):
        """ Designer exists in GWF profiles.csv """
        designer = self.metadata.get('designer', '')
        self.assertTrue(designer)
        import urllib
        import csv
        fp = urllib.urlopen('https://googlefontdirectory.googlecode.com/hg/designers/profiles.csv')
        try:
            designers = []
            for row in csv.reader(fp):
                if not row:
                    continue
                designers.append(row[0])
            self.assertTrue(designer in designers,
                            msg='Designer %s is not in profiles.csv' % designer)
        except Exception:
            self.assertTrue(False)

    @tags('required')
    def test_metadata_fonts_key_list(self):
        """ METADATA.json font key should be list """
        self.assertEqual(type(self.metadata.get('fonts', '')), type([]))

    @tags('required')
    def test_metadata_subsets_key_list(self):
        """ METADATA.json subsets key should be list """
        self.assertEqual(type(self.metadata.get('subsets', '')), type([]))

    @tags('required')
    def test_subsets_files_is_font(self):
        """ Subset file is a TrueType format """
        for subset in self.metadata.get('subsets', []):
            self.assertTrue(magic.from_file(self.fname + '.' + subset),
                            'TrueType font data')

    @tags('required')
    def test_metadata_fonts_items_dicts(self):
        """ METADATA.json fonts key items are dicts """
        for x in self.metadata.get('fonts', None):
            self.assertEqual(type(x), type({}), msg="type(%s) is not dict" % x)

    @tags('required')
    def test_metadata_subsets_items_string(self):
        """ METADATA.json subsets key items are strings """
        for x in self.metadata.get('subsets', None):
            self.assertEqual(type(x), type(""), msg="type(%s) is not dict" % x)

    @tags('required')
    def test_metadata_top_keys_types(self):
        """ METADATA.json should have proper top keys types """
        self.assertEqual(type(self.metadata.get("name", None)),
                         type(""), msg="name key type invalid")
        self.assertEqual(type(self.metadata.get("designer", None)),
                         type(""), msg="designer key type invalid")
        self.assertEqual(type(self.metadata.get("license", None)),
                         type(""), msg="license key type invalid")
        self.assertEqual(type(self.metadata.get("visibility", None)),
                         type(""), msg="visibility key type invalid")
        self.assertEqual(type(self.metadata.get("category", None)),
                         type(""), msg="category key type invalid")
        self.assertEqual(type(self.metadata.get("size", None)),
                         type(0), msg="size key type invalid")
        self.assertEqual(type(self.metadata.get("dateAdded", None)),
                         type(""), msg="dateAdded key type invalid")

    @tags('required')
    def test_metadata_no_unknown_top_keys(self):
        """ METADATA.json don't have unknown top keys """
        top_keys = ["name", "designer", "license", "visibility", "category",
                    "size", "dateAdded", "fonts", "subsets"]
        for x in self.metadata.keys():
            self.assertIn(x, top_keys, msg="%s found unknown top key" % x)

    @tags('required')
    def test_metadata_atleast_latin_menu_subsets_exist(self):
        """ METADATA.json subsets should have at least 'menu' and 'latin' """
        self.assertIn('menu', self.metadata.get('subsets', []),
                      msg="Subsets missing menu")
        self.assertIn('latin', self.metadata.get('subsets', []),
                      msg="Subsets missing latin")

    @tags('required')
    def test_metadata_copyrights_are_equal_for_all_fonts(self):
        """ METADATA.json fonts copyright string is the same for all items """

        copyright = None

        for x in self.metadata.get('fonts', None):
            copyright = x.get('copyright', None)
            break

        if copyright:
            for x in self.metadata.get('fonts', None):
                self.assertEqual(x.get('copyright', ''), copyright)

    @tags('required')
    def test_metadata_license(self):
        """ METADATA.json license is 'Apache2', 'UFL' or 'OFL' """
        licenses = ['Apache2', 'OFL', 'UFL']
        self.assertIn(self.metadata.get('license', ''), licenses,
                      msg='License has invalid value')

# TODO: Find where this check came from
    @tags('required')
    def test_metadata_copyright_size(self):
        """ Copyright string should be less than 500 chars """
        for x in self.metadata.get('fonts', None):
            self.assertLessEqual(len(x.get('copyright', '')), 500)

    @tags('required')
    def test_metadata_has_unique_style_weight_pairs(self):
        """ METADATA.json only contains unique style:weight pairs """
        pairs = []
        for fontdata in self.metadata.get('fonts', []):
            styleweight = '%s:%s' % (fontdata['style'],
                                     fontdata.get('weight', 0))
            self.assertNotIn(styleweight, pairs)
            pairs.append(styleweight)
