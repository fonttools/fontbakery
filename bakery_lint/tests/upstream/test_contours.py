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
from robofab.pens.digestPen import DigestPointPen


class TestForOpenContours(TestCase):

    targets = ['upstream']
    name = __name__
    tool = 'lint'

    @classmethod
    def skipUnless(cls):
        return not cls.operator.path.endswith('.ufo')

    def test_for_open_contours(self):
        """ One or more contours are not properly closed. """
        font = robofab.world.OpenFont(self.operator.path)

        for glyph in font:
            openContours = {}
            for index, contour in enumerate(glyph):
                if not contour.points or contour.points[0].type == 'move':
                    continue

                start = contour[0].onCurve
                start = (start.x, start.y)
                end = contour[-1].onCurve
                end = (end.x, end.y)
                if start != end:
                    openContours[index] = (start, end)

            if openContours:
                self.fail('{0} has opened contours {1}'.format(glyph.name, openContours))


class TestForSmallContours(TestCase):

    targets = ['upstream']
    name = __name__
    tool = 'lint'

    @classmethod
    def skipUnless(cls):
        return not cls.operator.path.endswith('.ufo')

    def test_for_small_contours(self):
        """ One or more contours are suspiciously small. """
        font = robofab.world.OpenFont(self.operator.path)

        for glyph in font:
            smallContours = {}
            for index, contour in enumerate(glyph):
                box = contour.box
                if not box:
                    continue
                xMin, yMin, xMax, yMax = box
                w = xMax - xMin
                h = yMin - yMax
                area = abs(w * h)
                if area <= 4:
                    smallContours[index] = contour.box
            if smallContours:
                self.fail('{0} has suspiciously small contours {1}'.format(glyph.name, smallContours))


class TestDuplicateContours(TestCase):

    targets = ['upstream']
    name = __name__
    tool = 'lint'

    @classmethod
    def skipUnless(cls):
        return not cls.operator.path.endswith('.ufo')

    def test_duplicate_contours(self):
        """ One or more contours are duplicated. """
        font = robofab.world.OpenFont(self.operator.path)

        for glyph in font:
            contours = {}
            for index, contour in enumerate(glyph):
                contour = contour.copy()
                contour.autoStartSegment()
                pen = DigestPointPen()
                contour.drawPoints(pen)
                digest = pen.getDigest()
                if digest not in contours:
                    contours[digest] = []
                contours[digest].append(index)
            duplicateContours = []
            for digest, indexes in contours.items():
                if len(indexes) > 1:
                    duplicateContours.append(indexes[0])
            if duplicateContours:
                self.fail('{0} has duplicated contours {1}'.format(glyph.name, duplicateContours))
