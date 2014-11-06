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


class TestMetricsSymmetry(TestCase):

    targets = ['upstream']
    name = __name__
    tool = 'lint'

    @classmethod
    def skipUnless(cls):
        return not cls.operator.path.endswith('.ufo')

    def test_metrics_symmetry(self):
        """ The side-bearings are almost equal. """
        font = robofab.world.OpenFont(self.operator.path)

        for glyph in font:
            left = glyph.leftMargin
            right = glyph.rightMargin
            diff = int(round(abs(left - right)))
            if diff == 1:
                message = "The side-bearings are 1 unit from being equal."
            else:
                message = "The side-bearings are %d units from being equal." % diff
            if 0 < diff <= 5:
                self.fail('{0} ({1})'.format(message, glyph.name))
