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
import unittest
import mock
import simplejson
import StringIO

from checker.tests import downstream
from checker.tests.downstream.test_check_subsets_exists import File
from cli.ttfont import Font as OriginFont


class TestCase(unittest.TestCase):

    def failure_run(self, test_klass):
        result = _run_font_test(test_klass)

        if result.errors:
            self.fail(result.errors[0][1])

        self.assertTrue(bool(result.failures))

    def success_run(self, test_klass):
        result = _run_font_test(test_klass)

        if result.errors:
            self.fail(result.errors[0][1])

        if result.failures:
            self.fail(result.failures[0][1])

        self.assertFalse(bool(result.failures))


def _get_tests(testcase_klass):
    return unittest.defaultTestLoader.loadTestsFromTestCase(testcase_klass)


def _run_font_test(testcase_klass):
    runner = unittest.TextTestRunner(stream=StringIO.StringIO())
    tests = _get_tests(testcase_klass)
    return runner.run(tests)


class Test_CheckCanonicalFilenamesTestCase(TestCase):

    @mock.patch.object(downstream.CheckCanonicalFilenames, 'read_metadata_contents')
    def test_one(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{
                'name': 'FamilyName',
                'filename': 'FamilyName-Regular.ttf'
            }]
        })
        self.success_run(downstream.CheckCanonicalFilenames)

        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{
                'name': 'Family',
                'filename': 'Family-Bold.ttf'
            }]
        })
        self.failure_run(downstream.CheckCanonicalFilenames)


class Test_CheckCanonicalStyles(TestCase):

    @mock.patch.object(downstream.CheckCanonicalStyles, 'read_metadata_contents')
    def test_two(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{
                'name': 'Family',
                'filename': 'Family-Regular.ttf'
            }]
        })

        class Font(object):
            macStyle = 0
            italicAngle = 0
            names = []

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            mocked_get_ttfont.return_value.macStyle = downstream.CheckCanonicalStyles.ITALIC_MASK

            self.failure_run(downstream.CheckCanonicalStyles)

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            mocked_get_ttfont.return_value.macStyle = 0
            self.success_run(downstream.CheckCanonicalStyles)

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            mocked_get_ttfont.return_value.italicAngle = 10
            self.failure_run(downstream.CheckCanonicalStyles)

        class name:
            string = ''

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            n = name()
            n.string = 'italic'
            mocked_get_ttfont.return_value.names.append(n)
            self.failure_run(downstream.CheckCanonicalStyles)


class Test_CheckCanonicalWeights(TestCase):

    @mock.patch.object(downstream.CheckCanonicalWeights, 'read_metadata_contents')
    def test_three(self, metadata_contents):

        class Font(object):
            OS2_usWeightClass = 400

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            # test if font weight less than 100 is invalid value
            metadata_contents.return_value = simplejson.dumps({
                'fonts': [{
                    'weight': 50
                }]
            })
            mocked_get_ttfont.return_value = Font()
            self.failure_run(downstream.CheckCanonicalWeights)

            # test if font weight larger than 900 is invalid value
            metadata_contents.return_value = simplejson.dumps({
                'fonts': [{
                    'weight': 901
                }]
            })
            mocked_get_ttfont.return_value = Font()
            self.failure_run(downstream.CheckCanonicalWeights)

            # test if range 100..900 is valid values and checked for fonts
            for n in range(1, 10):
                metadata_contents.return_value = simplejson.dumps({
                    'fonts': [{
                        'weight': n * 100
                    }]
                })
                mocked_get_ttfont.return_value.OS2_usWeightClass = n * 100
                self.success_run(downstream.CheckCanonicalWeights)


class Test_CheckFamilyNameMatchesFontName(TestCase):

    @mock.patch.object(downstream.CheckFamilyNameMatchesFontNames, 'read_metadata_contents')
    def test_four(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'name': 'Family',
            'fonts': [{
                'name': 'Family'
            }]
        })
        self.success_run(downstream.CheckFamilyNameMatchesFontNames)

        metadata_contents.return_value = simplejson.dumps({
            'name': 'Family',
            'fonts': [{
                'name': 'FontName'
            }]
        })
        self.failure_run(downstream.CheckFamilyNameMatchesFontNames)


