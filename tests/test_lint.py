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
import json

from bakery_cli.ttfont import Font as OriginFont
from bakery_lint.base import TestCaseOperator
from bakery_lint.tests import downstream, upstream
from bakery_lint.tests.downstream.test_check_subsets_exists import File


class TestCase(unittest.TestCase):

    def failure_run(self, test_klass, test_method=None):
        result = _run_font_test(test_klass, test_method)

        if result.errors:
            self.fail(result.errors[0][1])

        self.assertTrue(bool(result.failures))

    def success_run(self, test_klass, test_method=None):
        result = _run_font_test(test_klass, test_method)

        if result.errors:
            self.fail(result.errors[0][1])

        if result.failures:
            self.fail(result.failures[0][1])

        self.assertFalse(bool(result.failures))


def _run_font_test(testcase_klass, test_method):
    from bakery_lint.base import BakeryTestRunner, BakeryTestResult
    runner = BakeryTestRunner(resultclass=BakeryTestResult)
    tests = unittest.defaultTestLoader.loadTestsFromTestCase(testcase_klass)

    suite = unittest.TestSuite()
    for i, test in enumerate(tests):
        if test_method and test._testMethodName != test_method:
            continue
        suite.addTest(test)
    return runner.run(suite)


class Test_CheckCanonicalFilenamesTestCase(TestCase):

    @mock.patch.object(downstream.CheckCanonicalFilenames, 'read_metadata_contents')
    def test_one(self, metadata_contents):
        targetTestCase = downstream.CheckCanonicalFilenames
        targetTestCase.operator = TestCaseOperator('')
        metadata_contents.return_value = json.dumps({
            'fonts': [{
                'name': 'FamilyName',
                'filename': 'FamilyName-Regular.ttf'
            }]
        })
        self.success_run(targetTestCase)

        metadata_contents.return_value = json.dumps({
            'fonts': [{
                'name': 'Family',
                'filename': 'Family-Bold.ttf'
            }]
        })
        self.failure_run(targetTestCase)


class Test_CheckCanonicalStyles(TestCase):

    @mock.patch.object(downstream.CheckCanonicalStyles, 'read_metadata_contents')
    def test_two(self, metadata_contents):
        from bakery_lint.base import TestCaseOperator
        metadata_contents.return_value = json.dumps({
            'fonts': [{
                'name': 'Family',
                'filename': 'Family-Regular.ttf'
            }]
        })

        class Font(object):
            macStyle = 0
            italicAngle = 0
            names = []

        targetTestCase = downstream.CheckCanonicalStyles
        targetTestCase.operator = TestCaseOperator('')

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            mocked_get_ttfont.return_value.macStyle = downstream.CheckCanonicalStyles.ITALIC_MASK

            self.failure_run(targetTestCase)

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            mocked_get_ttfont.return_value.macStyle = 0
            self.success_run(targetTestCase)

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            mocked_get_ttfont.return_value.italicAngle = 10
            self.failure_run(targetTestCase)

        class name(object):
            string = ''

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            n = name()
            n.string = 'italic'
            mocked_get_ttfont.return_value.names.append(n)
            self.failure_run(targetTestCase)


class Test_CheckCanonicalWeights(TestCase):

    @mock.patch.object(downstream.CheckCanonicalWeights, 'read_metadata_contents')
    def test_three(self, metadata_contents):

        targetTestCase = downstream.CheckCanonicalWeights
        targetTestCase.operator = TestCaseOperator('')

        class Font(object):
            OS2_usWeightClass = 400

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            # test if font weight less than 100 is invalid value
            metadata_contents.return_value = json.dumps({
                'fonts': [{
                    'weight': 50
                }]
            })
            mocked_get_ttfont.return_value = Font()
            self.failure_run(targetTestCase)

            # test if font weight larger than 900 is invalid value
            metadata_contents.return_value = json.dumps({
                'fonts': [{
                    'weight': 901
                }]
            })
            mocked_get_ttfont.return_value = Font()
            self.failure_run(targetTestCase)

            # test if range 100..900 is valid values and checked for fonts
            for n in range(1, 10):
                metadata_contents.return_value = json.dumps({
                    'fonts': [{
                        'weight': n * 100
                    }]
                })
                mocked_get_ttfont.return_value.OS2_usWeightClass = n * 100
                self.success_run(targetTestCase)


class Test_CheckFamilyNameMatchesFontName(TestCase):

    @mock.patch.object(downstream.CheckFamilyNameMatchesFontNames, 'read_metadata_contents')
    def test_four(self, metadata_contents):
        targetTestCase = downstream.CheckFamilyNameMatchesFontNames
        targetTestCase.operator = TestCaseOperator('')
        metadata_contents.return_value = json.dumps({
            'name': 'Family',
            'fonts': [{
                'name': 'Family'
            }]
        })
        self.success_run(targetTestCase)

        metadata_contents.return_value = json.dumps({
            'name': 'Family',
            'fonts': [{
                'name': 'FontName'
            }]
        })
        self.failure_run(targetTestCase)


