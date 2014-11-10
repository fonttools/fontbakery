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
import re

from bakery_lint.base import BakeryTestCase, tags
from fontTools.agl import AGL2UV
import robofab.world


uniNamePattern = re.compile(
    "uni"
    "([0-9A-Fa-f]{4})"
    "$"
)


class UniqueUnicodeValues(BakeryTestCase):

    targets = ['upstream']
    name = __name__
    tool = 'lint'

    @classmethod
    def skipUnless(cls):
        return not cls.operator.path.lower().endswith('.ufo')

    @tags('note')
    def test_unique_unicode_values(self):
        """ Font unicode values are unique? """

        font = robofab.world.OpenFont(self.operator.path)

        for glyphname in font.keys():
            glyph = font[glyphname]

            uni = glyph.unicode
            name = glyph.name

            # test for uniXXXX name
            m = uniNamePattern.match(name)
            if m is not None:
                uniFromName = m.group(1)
                uniFromName = int(uniFromName, 16)
                if uni != uniFromName:
                    self.fail(("Unicode value of glyph {} "
                               "does not match glyph name "
                               "of uniXXXX").format(name))
            # test against AGLFN
            else:
                expectedUni = AGL2UV.get(name)
                if expectedUni != uni:
                    self.fail(("Unicode value of glyph {} "
                               "does not match glyph name "
                               "from fontTools AGL2UV").format(name))

            # look for duplicates
            if uni is not None:
                duplicates = []
                for name in sorted(font.keys()):
                    if name == glyph.name:
                        continue
                    other = font[name]
                    if other.unicode == uni:
                        duplicates.append(name)

                if duplicates:
                    self.fail("Unicode value of {0} is also used by {1}".format(glyph.name, " ".join(duplicates)))
