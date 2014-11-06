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

from bakery_lint.base import BakeryTestCase as TestCase


class TestLigatureMetrics(TestCase):

    targets = ['upstream']
    name = __name__
    tool = 'lint'

    @classmethod
    def skipUnless(cls):
        return not cls.operator.path.endswith('.ufo')

    def test_ligature_metrics(self):
        """ The side-bearings don't match the ligature's presumed
        part metrics. """
        font = robofab.world.OpenFont(self.operator.path)

        for glyph in font:
            name = glyph.name
            if "_" not in name:
                continue
            base = name
            suffix = None
            if "." in name:
                base, suffix = name.split(".", 1)
            # guess at the ligature parts
            parts = base.split("_")
            leftPart = parts[0]
            rightPart = parts[-1]
            # try snapping on the suffixes
            if suffix:
                if leftPart + "." + suffix in font:
                    leftPart += "." + suffix
                if rightPart + "." + suffix in font:
                    rightPart += "." + suffix
            # test
            left = glyph.leftMargin
            right = glyph.rightMargin
            if leftPart not in font:
                self.fail("Couldn't find the ligature's left"
                          " component for {}.".format(name))
            else:
                expectedLeft = font[leftPart].leftMargin
                if left != expectedLeft:
                    self.fail("Left doesn't match the presumed part"
                              " {0} left for {1}".format(leftPart, name))
            if rightPart not in font:
                self.fail("Couldn't find the ligature's right component"
                          " for {}.".format(name))
            else:
                expectedRight = font[rightPart].rightMargin
                if right != expectedRight:
                    self.fail("Right doesn't match the presumed part"
                              " {0} right for {1}".format(rightPart, name))