class Test_CheckMenuSubsetContainsProperGlyphs(TestCase):

    @mock.patch.object(downstream.CheckMenuSubsetContainsProperGlyphs, 'read_metadata_contents')
    def test_five(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'name': 'Font Family',
            'fonts': [{
                'name': 'FontName',
                'filename': 'FontName-Regular.ttf'
            }]
        })

        class FontS:

            def retrieve_cmap_format_4(self):
                return type('cmap', (object, ),
                            {'cmap': dict(map(lambda x: (ord(x), x), 'Font Name'))})

        class FontF:

            def retrieve_cmap_format_4(self):
                return type('cmap', (object, ),
                            {'cmap': dict(map(lambda x: (ord(x), x), 'FontName'))})

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = FontS()
            self.success_run(downstream.CheckMenuSubsetContainsProperGlyphs)

            mocked_get_ttfont.return_value = FontF()
            self.failure_run(downstream.CheckMenuSubsetContainsProperGlyphs)


class Test_CheckMetadataMatchesNameTable(TestCase):

    @mock.patch.object(downstream.CheckMetadataMatchesNameTable, 'read_metadata_contents')
    def test_six(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'name': 'Family',
            'fonts': [{
                'name': 'Family',
                'filename': 'FontFamily-Regular.ttf',
                'fullName': 'Family Font'
            }]
        })

        class Font:
            familyname = 'Family'
            fullname = 'Family Font'

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            self.success_run(downstream.CheckMetadataMatchesNameTable)

            mocked_get_ttfont.return_value.familyname = 'Arial Font Family'
            self.failure_run(downstream.CheckMetadataMatchesNameTable)


class Test_CheckNbspWidthMatchesSpWidth(TestCase):

    @mock.patch.object(downstream.CheckNbspWidthMatchesSpWidth, 'read_metadata_contents')
    def test_seven(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{
                'name': 'Font Name'
            }]
        })

        class Font:

            def advance_width(self, glyphId):
                return 1680

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            self.success_run(downstream.CheckNbspWidthMatchesSpWidth)


class Test_CheckSubsetsExist(TestCase):

    @mock.patch.object(downstream.CheckSubsetsExist, 'read_metadata_contents')
    def test_eight(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{
                'filename': 'FontName-Regular.ttf'
            }],
            'subsets': ['cyrillic']
        })

        with mock.patch.object(File, 'exists') as exists:
            with mock.patch.object(File, 'size') as size:
                size.return_value = 11
                with mock.patch.object(File, 'mime') as mime:
                    mime.return_value = 'application/x-font-ttf'
                    self.success_run(downstream.CheckSubsetsExist)

                    exists.assert_called_with('FontName-Regular.cyrillic')
                    self.assertEqual(size.call_args_list,
                                     [mock.call('FontName-Regular.cyrillic'),
                                      mock.call('FontName-Regular.ttf')])


class Test_CheckUnusedGlyphData(TestCase):

    def test_nine(self):

        class Font:

            def get_glyf_length(self):
                return 1234

            def get_loca_glyph_offset(self, num):
                return 1200

            def get_loca_glyph_length(self, num):
                return 34

            def get_loca_num_glyphs(self):
                return 123

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            self.success_run(downstream.CheckUnusedGlyphData)


class Test_CheckOS2WidthClass(TestCase):

    def test_ten(self):

        class Font:
            OS2_usWidthClass = 4

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            self.success_run(downstream.CheckOS2WidthClass)

            for i in [0, 10]:
                mocked_get_ttfont.return_value.OS2_usWidthClass = i
                self.failure_run(downstream.CheckOS2WidthClass)


class Test_CheckNoProblematicFormats(TestCase):

    def test_eleven(self):

        class FontTool:

            @staticmethod
            def get_tables():
                return ['glyf', 'post', 'GPOS']

        import cli.ttfont
        with mock.patch.object(cli.ttfont.FontTool, 'get_tables') as get_tables:
            get_tables.return_value = FontTool.get_tables()
            self.failure_run(downstream.CheckNoProblematicFormats)


class Test_CheckHmtxHheaMaxAdvanceWidthAgreement(TestCase):

    def test_twelve(self):

        class Font:

            def get_hmtx_max_advanced_width(self):
                return 250

            @property
            def advance_width_max(self):
                return 250

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            self.success_run(downstream.CheckHmtxHheaMaxAdvanceWidthAgreement)

            mocked_get_ttfont.return_value.advance_width_max = 240
            self.failure_run(downstream.CheckHmtxHheaMaxAdvanceWidthAgreement)


