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
import json


class FamilyMetadata(object):

    def __init__(self, metadata_object):
        assert type(metadata_object) == dict
        self.metadata_object = metadata_object

    @property
    def name(self):
        return self.metadata_object['name']

    @property
    def designer(self):
        return self.metadata_object.get('designer', '')

    @property
    def license(self):
        return self.metadata_object.get('license', '')

    @property
    def visibility(self):
        return self.metadata_object.get('visibility', 'Sandbox')

    @property
    def category(self):
        return self.metadata_object.get('category', '')

    @property
    def size(self):
        return self.metadata_object.get('size', 0)

    @property
    def date_added(self):
        # TODO: property has to return datetime object or None
        #  For the moment it is enough to return string value
        #  but need to remember that string value is hard to validate
        #  to correct date
        return self.metadata_object.get('dateAdded', '')

    @property
    def subsets(self):
        return self.metadata_object.get('subsets', [])

    @property
    def fonts(self):
        for f in self.metadata_object['fonts']:
            yield FontMetadata(f)


class FontMetadata(object):

    def __init__(self, metadata_object):
        self.metadata_object = metadata_object

    @property
    def name(self):
        return self.metadata_object['name']

    @property
    def post_script_name(self):
        return self.metadata_object.get('postScriptName', '')

    @property
    def full_name(self):
        return self.metadata_object.get('full_name', '')

    @property
    def style(self):
        return self.metadata_object.get('style', 'normal')

    @property
    def weight(self):
        return self.metadata_object.get('weight', 400)

    @property
    def filename(self):
        return self.metadata_object.get('filename', '')

    @property
    def copyright(self):
        return self.metadata_object.get('copyright', '')


class Metadata(object):

    @staticmethod
    def get_family_metadata(contents):
        """ Returns root of FamilyMetadata instance

            Args:
                contents: Metadata jsoned object dumped to string
        """
        return FamilyMetadata(json.loads(contents))
