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
import magic
import os.path as op

from bakery_lint.base import BakeryTestCase as TestCase, tags
from bakery_lint.metadata import Metadata


class CheckFontsMenuAgreements(TestCase):

    name = __name__
    targets = ['metadata']
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    def menufile(self, font_metadata):
        return '%s.menu' % font_metadata.filename[:-4]

    @tags('required')
    def test_menu_file_agreement(self):
        """ Check fonts have corresponding menu files """
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)
        for font_metadata in fm.fonts:
            menufile = self.menufile(font_metadata)
            path = op.join(op.dirname(self.operator.path), menufile)

            if not op.exists(path):
                self.fail('%s does not exist' % menufile)

            if magic.from_file(path) != 'TrueType font data':
                self.fail('%s is not actual TTF file' % menufile)