class Test_CheckGlyfTableLength(TestCase):

    def test_thirteen(self):

        class Font:

            def get_loca_length(self):
                return 5541  # considering padding in 3 bytes

            def get_glyf_length(self):
                return 5544

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            self.success_run(downstream.CheckGlyfTableLength)

    def test_fourteen(self):
        class Font:

            def get_loca_length(self):
                return 5550  # considering "loca" length greater than "glyf"

            def get_glyf_length(self):
                return 5544

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            self.failure_run(downstream.CheckGlyfTableLength)

    def test_fifteen(self):
        class Font:

            def get_loca_length(self):
                # considering "loca" less than glyf on more
                # than 3 bytes (allowed padding)
                return 5540

            def get_glyf_length(self):
                return 5544

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            self.failure_run(downstream.CheckGlyfTableLength)


class Test_CheckFullFontNameBeginsWithFamilyName(TestCase):

    def test_sixteen(self):
        class Font:
            bin2unistring = OriginFont.bin2unistring

            @property
            def names(self):
                return [
                    type('name', (object,),
                         {'nameID': 1, 'string': 'FamilyName', 'platEncID': 1,
                          'langID': 1, 'platformID': 1}),
                    type('name', (object,),
                         {'nameID': 4, 'string': 'FamilyNameRegular',
                          'platEncID': 1, 'langID': 1, 'platformID': 1})
                ]

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            self.success_run(downstream.CheckFullFontNameBeginsWithFamilyName)

    def test_seventeen(self):
        class Font:
            bin2unistring = OriginFont.bin2unistring

            @property
            def names(self):
                return [
                    type('name', (object,),
                         {'nameID': 1, 'string': 'FamilyName', 'platEncID': 1,
                          'langID': 1, 'platformID': 1}),
                    type('name', (object,),
                         {'nameID': 4, 'string': 'FamilyRegular',
                          'platEncID': 1, 'langID': 1, 'platformID': 1})
                ]

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            self.failure_run(downstream.CheckFullFontNameBeginsWithFamilyName)


class Test_CheckUPMHeightsLess120(TestCase):

    def test_eighteen(self):

        class FakeAscents:

            maxv = 910

            def get_max(self):
                return self.maxv

        class FakeDescents:

            minv = -210

            def get_min(self):
                return self.minv

        class Font:

            upm_height = 1024

            def get_upm_heights(self):
                return self.upm_height

            ascents = FakeAscents()
            descents = FakeDescents()

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            self.success_run(downstream.TestCheckUPMHeightsLess120)

            mocked_get_ttfont.return_value.ascents.maxv = 1400
            self.failure_run(downstream.TestCheckUPMHeightsLess120)


class Test_CheckFontNameInCamelCase(TestCase):

    @mock.patch.object(downstream.CheckFontNameNotInCamelCase, 'read_metadata_contents')
    def test_nineteen(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'name': 'Font Family',
            'fonts': [{
                'name': 'Font Family',
                'filename': 'FontFamily-Regular.ttf'
            }]
        })
        self.success_run(downstream.CheckFontNameNotInCamelCase)

        metadata_contents.return_value = simplejson.dumps({
            'name': 'Font Family',
            'fonts': [{
                'name': 'FontFamily',
                'filename': 'FontFamily-Regular.ttf'
            }]
        })

        self.failure_run(downstream.CheckFontNameNotInCamelCase)


class Test_CheckMagicPREPByteCode(TestCase):

    def test_twenty(self):

        class Font:
            bytecode = '\xb8\x01\xff\x85\xb0\x04\x8d'

            def get_program_bytecode(self):
                return self.bytecode

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            self.success_run(downstream.CheckMagicPREPByteCode)

            mocked_get_ttfont.return_value.bytecode = '\x00'
            self.failure_run(downstream.CheckMagicPREPByteCode)


class Test_CheckFontNamesSameAcrossPlatforms(TestCase):

    def test_twenty_one(self):

        class Font:
            bin2unistring = OriginFont.bin2unistring

            @property
            def names(self):
                return [
                    type('name', (object,),
                         {'nameID': 1, 'string': 'FamilyName',
                          'langID': 0x409, 'platformID': 3}),
                    type('name', (object,),
                         {'nameID': 1, 'string': 'FamilyNameRegular',
                          'langID': 0, 'platformID': 1})
                ]

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            self.failure_run(downstream.CheckNamesSameAcrossPlatforms)

            mocked_get_ttfont.return_value.names = [
                type('name', (object,),
                     {'nameID': 1, 'string': 'FamilyNameRegular',
                      'langID': 0x409, 'platformID': 3}),
                type('name', (object,),
                     {'nameID': 1, 'string': 'FamilyNameRegular',
                      'langID': 0, 'platformID': 1})
            ]

            self.success_run(downstream.CheckNamesSameAcrossPlatforms)


