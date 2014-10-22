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

from bakery_lint.base import BakeryTestCase as TestCase
from bakery_lint.metadata import Metadata


class File(object):

    def __init__(self, rootdir):
        self.rootdir = rootdir

    def exists(self, filename):
        return op.exists(op.join(self.rootdir, filename))

    def size(self, filename):
        return op.getsize(op.join(self.rootdir, filename))

    def mime(self, filename):
        return magic.from_file(op.join(self.rootdir, filename), mime=True)


class CheckSubsetsExist(TestCase):

    targets = ['metadata']
    tool = 'lint'
    name = __name__

    def setUp(self):
        self.f = File(op.dirname(self.operator.path))

    def read_metadata_contents(self):
        return open(self.operator.path).read()

    def get_subset_filename(self, font_filename, subset_name):
        return font_filename.replace('.ttf', '.%s' % subset_name)

    def test_check_subsets_exists(self):
        """ Check that corresponding subset files exist for fonts """
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)
        for font_metadata in fm.fonts:
            for subset in fm.subsets:
                subset_filename = self.get_subset_filename(font_metadata.filename, subset)

                error = "The subset file for the %s subset does not exist"
                error = error % subset_filename
                self.assertTrue(self.f.exists(subset_filename), error)

                error = "The subset file %s is bigger than the original file"
                error = error % subset_filename
                self.assertLessEqual(self.f.size(subset_filename),
                                     self.f.size(font_metadata.filename),
                                     error)

                self.assertEqual(self.f.mime(subset_filename),
                                 'application/x-font-ttf')
