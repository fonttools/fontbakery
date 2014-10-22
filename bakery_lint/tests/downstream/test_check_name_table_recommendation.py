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
from bakery_lint.base import BakeryTestCase as TestCase, autofix
from bakery_cli.ttfont import Font, getSuggestedFontNameValues


class CheckOTStyleNameRecommendation(TestCase):

    targets = ['result']
    tool = 'lint'
    name = __name__

    @autofix('bakery_cli.pipe.autofix.fix_opentype_specific_fields')
    def test_check_stylename_is_under_recommendations(self):
        """ Style name must be equal to one of the following four
            values: “Regular”, “Italic”, “Bold” or “Bold Italic” """
        font = Font.get_ttfont(self.operator.path)
        self.assertIn(font.ot_style_name, ['Regular', 'Italic',
                                           'Bold', 'Bold Italic'])


class CheckOTFamilyNameRecommendation(TestCase):

    targets = ['result']
    tool = 'lint'
    name = __name__

    @autofix('bakery_cli.pipe.autofix.fix_opentype_specific_fields')
    def test_check_opentype_familyname(self):
        """ OT Family Name for Windows should be equal to Family Name """
        font = Font.get_ttfont(self.operator.path)
        self.assertEqual(font.ot_family_name, font.familyname)


class CheckOTFullNameRecommendation(TestCase):

    targets = ['result']
    tool = 'lint'
    name = __name__

    @autofix('bakery_cli.pipe.autofix.fix_opentype_specific_fields')
    def test_check_opentype_fullname(self):
        """ Full name matches Windows-only Opentype-specific FullName """
        font = Font.get_ttfont(self.operator.path)
        self.assertEqual(font.ot_full_name, font.fullname)


class CheckSuggestedSubfamilyName(TestCase):

    targets = ['result']
    tool = 'lint'
    name = __name__

    @autofix('bakery_cli.pipe.autofix.fix_opentype_specific_fields')
    def test_suggested_subfamily_name(self):
        """ Family does not contain subfamily in `name` table """
        # Currently we just look that family does not contain any spaces
        # in its name. This prevent us from incorrect suggestions of names
        font = Font.get_ttfont(self.operator.path)
        suggestedvalues = getSuggestedFontNameValues(font.ttfont)
        self.assertEqual(font.familyname, suggestedvalues['family'])
        self.assertEqual(font.stylename, suggestedvalues['subfamily'])