class Test_CheckPostScriptNameMatchesWeight(TestCase):

    @mock.patch.object(downstream.CheckPostScriptNameMatchesWeight, 'read_metadata_contents')
    def test_twenty_three(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{'weight': 400, 'postScriptName': 'Family-Regular'},
                      {'weight': 400, 'postScriptName': 'Family-Italic'},
                      {'weight': 100, 'postScriptName': 'Family-Thin'},
                      {'weight': 100, 'postScriptName': 'Family-ThinItalic'},
                      {'weight': 200, 'postScriptName': 'Family-ExtraLight'},
                      {'weight': 200, 'postScriptName': 'Family-ExtraLightItalic'},
                      {'weight': 300, 'postScriptName': 'Family-Light'},
                      {'weight': 300, 'postScriptName': 'Family-LightItalic'},
                      {'weight': 500, 'postScriptName': 'Family-Medium'},
                      {'weight': 500, 'postScriptName': 'Family-MediumItalic'},
                      {'weight': 600, 'postScriptName': 'Family-SemiBold'},
                      {'weight': 600, 'postScriptName': 'Family-SemiBoldItalic'},
                      {'weight': 700, 'postScriptName': 'Family-Bold'},
                      {'weight': 700, 'postScriptName': 'Family-BoldItalic'},
                      {'weight': 800, 'postScriptName': 'Family-ExtraBold'},
                      {'weight': 800, 'postScriptName': 'Family-ExtraBoldItalic'},
                      {'weight': 900, 'postScriptName': 'Family-Black'},
                      {'weight': 900, 'postScriptName': 'Family-BlackItalic'}]
        })
        self.success_run(downstream.CheckPostScriptNameMatchesWeight)

        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{'weight': 500, 'postScriptName': 'Family-Regular'}]
        })

        self.failure_run(downstream.CheckPostScriptNameMatchesWeight)


class Test_CheckMetadataContainsReservedFontName(TestCase):

    @mock.patch.object(downstream.CheckMetadataContainsReservedFontName, 'read_metadata_contents')
    def test_twenty_four(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{'copyright': 'Copyright (c) 2014 (mail@example.com) with Reserved Font Name'}]
        })
        self.success_run(downstream.CheckMetadataContainsReservedFontName)

        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{'copyright': 'Copyright (c) 2014 (mail@example.com)'}]
        })

        self.failure_run(downstream.CheckMetadataContainsReservedFontName)

        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{'copyright': 'Copyright (c) 2014 with Reserved Font Name'}]
        })

        self.failure_run(downstream.CheckMetadataContainsReservedFontName)


class Test_CheckLicenseIncluded(TestCase):

    def test_twenty_five(self):

        class Font:
            bin2unistring = OriginFont.bin2unistring

            license_url = ''

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            self.failure_run(downstream.CheckLicenseIncluded)

            mocked_get_ttfont.return_value.license_url = 'http://example.com/'
            self.success_run(downstream.CheckLicenseIncluded)


class Test_CheckFontWeightSameAsInMetadata(TestCase):

    @mock.patch.object(downstream.CheckFontWeightSameAsInMetadata, 'read_metadata_contents')
    def test_twenty_six(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{'filename': 'Family-Regular.ttf', 'weight': 400}]
        })

        class Font:
            OS2_usWeightClass = 400

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as get_ttfont:
            get_ttfont.return_value = Font()

            self.success_run(downstream.CheckFontWeightSameAsInMetadata)

            get_ttfont.return_value.OS2_usWeightClass = 300
            self.failure_run(downstream.CheckFontWeightSameAsInMetadata)


class Test_CheckFontNameEqualToMacStyleFlags(TestCase):

    def test_twenty_seven(self):

        class Font:

            macStyle = 0b00101011
            fullname = 'Family-Regular'

        with mock.patch.object(OriginFont, 'get_ttfont') as get_ttfont:
            get_ttfont.return_value = Font()

            self.failure_run(downstream.CheckFontNameEqualToMacStyleFlags)

            get_ttfont.return_value.fullname = 'Family-BoldItalic'
            self.success_run(downstream.CheckFontNameEqualToMacStyleFlags)

            get_ttfont.return_value.fullname = 'Family-Regular'
            get_ttfont.return_value.macStyle = 0b00
            self.success_run(downstream.CheckFontNameEqualToMacStyleFlags)


