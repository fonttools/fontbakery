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
from checker.base import BakeryTestCase as TestCase, tags
from checker.metadata import Metadata


class CheckMetadataFields(TestCase):

    path = '.'
    name = __name__
    targets = ['metadata']
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.path).read()

    @tags('required')
    def test_check_metadata_fields(self):
        """ Check METADATA.json "fonts" property items have required field """
        contents = self.read_metadata_contents()
        family = Metadata.get_family_metadata(contents)

        keys = [("name", str), ("postScriptName", str),
                ("fullName", str), ("style", str),
                ("weight", int), ("filename", str),
                ("copyright", str)]

        missing = set([])
        unknown = set([])

        for j, itemtype in keys:

            for font_metadata in family.fonts:
                if j not in font_metadata:
                    missing.add(j)

                for k in font_metadata:
                    if k not in map(lambda x: x[0], keys):
                        unknown.add(k)

        if unknown:
            msg = 'METADATA.json "fonts" property has unknown items [%s]'
            self.fail(msg % ', '.join(unknown))

        if missing:
            msg = 'METADATA.json "fonts" property items missed [%s] items'
            self.fail(msg % ', '.join(missing))

