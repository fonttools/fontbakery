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

from bakery_lint.base import BakeryTestCase as TestCase
from bakery_lint.metadata import Metadata


class CheckFontNameNotInCamelCase(TestCase):

    targets = ['metadata']
    name = __name__
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    def test_fontname_not_in_camel_case(self):
        """ Check if fontname is not camel cased """
        contents = self.read_metadata_contents()
        familymetadata = Metadata.get_family_metadata(contents)

        camelcased_fontnames = []
        for font_metadata in familymetadata.fonts:
            if bool(re.match(r'([A-Z][a-z]+){2,}', font_metadata.name)):
                camelcased_fontnames.append(font_metadata.name)

        if camelcased_fontnames:
            self.fail(('%s are camel cased names. To solve this check just '
                       'use spaces in names.'))
