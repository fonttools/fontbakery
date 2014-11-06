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
import robofab.world
from bakery_lint.tests import unicodeTools

from bakery_lint.base import BakeryTestCase as TestCase




class TestComponentMetrics(TestCase):

    targets = ['upstream']
    name = __name__
    tool = 'lint'

    @classmethod
    def skipUnless(cls):
        return not cls.operator.path.endswith('.ufo')

    def setUp(self):
        self.font = robofab.world.OpenFont(self.operator.path)

    def _getXMinMaxComponents(self, components):
        minSide = []
        maxSide = []
        for component in components:
            xMin, _, xMax, _ = component.box
            minSide.append((xMin, component))
            maxSide.append((xMax, component))
        o = [
            min(minSide)[-1],
            max(maxSide)[-1],
        ]
        return o

    def _getComponentBaseMargins(self, component):
        baseGlyphName = component.baseGlyph
        baseGlyph = self.font[baseGlyphName]
        scale = component.scale[0]
        left = baseGlyph.leftMargin * scale
        right = baseGlyph.rightMargin * scale
        return left, right

    def unicodeForGlyphName(self, glyphName):
        """
        Get the Unicode value for **glyphName**. Returns *None*
        if no value is found.
        """
        if glyphName not in self.font:
            return None
        glyph = self.font[glyphName]
        unicodes = glyph.unicodes
        if not unicodes:
            return None
        return unicodes[0]

    def pseudoUnicodeForGlyphName(self, glyphName):
        """
        Get the pseudo-Unicode value for **glyphName**.
        This will return *None* if nothing is found.
        """
        realValue = self.unicodeForGlyphName(glyphName)
        if realValue is not None:
            return realValue
        # glyph doesn't have a suffix
        if glyphName.startswith(".") or glyphName.startswith("_"):
            return None
        if "." not in glyphName and "_" not in glyphName:
            return None
        # get the base
        base = glyphName.split(".")[0]
        # in the case of ligatures, grab the first glyph
        base = base.split("_")[0]
        # get the value for the base
        return self.unicodeForGlyphName(base)

    def categoryForGlyphName(self, glyphName, allowPseudoUnicode=True):
        """ Get the category for **glyphName**. If **allowPseudoUnicode** is
        True, a pseudo-Unicode value will be used if needed. This will
        return *None* if nothing can be found.
        """
        if allowPseudoUnicode:
            value = self.pseudoUnicodeForGlyphName(glyphName)
        else:
            value = self.unicodeForGlyphName(glyphName)
        if value is None:
            return "Cn"
        return unicodeTools.category(value)

    def test_component_metrics(self):
        """ The side-bearings don't match the component's metrics. """
        for glyph in self.font:
            components = [c for c in glyph.components
                          if c.baseGlyph in self.font]
            # no components
            if len(components) == 0:
                continue

            if len(components) > 1:
                # filter marks
                nonMarks = []
                markCategories = ("Sk", "Zs", "Lm")
                for component in components:
                    baseGlyphName = component.baseGlyph
                    category = self.categoryForGlyphName(baseGlyphName, allowPseudoUnicode=True)
                    if category not in markCategories:
                        nonMarks.append(component)
                if nonMarks:
                    components = nonMarks
            # order the components from left to right based on their boxes
            if len(components) > 1:
                leftComponent, rightComponent = self._getXMinMaxComponents(components)
            else:
                leftComponent = rightComponent = components[0]
            expectedLeft = self._getComponentBaseMargins(leftComponent)[0]
            expectedRight = self._getComponentBaseMargins(rightComponent)[1]
            left = leftComponent.box[0]
            right = glyph.width - rightComponent.box[2]
            if left != expectedLeft:
                self.fail("%s component left does not match %s left" % (leftComponent.baseGlyph, leftComponent.baseGlyph))
            if right != expectedRight:
                self.fail("%s component right does not match %s right" % (rightComponent.baseGlyph, rightComponent.baseGlyph))