class Test_CheckItalicStyleMatchesMacStyle(TestCase):

    @mock.patch.object(downstream.CheckItalicStyleMatchesMacStyle, 'read_metadata_contents')
    def test_twenty_six(self, metadata_contents):

        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{'filename': 'Family-Regular.ttf',
                       'style': 'italic'}]
        })

        class Font:
            macStyle = 0b10
            fullname = 'Family-Italic'
            familyname = 'Family-Italic'

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as get_ttfont:
            get_ttfont.return_value = Font()
            self.success_run(downstream.CheckItalicStyleMatchesMacStyle)

            get_ttfont.return_value.fullname = 'Family-Regular'
            self.failure_run(downstream.CheckItalicStyleMatchesMacStyle)

            get_ttfont.return_value.familyname = 'Family-Regular'
            self.failure_run(downstream.CheckItalicStyleMatchesMacStyle)

            get_ttfont.return_value.macStyle = 0
            self.failure_run(downstream.CheckItalicStyleMatchesMacStyle)


class Test_CheckNormalStyleMatchesMacStyle(TestCase):

    @mock.patch.object(downstream.CheckNormalStyleMatchesMacStyle, 'read_metadata_contents')
    def test_twenty_six(self, metadata_contents):

        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{'filename': 'Family-Regular.ttf',
                       'style': 'normal'}]
        })

        class Font:
            macStyle = 0
            fullname = 'Family-Bold'
            familyname = 'Family-Bold'

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as get_ttfont:
            get_ttfont.return_value = Font()

            self.success_run(downstream.CheckNormalStyleMatchesMacStyle)

            get_ttfont.return_value.fullname = 'Family-Italic'
            self.failure_run(downstream.CheckNormalStyleMatchesMacStyle)

            get_ttfont.return_value.familyname = 'Family-BoldItalic'
            self.failure_run(downstream.CheckNormalStyleMatchesMacStyle)

            get_ttfont.return_value.macStyle = 0b10
            self.failure_run(downstream.CheckNormalStyleMatchesMacStyle)


class Test_CheckNamesAreASCIIOnly(TestCase):

    def test_twenty_seven(self):
        class Font:
            pass

        with mock.patch.object(OriginFont, 'get_ttfont') as get_ttfont:
            get_ttfont.return_value = Font()
            get_ttfont.return_value.names = [
                type('name', (object,),
                     {'nameID': 1, 'string': 'FamilyNameRegular',
                      'langID': 0x409, 'platformID': 3}),
            ]
            self.success_run(downstream.CheckNamesAreASCIIOnly)

            get_ttfont.return_value.names = [
                type('name', (object,),
                     {'nameID': 1, 'string': u'FamilyNameRegularЙ',
                      'langID': 0x409, 'platformID': 3}),
            ]


class Test_CheckMetadataFields(TestCase):

    @mock.patch.object(downstream.CheckMetadataFields, 'read_metadata_contents')
    def test_twenty_eight(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{'name': 'Family',
                       'filename': 'Family-Regular.ttf',
                       'weight': 400,
                       'fullName': 'Family Regular',
                       'postScriptName': 'Family-Regular',
                       'style': 'normal',
                       'copyright': ''}]
        })
        self.success_run(downstream.CheckMetadataFields)

        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{'name': 'Family',
                       'filename': 'Family-Regular.ttf',
                       # 'weight': 400,
                       # 'fullName': 'Family Regular',
                       # 'postScriptName': 'Family-Regular',
                       # 'style': 'normal',
                       'copyright': ''}]
        })
        self.failure_run(downstream.CheckMetadataFields)

        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{'name': 'Family',
                       'filename': 'Family-Regular.ttf',
                       'weight': 400,
                       'fullName': 'Family Regular',
                       'postScriptName': 'Family-Regular',
                       'style': 'normal',
                       'copyright': '',
                       'tables': []}]
        })
        self.failure_run(downstream.CheckMetadataFields)


class Test_CheckFontHasDsigTable(TestCase):

    def test_twenty_nine(self):

        with mock.patch.object(OriginFont, 'get_ttfont') as get_ttfont:
            get_ttfont.return_value = {'DSIG': True}
            self.success_run(downstream.CheckFontHasDsigTable)

            get_ttfont.return_value = {}
            self.failure_run(downstream.CheckFontHasDsigTable)