class Test_CheckMenuSubsetContainsProperGlyphs(TestCase):

    @mock.patch.object(downstream.CheckMenuSubsetContainsProperGlyphs, 'read_metadata_contents')
    def test_five(self, metadata_contents):
        targetTestCase = downstream.CheckMenuSubsetContainsProperGlyphs
        targetTestCase.operator = TestCaseOperator('')

        metadata_contents.return_value = json.dumps({
            'name': 'Font Family',
            'fonts': [{
                'name': 'FontName',
                'filename': 'FontName-Regular.ttf'
            }]
        })

        class FontS(object):

            def retrieve_cmap_format_4(self):
                return type('cmap', (object, ),
                            {'cmap': dict([(ord(x), x) for x in 'Font Name'])})

        class FontF(object):

            def retrieve_cmap_format_4(self):
                return type('cmap', (object, ),
                            {'cmap': dict([(ord(x), x) for x in 'FontName'])})

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = FontS()
            self.success_run(targetTestCase)

            mocked_get_ttfont.return_value = FontF()
            self.failure_run(targetTestCase)


class Test_CheckMetadataMatchesNameTable(TestCase):

    @mock.patch.object(downstream.CheckMetadataMatchesNameTable, 'read_metadata_contents')
    def test_six(self, metadata_contents):
        targetTestCase = downstream.CheckMetadataMatchesNameTable
        targetTestCase.operator = TestCaseOperator('')
        metadata_contents.return_value = json.dumps({
            'name': 'Family',
            'fonts': [{
                'name': 'Family',
                'filename': 'FontFamily-Regular.ttf',
                'fullName': 'Family Font'
            }]
        })

        class Font(object):
            familyname = 'Family'
            fullname = 'Family Font'

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            self.success_run(targetTestCase)

            mocked_get_ttfont.return_value.familyname = 'Arial Font Family'
            self.failure_run(targetTestCase)


# class Test_CheckNbspWidthMatchesSpWidth(TestCase):

#     def test_seven(self):
#         targetTestCase = downstream.CheckNbspWidthMatchesSpWidth
#         targetTestCase.operator = TestCaseOperator('')

#         class Font(object):

#             ttfont

#             def advance_width(self, glyphId):
#                 return 1680

#         with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
#             mocked_get_ttfont.return_value = Font()
#             self.success_run(targetTestCase)