class Test_CheckFontHasNotKernTable(TestCase):

    def test_twenty_nine(self):

        with mock.patch.object(OriginFont, 'get_ttfont') as get_ttfont:
            get_ttfont.return_value = {'KERN': True}
            self.failure_run(downstream.CheckFontHasNotKernTable)

            get_ttfont.return_value = {}
            self.success_run(downstream.CheckFontHasNotKernTable)


class Test_CheckGposTableHasKerningInfo(TestCase):

    def test_thirty(self):

        PairSet = type('PairSet', (object, ),
                       {'PairSetCount': 1})

        PairAdjustement = type('PairAdjustement', (object, ),
                               {'LookupType': 2,
                                'SubTableCount': 1,
                                'SubTable': [PairSet]})

        Lookup = type('Lookup', (object, ), {'Lookup': [PairAdjustement]})

        gpos = type('gpos', (object, ),
                    {'table': type('table', (object, ),
                                   {'LookupList': Lookup})})

        Font = {'GPOS': gpos}

        with mock.patch.object(OriginFont, 'get_ttfont') as get_ttfont:
            get_ttfont.return_value = Font
            self.success_run(downstream.CheckGposTableHasKerningInfo)

            get_ttfont.return_value = {}
            self.failure_run(downstream.CheckGposTableHasKerningInfo)


class Test_CheckGaspTableType(TestCase):

    def test_thirty_one(self):

        with mock.patch.object(OriginFont, 'get_ttfont') as get_ttfont:

            gasp = type('GASP', (object, ), {'gaspRange': {65535: 15}})
            get_ttfont.return_value = {'gasp': gasp}
            self.success_run(downstream.CheckGaspTableType)

            gasp = type('GASP', (object, ), {'gaspRange': []})
            get_ttfont.return_value = {'gasp': gasp}
            self.failure_run(downstream.CheckGaspTableType)

            gasp = type('GASP', (object, ), {'gaspRange': {65535: 14}})
            get_ttfont.return_value = {'gasp': gasp}
            self.failure_run(downstream.CheckGaspTableType)

            get_ttfont.return_value = {}
            self.failure_run(downstream.CheckGaspTableType)


class Test_CheckMonospaceAgreement(TestCase):

    @mock.patch.object(downstream.CheckMonospaceAgreement, 'read_metadata_contents')
    def test_thirty_two(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'category': 'Monospace',
            'fonts': [{'name': 'Family',
                       'filename': 'Family-Regular.ttf'}]
        })

        class Font:

            _glyph_advance_width = 2134
            _advance_width = 2134

            def glyphs(self):
                return ['a', 'b']

            def advance_width(self, glyphid=None):
                if not glyphid:
                    return self._advance_width
                return self._glyph_advance_width

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as get_ttfont:
            get_ttfont.return_value = Font()
            self.success_run(downstream.CheckMonospaceAgreement)

            get_ttfont.return_value._glyph_advance_width = 1111
            self.failure_run(downstream.CheckMonospaceAgreement)


class Test_CheckItalicAngleAgreement(TestCase):

    def test_thirty_three(self):

        class Font:
            italicAngle = 0

        with mock.patch.object(OriginFont, 'get_ttfont') as get_ttfont:
            get_ttfont.return_value = Font()

            self.success_run(downstream.CheckItalicAngleAgreement)

            get_ttfont.return_value.italicAngle = 10
            self.failure_run(downstream.CheckItalicAngleAgreement)

            get_ttfont.return_value.italicAngle = -30
            self.failure_run(downstream.CheckItalicAngleAgreement)


class Test_CheckGlyphExistence(TestCase):

    def test_thirty_four(self):

        class Font:

            _cmap = {
                160: 'nonbreakingspace',
                32: 'space',
                8364: 'Euro'
            }

            def retrieve_cmap_format_4(self):
                return type('cmap', (object, ), {'cmap': self._cmap})

        with mock.patch.object(OriginFont, 'get_ttfont') as get_ttfont:
            get_ttfont.return_value = Font()

            self.success_run(downstream.CheckGlyphExistence)

            get_ttfont.return_value._cmap = {
                160: 'nonbreakingspace',
                32: 'space'
            }
            self.failure_run(downstream.CheckGlyphExistence)

            get_ttfont.return_value._cmap = {
                160: 'nonbreakingspace',
                8364: 'Euro'
            }
            self.failure_run(downstream.CheckGlyphExistence)

            get_ttfont.return_value._cmap = {
                32: 'space',
                8364: 'Euro'
            }
            self.failure_run(downstream.CheckGlyphExistence)