class Test_CheckSubsetsExist(TestCase):

    @mock.patch.object(downstream.CheckSubsetsExist, 'read_metadata_contents')
    def test_eight(self, metadata_contents):
        targetTestCase = downstream.CheckSubsetsExist
        targetTestCase.operator = TestCaseOperator('')
        metadata_contents.return_value = json.dumps({
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
                    self.success_run(targetTestCase)

                    exists.assert_called_with('FontName-Regular.cyrillic')
                    self.assertEqual(size.call_args_list,
                                     [mock.call('FontName-Regular.cyrillic'),
                                      mock.call('FontName-Regular.ttf')])


class Test_CheckOS2WidthClass(TestCase):

    def test_ten(self):

        targetTestCase = downstream.CheckOS2WidthClass
        targetTestCase.operator = TestCaseOperator('')

        class Font(object):
            OS2_usWidthClass = 4

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            self.success_run(targetTestCase)

            for i in [0, 10]:
                mocked_get_ttfont.return_value.OS2_usWidthClass = i
                self.failure_run(targetTestCase)


class Test_CheckNoProblematicFormats(TestCase):

    def test_eleven(self):

        targetTestCase = downstream.CheckNoProblematicFormats
        targetTestCase.operator = TestCaseOperator('')

        class FontTool(object):

            @staticmethod
            def get_tables():
                return ['glyf', 'post', 'GPOS']

        import bakery_cli.ttfont
        with mock.patch.object(bakery_cli.ttfont.FontTool, 'get_tables') as get_tables:
            get_tables.return_value = FontTool.get_tables()
            self.failure_run(targetTestCase)


class Test_CheckHmtxHheaMaxAdvanceWidthAgreement(TestCase):

    def test_twelve(self):

        targetTestCase = downstream.CheckHmtxHheaMaxAdvanceWidthAgreement
        targetTestCase.operator = TestCaseOperator('')

        class Font(object):

            def get_hmtx_max_advanced_width(self):
                return 250

            advance_width_max = 250

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            self.success_run(targetTestCase)

            mocked_get_ttfont.return_value.advance_width_max = 240
            self.failure_run(targetTestCase)


class Test_CheckGlyfTableLength(TestCase):

    def test_thirteen(self):
        targetTestCase = downstream.CheckGlyfTableLength
        targetTestCase.operator = TestCaseOperator('')

        class Font(object):

            def get_loca_length(self):
                return 5541  # considering padding in 3 bytes

            def get_glyf_length(self):
                return 5544

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            self.success_run(targetTestCase)

    def test_fourteen(self):
        targetTestCase = downstream.CheckGlyfTableLength
        targetTestCase.operator = TestCaseOperator('')

        class Font(object):

            def get_loca_length(self):
                return 5550  # considering "loca" length greater than "glyf"

            def get_glyf_length(self):
                return 5544

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            self.failure_run(targetTestCase)

    def test_fifteen(self):
        targetTestCase = downstream.CheckGlyfTableLength
        targetTestCase.operator = TestCaseOperator('')

        class Font(object):

            def get_loca_length(self):
                # considering "loca" less than glyf on more
                # than 3 bytes (allowed padding)
                return 5540

            def get_glyf_length(self):
                return 5544

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            self.failure_run(targetTestCase)


class Test_CheckFullFontNameBeginsWithFamilyName(TestCase):

    def test_sixteen(self):
        targetTestCase = downstream.CheckFullFontNameBeginsWithFamilyName
        targetTestCase.operator = TestCaseOperator('')

        class Font(object):
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
            self.success_run(targetTestCase)

    def test_seventeen(self):
        targetTestCase = downstream.CheckFullFontNameBeginsWithFamilyName
        targetTestCase.operator = TestCaseOperator('')

        class Font(object):
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
            self.failure_run(targetTestCase)


class Test_CheckUPMHeightsLess120(TestCase):

    def test_eighteen(self):
        targetTestCase = downstream.TestCheckUPMHeightsLess120
        targetTestCase.operator = TestCaseOperator('')

        class FakeAscents(object):

            maxv = 910

            def get_max(self):
                return self.maxv

        class FakeDescents(object):

            minv = -210

            def get_min(self):
                return self.minv

        class Font(object):

            upm_height = 1024

            def get_upm_height(self):
                return self.upm_height

            ascents = FakeAscents()
            descents = FakeDescents()

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            self.success_run(targetTestCase)

            mocked_get_ttfont.return_value.ascents.maxv = 1400
            self.failure_run(targetTestCase)


class Test_CheckFontNameInCamelCase(TestCase):

    @mock.patch.object(downstream.CheckFontNameNotInCamelCase,
                       'read_metadata_contents')
    def test_nineteen(self, metadata_contents):
        targetTestCase = downstream.CheckFontNameNotInCamelCase
        targetTestCase.operator = TestCaseOperator('')
        metadata_contents.return_value = json.dumps({
            'name': 'Font Family',
            'fonts': [{
                'name': 'Font Family',
                'filename': 'FontFamily-Regular.ttf'
            }]
        })
        self.success_run(targetTestCase)

        metadata_contents.return_value = json.dumps({
            'name': 'Font Family',
            'fonts': [{
                'name': 'FontFamily',
                'filename': 'FontFamily-Regular.ttf'
            }]
        })

        self.failure_run(targetTestCase)


class Test_CheckMagicPREPByteCode(TestCase):

    def test_twenty(self):
        targetTestCase = downstream.CheckMagicPREPByteCode
        targetTestCase.operator = TestCaseOperator('')

        class Font(object):
            bytecode = '\xb8\x01\xff\x85\xb0\x04\x8d'

            def get_program_bytecode(self):
                return self.bytecode

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            self.success_run(targetTestCase)

            mocked_get_ttfont.return_value.bytecode = '\x00'
            self.failure_run(targetTestCase)


class Test_CheckFontNamesSameAcrossPlatforms(TestCase):

    def test_twenty_one(self):

        targetTestCase = downstream.CheckNamesSameAcrossPlatforms
        targetTestCase.operator = TestCaseOperator('')

        class Font(object):
            bin2unistring = OriginFont.bin2unistring

            names = [
                type('name', (object,),
                     {'nameID': 1, 'string': 'FamilyName',
                      'langID': 0x409, 'platformID': 3}),
                type('name', (object,),
                     {'nameID': 1, 'string': 'FamilyNameRegular',
                      'langID': 0, 'platformID': 1})
            ]

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            self.failure_run(targetTestCase)

            mocked_get_ttfont.return_value.names = [
                type('name', (object,),
                     {'nameID': 1, 'string': 'FamilyNameRegular',
                      'langID': 0x409, 'platformID': 3}),
                type('name', (object,),
                     {'nameID': 1, 'string': 'FamilyNameRegular',
                      'langID': 0, 'platformID': 1})
            ]

            self.success_run(targetTestCase)


class Test_CheckPostScriptNameMatchesWeight(TestCase):

    @mock.patch.object(downstream.CheckPostScriptNameMatchesWeight,
                       'read_metadata_contents')
    def test_twenty_three(self, metadata_contents):
        targetTestCase = downstream.CheckPostScriptNameMatchesWeight
        targetTestCase.operator = TestCaseOperator('')

        metadata_contents.return_value = json.dumps({
            'fonts': [{'weight': 400, 'postScriptName': 'Fam-Regular'},
                      {'weight': 400, 'postScriptName': 'Fam-Italic'},
                      {'weight': 100, 'postScriptName': 'Fam-Thin'},
                      {'weight': 100, 'postScriptName': 'Fam-ThinItalic'},
                      {'weight': 200, 'postScriptName': 'Fam-ExtraLight'},
                      {'weight': 200, 'postScriptName': 'Fam-ExtraLightItalic'},
                      {'weight': 300, 'postScriptName': 'Fam-Light'},
                      {'weight': 300, 'postScriptName': 'Fam-LightItalic'},
                      {'weight': 500, 'postScriptName': 'Fam-Medium'},
                      {'weight': 500, 'postScriptName': 'Fam-MediumItalic'},
                      {'weight': 600, 'postScriptName': 'Fam-SemiBold'},
                      {'weight': 600, 'postScriptName': 'Fam-SemiBoldItalic'},
                      {'weight': 700, 'postScriptName': 'Fam-Bold'},
                      {'weight': 700, 'postScriptName': 'Fam-BoldItalic'},
                      {'weight': 800, 'postScriptName': 'Fam-ExtraBold'},
                      {'weight': 800, 'postScriptName': 'Fam-ExtraBoldItalic'},
                      {'weight': 900, 'postScriptName': 'Fam-Black'},
                      {'weight': 900, 'postScriptName': 'Fam-BlackItalic'}]
        })
        self.success_run(targetTestCase)

        metadata_contents.return_value = json.dumps({
            'fonts': [{'weight': 500, 'postScriptName': 'Family-Regular'}]
        })

        self.failure_run(targetTestCase)


class Test_CheckMetadataContainsReservedFontName(TestCase):

    @mock.patch.object(downstream.CheckMetadataContainsReservedFontName,
                       'read_metadata_contents')
    def test_twenty_four(self, metadata_contents):
        targetTestCase = downstream.CheckMetadataContainsReservedFontName
        targetTestCase.operator = TestCaseOperator('')

        metadata_contents.return_value = json.dumps({
            'fonts': [{'copyright': ('Copyright (c) 2014 (mail@example.com)'
                                     ' with Reserved Font Name')}]
        })
        self.failure_run(targetTestCase)

        metadata_contents.return_value = json.dumps({
            'fonts': [{'copyright': 'Copyright (c) 2014 (mail@example.com)'}]
        })

        self.success_run(targetTestCase)

        metadata_contents.return_value = json.dumps({
            'fonts': [{'copyright': ('Copyright (c) 2014'
                                     ' with Reserved Font Name')}]
        })

        self.failure_run(targetTestCase)


class Test_CheckLicenseIncluded(TestCase):

    def test_twenty_five(self):
        targetTestCase = downstream.CheckLicenseIncluded
        targetTestCase.operator = TestCaseOperator('')

        class Font(object):
            bin2unistring = OriginFont.bin2unistring

            license_url = ''

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            self.failure_run(targetTestCase)

            mocked_get_ttfont.return_value.license_url = 'http://example.com/'
            self.success_run(targetTestCase)


class Test_CheckFontWeightSameAsInMetadata(TestCase):

    @mock.patch.object(downstream.CheckFontWeightSameAsInMetadata, 'read_metadata_contents')
    def test_twenty_six(self, metadata_contents):
        targetTestCase = downstream.CheckFontWeightSameAsInMetadata
        targetTestCase.operator = TestCaseOperator('')

        metadata_contents.return_value = json.dumps({
            'fonts': [{'filename': 'Family-Regular.ttf', 'weight': 400}]
        })

        class Font(object):
            OS2_usWeightClass = 400

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as get_ttfont:
            get_ttfont.return_value = Font()

            self.success_run(targetTestCase)

            get_ttfont.return_value.OS2_usWeightClass = 300
            self.failure_run(targetTestCase)


class Test_CheckFontNameEqualToMacStyleFlags(TestCase):

    def test_twenty_seven(self):
        targetTestCase = downstream.CheckFontNameEqualToMacStyleFlags
        targetTestCase.operator = TestCaseOperator('')

        class Font(object):
            macStyle = 0b00101011
            fullname = 'Family-Regular'

        with mock.patch.object(OriginFont, 'get_ttfont') as get_ttfont:
            get_ttfont.return_value = Font()
            self.failure_run(targetTestCase)

            get_ttfont.return_value.fullname = 'Family-BoldItalic'
            self.success_run(targetTestCase)

            get_ttfont.return_value.fullname = 'Family-Regular'
            get_ttfont.return_value.macStyle = 0b00
            self.success_run(targetTestCase)


class Test_CheckItalicStyleMatchesMacStyle(TestCase):

    @mock.patch.object(downstream.CheckItalicStyleMatchesMacStyle, 'read_metadata_contents')
    def test_twenty_six(self, metadata_contents):
        targetTestCase = downstream.CheckItalicStyleMatchesMacStyle
        targetTestCase.operator = TestCaseOperator('')

        metadata_contents.return_value = json.dumps({
            'fonts': [{'filename': 'Family-Regular.ttf',
                       'style': 'italic'}]
        })

        class Font(object):
            macStyle = 0b10
            fullname = 'Family-Italic'
            familyname = 'Family-Italic'

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as get_ttfont:
            get_ttfont.return_value = Font()
            self.success_run(targetTestCase)

            get_ttfont.return_value.fullname = 'Family-Regular'
            self.failure_run(targetTestCase)

            get_ttfont.return_value.familyname = 'Family-Regular'
            self.failure_run(targetTestCase)

            get_ttfont.return_value.macStyle = 0
            self.failure_run(targetTestCase)


class Test_CheckNormalStyleMatchesMacStyle(TestCase):

    @mock.patch.object(downstream.CheckNormalStyleMatchesMacStyle, 'read_metadata_contents')
    def test_twenty_six(self, metadata_contents):
        targetTestCase = downstream.CheckNormalStyleMatchesMacStyle
        targetTestCase.operator = TestCaseOperator('')

        metadata_contents.return_value = json.dumps({
            'fonts': [{'filename': 'Family-Regular.ttf',
                       'style': 'normal'}]
        })

        class Font(object):
            macStyle = 0
            fullname = 'Family-Bold'
            familyname = 'Family-Bold'

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as get_ttfont:
            get_ttfont.return_value = Font()

            self.success_run(targetTestCase)

            get_ttfont.return_value.fullname = 'Family-Italic'
            self.failure_run(targetTestCase)

            get_ttfont.return_value.familyname = 'Family-BoldItalic'
            self.failure_run(targetTestCase)

            get_ttfont.return_value.macStyle = 0b10
            self.failure_run(targetTestCase)


class Test_CheckNamesAreASCIIOnly(TestCase):

    def test_twenty_seven(self):
        targetTestCase = downstream.CheckNamesAreASCIIOnly
        targetTestCase.operator = TestCaseOperator('')

        class Font(object):
            pass

        with mock.patch.object(OriginFont, 'get_ttfont') as get_ttfont:
            get_ttfont.return_value = Font()
            get_ttfont.return_value.names = [
                type('name', (object,),
                     {'nameID': 1, 'string': 'FamilyNameRegular',
                      'langID': 0x409, 'platformID': 3}),
            ]
            self.success_run(targetTestCase)

            get_ttfont.return_value.names = [
                type('name', (object,),
                     {'nameID': 1, 'string': u'FamilyNameRegularЙ',
                      'langID': 0x409, 'platformID': 3}),
            ]


class Test_CheckMetadataFields(TestCase):

    @mock.patch.object(downstream.CheckMetadataFields, 'read_metadata_contents')
    def test_twenty_eight(self, metadata_contents):
        targetTestCase = downstream.CheckMetadataFields
        targetTestCase.operator = TestCaseOperator('')

        metadata_contents.return_value = json.dumps({
            'fonts': [{'name': 'Family',
                       'filename': 'Family-Regular.ttf',
                       'weight': 400,
                       'fullName': 'Family Regular',
                       'postScriptName': 'Family-Regular',
                       'style': 'normal',
                       'copyright': ''}]
        })
        self.success_run(targetTestCase)

        metadata_contents.return_value = json.dumps({
            'fonts': [{'name': 'Family',
                       'filename': 'Family-Regular.ttf',
                       # 'weight': 400,
                       # 'fullName': 'Family Regular',
                       # 'postScriptName': 'Family-Regular',
                       # 'style': 'normal',
                       'copyright': ''}]
        })
        self.failure_run(targetTestCase)

        metadata_contents.return_value = json.dumps({
            'fonts': [{'name': 'Family',
                       'filename': 'Family-Regular.ttf',
                       'weight': 400,
                       'fullName': 'Family Regular',
                       'postScriptName': 'Family-Regular',
                       'style': 'normal',
                       'copyright': '',
                       'tables': []}]
        })
        self.failure_run(targetTestCase)


class Test_CheckFontHasDsigTable(TestCase):

    def test_twenty_nine(self):
        targetTestCase = downstream.CheckFontHasDsigTable
        targetTestCase.operator = TestCaseOperator('')

        with mock.patch.object(OriginFont, 'get_ttfont') as get_ttfont:
            with mock.patch('bakery_cli.pipe.autofix.dsig_signature') as dsig:
                get_ttfont.return_value = {'DSIG': True}
                self.success_run(targetTestCase)
                self.assert_(not dsig.called)

                get_ttfont.return_value = {}
                self.failure_run(targetTestCase)
                self.assert_(dsig.called)


class Test_CheckFontHasNotKernTable(TestCase):

    def test_twenty_nine(self):
        targetTestCase = downstream.CheckFontHasNotKernTable
        targetTestCase.operator = TestCaseOperator('')

        with mock.patch.object(OriginFont, 'get_ttfont') as get_ttfont:
            get_ttfont.return_value = {'KERN': True}
            self.failure_run(targetTestCase)

            get_ttfont.return_value = {}
            self.success_run(targetTestCase)


class Test_CheckGposTableHasKerningInfo(TestCase):

    def test_thirty(self):
        targetTestCase = downstream.CheckGposTableHasKerningInfo
        targetTestCase.operator = TestCaseOperator('')

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
            self.success_run(targetTestCase)

            get_ttfont.return_value = {}
            self.failure_run(targetTestCase)


class Test_CheckGaspTableType(TestCase):

    def test_thirty_one(self):
        targetTestCase = downstream.CheckGaspTableType
        targetTestCase.operator = TestCaseOperator('')

        with mock.patch.object(OriginFont, 'get_ttfont') as get_ttfont:

            with mock.patch('bakery_cli.pipe.autofix.gaspfix') as fix:

                gasp = type('GASP', (object, ), {'gaspRange': {65535: 15}})
                get_ttfont.return_value = {'gasp': gasp}
                self.success_run(targetTestCase)
                assert fix.called

                gasp = type('GASP', (object, ), {'gaspRange': []})
                get_ttfont.return_value = {'gasp': gasp}
                self.failure_run(targetTestCase)

                assert fix.called

                gasp = type('GASP', (object, ), {'gaspRange': {65535: 14}})
                get_ttfont.return_value = {'gasp': gasp}
                self.failure_run(targetTestCase)

                get_ttfont.return_value = {}
                self.failure_run(targetTestCase)


class Test_CheckMonospaceAgreement(TestCase):

    @mock.patch.object(downstream.CheckMonospaceAgreement,
                       'read_metadata_contents')
    def test_thirty_two(self, metadata_contents):
        targetTestCase = downstream.CheckMonospaceAgreement
        targetTestCase.operator = TestCaseOperator('')

        metadata_contents.return_value = json.dumps({
            'category': 'Monospace',
            'fonts': [{'name': 'Family',
                       'filename': 'Family-Regular.ttf'}]
        })

        class Font(object):

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
            self.success_run(targetTestCase)

            get_ttfont.return_value._glyph_advance_width = 1111
            self.failure_run(targetTestCase)


class Test_CheckItalicAngleAgreement(TestCase):

    def test_thirty_three(self):
        targetTestCase = downstream.CheckItalicAngleAgreement
        targetTestCase.operator = TestCaseOperator('')

        class Font(object):
            italicAngle = 0

        with mock.patch.object(OriginFont, 'get_ttfont') as get_ttfont:
            get_ttfont.return_value = Font()
            self.success_run(targetTestCase)

            get_ttfont.return_value.italicAngle = 10
            self.failure_run(targetTestCase)

            get_ttfont.return_value.italicAngle = -30
            self.failure_run(targetTestCase)


class Test_CheckGlyphExistence(TestCase):

    def test_thirty_four(self):
        targetTestCase = downstream.CheckGlyphExistence
        targetTestCase.operator = TestCaseOperator('')

        class Font(object):

            _cmap = {
                160: 'nonbreakingspace',
                32: 'space',
                8364: 'Euro'
            }

            def retrieve_cmap_format_4(self):
                return type('cmap', (object, ), {'cmap': self._cmap})

        with mock.patch.object(OriginFont, 'get_ttfont') as get_ttfont:
            get_ttfont.return_value = Font()

            self.success_run(targetTestCase)

            get_ttfont.return_value._cmap = {
                160: 'nonbreakingspace',
                32: 'space'
            }
            self.failure_run(targetTestCase)

            get_ttfont.return_value._cmap = {
                160: 'nonbreakingspace',
                8364: 'Euro'
            }
            self.failure_run(targetTestCase)

            get_ttfont.return_value._cmap = {
                32: 'space',
                8364: 'Euro'
            }
            self.failure_run(targetTestCase)


class Test_UfoFontFamilyRecommendation(TestCase):

    def test_fullfontname_less_than_64_chars(self):
        targetTestCase = upstream.TestUFOFontFamilyNamingTest
        targetTestCase.operator = TestCaseOperator('Font.ufo')

        sfnt_names = [
            (),
            ('', '', 'Font'),  # familyname
            ('', '', 'Bold'),  # stylename
            (),
            ('', '', 'Font Bold'),  # fullname
            (),
            ('', '', 'Font-Bold')  # postscriptname
        ]

        failure_sfntnames = [
            (),
            ('', '', 'Font'),  # familyname
            ('', '', 'Bold'),  # stylename
            (),
            ('', '', 'Font Bold'),  # fullname
            (),
            ('', '', 'Font-Bold-Gold')  # postscriptname
        ]

        with mock.patch('fontforge.open') as ff:
            ff.return_value = type('sfnt_names', (object, ),
                                   {'sfnt_names': sfnt_names,
                                    'os2_weight': 250})
            self.success_run(targetTestCase)

            ff.return_value = type('sfnt_names', (object, ),
                                   {'sfnt_names': sfnt_names,
                                    'os2_weight': 900})
            self.success_run(targetTestCase)

            ff.return_value = type('sfnt_names', (object, ),
                                   {'sfnt_names': failure_sfntnames,
                                    'os2_weight': 900})
            self.failure_run(targetTestCase)

            ff.return_value = type('sfnt_names', (object, ),
                                   {'sfnt_names': sfnt_names,
                                    'os2_weight': 1000})
            self.failure_run(targetTestCase)

            ff.return_value = type('sfnt_names', (object, ),
                                   {'sfnt_names': sfnt_names,
                                    'os2_weight': 200})
            self.failure_run(targetTestCase)

            ff.return_value = type('sfnt_names', (object, ),
                                   {'sfnt_names': sfnt_names,
                                    'os2_weight': 355})
            self.failure_run(targetTestCase)


class Test_NameTableRecommendation(TestCase):

    def test_thirty_five(self):
        targetTestCase = downstream.CheckOTStyleNameRecommendation
        targetTestCase.operator = TestCaseOperator('')

        class Font(object):
            ot_style_name = 'Regular'

        with mock.patch.object(OriginFont, 'get_ttfont') as get_ttfont:
            with mock.patch('bakery_cli.pipe.autofix.fix_opentype_specific_fields') as fix:
                get_ttfont.return_value = Font
                for stylename in ['Regular', 'Italic', 'Bold', 'Bold Italic']:
                    get_ttfont.return_value.stylename = stylename
                    self.success_run(targetTestCase)
                    assert not fix.called

                get_ttfont.return_value.ot_style_name = 'Black Italic'

                self.failure_run(targetTestCase)
                assert fix.called


class Test_CheckOTFamilyNameRecommendation(TestCase):

    def test_thirty_six(self):
        targetTestCase = downstream.CheckOTFamilyNameRecommendation
        targetTestCase.operator = TestCaseOperator('')

        class Font(OriginFont):

            names = [
                type('name', (object, ),
                     {'nameID': 1, 'string': 'Hello', 'platformID': 1,
                      'langID': 0}),
                type('name', (object, ),
                     {'nameID': 16, 'string': 'Hello', 'platformID': 3,
                      'langID': 1033})]

        with mock.patch.object(OriginFont, 'get_ttfont') as get_ttfont:
            with mock.patch('bakery_cli.pipe.autofix.fix_opentype_specific_fields') as fix:
                get_ttfont.return_value = Font('')
                self.success_run(targetTestCase)
                assert not fix.called
                get_ttfont.return_value.names = [
                    type('name', (object, ),
                         {'nameID': 1, 'string': 'Hello', 'platformID': 1,
                          'langID': 0}),
                    type('name', (object, ),
                         {'nameID': 16, 'string': 'Hello', 'platformID': 1,
                          'langID': 0})
                ]
                self.failure_run(targetTestCase)
                assert fix.called


class Test_CheckOTFullNameRecommendation(TestCase):

    def test_thirty_eight(self):
        targetTestCase = downstream.CheckOTFullNameRecommendation
        targetTestCase.operator = TestCaseOperator('')

        class Font(OriginFont):

            names = [
                type('name', (object, ),
                     {'nameID': 4, 'string': 'Hello Bold', 'platformID': 1,
                      'langID': 0}),
                type('name', (object, ),
                     {'nameID': 18, 'string': 'Hello Bold', 'platformID': 3,
                      'langID': 1033})]

        with mock.patch.object(OriginFont, 'get_ttfont') as get_ttfont:
            with mock.patch('bakery_cli.pipe.autofix.fix_opentype_specific_fields') as fix:
                get_ttfont.return_value = Font('')
                self.success_run(targetTestCase)
                assert not fix.called

                get_ttfont.return_value.names = [
                    type('name', (object, ),
                         {'nameID': 4, 'string': 'Hello', 'platformID': 1,
                          'langID': 0}),
                    type('name', (object, ),
                         {'nameID': 18, 'string': 'Hello', 'platformID': 1,
                          'langID': 0})
                ]
                self.failure_run(targetTestCase)
                assert fix.called


class Test_CheckFSTypeTest(TestCase):

    def test_thirty_nine(self):
        targetTestCase = downstream.CheckFsTypeIsNotSet
        targetTestCase.operator = TestCaseOperator('')

        class Font(OriginFont):

            OS2_fsType = 12

        with mock.patch.object(OriginFont, 'get_ttfont') as get_ttfont:
            with mock.patch('bakery_cli.pipe.autofix.fix_fstype_to_zero') as fix:
                get_ttfont.return_value = Font('')
                self.failure_run(targetTestCase)
                assert fix.called

                get_ttfont.return_value.OS2_fsType = 0
                self.success_run(targetTestCase)
                assert fix.called


class Test_CheckVerticalMetricsAutoFixCalled(TestCase):

    def test_fourty(self):

        class FakeAscents(object):
            os2typo = 1200
            os2win = 1100
            hhea = 1100

        class Font(object):
            ascents = FakeAscents()

            def get_bounding(self):
                return 100, 1000

        targetTestCase = downstream.CheckVerticalAscentMetrics
        with mock.patch.object(OriginFont, 'get_ttfont') as get_ttfont:
            with mock.patch('bakery_cli.utils.UpstreamDirectory.get_binaries') as get_binaries:
                get_ttfont.return_value = Font()
                with mock.patch('bakery_cli.pipe.autofix.fix_metrics') as fix:

                    get_binaries.return_value = ['Font-Regular.ttf']
                    self.failure_run(targetTestCase)
                    assert fix.called

                with mock.patch('bakery_cli.pipe.autofix.fix_metrics') as fix:
                    get_ttfont.return_value.ascents.os2typo = 1000
                    get_ttfont.return_value.ascents.os2win = 1000
                    get_ttfont.return_value.ascents.hhea = 1000
                    self.success_run(targetTestCase)
                    assert not fix.called

    def test_fourty_one(self):

        class FakeDescents(object):
            os2typo = 1200
            os2win = 1100
            hhea = 1100

        class Font(object):
            descents = FakeDescents()

            def get_bounding(self):
                return -1000, 1000

        targetTestCase = downstream.CheckVerticalDescentMetrics
        with mock.patch.object(OriginFont, 'get_ttfont') as get_ttfont:
            get_ttfont.return_value = Font()
            with mock.patch('bakery_cli.utils.UpstreamDirectory.get_binaries') as get_binaries:
                get_binaries.return_value = ['Font-Regular.ttf']

                with mock.patch('bakery_cli.pipe.autofix.fix_metrics') as fix:

                    self.failure_run(targetTestCase)
                    assert fix.called

                with mock.patch('bakery_cli.pipe.autofix.fix_metrics') as fix:
                    get_ttfont.return_value.descents.os2typo = 1000
                    get_ttfont.return_value.descents.os2win = 1000
                    get_ttfont.return_value.descents.hhea = 1000
                    self.success_run(targetTestCase)
                    assert not fix.called


class TestFontOnDiskFamilyEqualToMetadataJSON(TestCase):

    @mock.patch.object(downstream.TestFontOnDiskFamilyEqualToMetadataJSON,
                       'read_metadata_contents')
    def test_font_on_disk_family_equal_in_metadata_json(self, obj):
        obj.return_value = json.dumps({
            'fonts': [{
                'name': 'FamilyName',
                'filename': 'FamilyName-Regular.ttf'
            }]
        })

        class FontFailure(object):

            @property
            def familyname(self):
                return 'Family'

        class FontSuccess(object):

            @property
            def familyname(self):
                return 'FamilyName'

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as func:
            func.return_value = FontFailure()
            self.failure_run(downstream.TestFontOnDiskFamilyEqualToMetadataJSON)

            func.return_value = FontSuccess()
            self.success_run(downstream.TestFontOnDiskFamilyEqualToMetadataJSON)


class TestPostScriptNameInMetadataEqualFontOnDisk(TestCase):

    @mock.patch.object(downstream.TestPostScriptNameInMetadataEqualFontOnDisk,
                       'read_metadata_contents')
    def test_font_on_disk_family_equal_in_metadata_json(self, obj):
        obj.return_value = json.dumps({
            'fonts': [{
                'postScriptName': 'FamilyName'
            }]
        })

        class FontFailure(object):

            @property
            def post_script_name(self):
                return 'Family'

        class FontSuccess(object):

            @property
            def post_script_name(self):
                return 'FamilyName'

        with mock.patch.object(OriginFont, 'get_ttfont_from_metadata') as func:
            func.return_value = FontFailure()
            self.failure_run(downstream.TestPostScriptNameInMetadataEqualFontOnDisk)

            func.return_value = FontSuccess()
            self.success_run(downstream.TestPostScriptNameInMetadataEqualFontOnDisk)
