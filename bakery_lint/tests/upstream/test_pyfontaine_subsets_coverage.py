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
import os.path as op
import re
import yaml

from bakery_cli.bakery import BAKERY_CONFIGURATION_DEFAULTS
from bakery_cli.utils import UpstreamDirectory
from bakery_lint.base import BakeryTestCase as TestCase

from fontaine.font import FontFactory
from fontaine.cmap import Library


def get_test_subset_function(value):
    def function(self):
        self.assertEqual(value, 100)
    function.tags = ['note']
    return function


class FontaineTest(TestCase):

    targets = ['upstream-repo']
    tool = 'PyFontaine'
    name = __name__

    @classmethod
    def __generateTests__(cls):
        pattern = re.compile(r'[\W_]+')
        library = Library(collections=['subsets'])

        directory = UpstreamDirectory(cls.operator.path)

        yamlpath = op.join(cls.operator.path, 'bakery.yaml')
        try:
            bakerydata = yaml.load(open(yamlpath))
        except IOError:
            bakerydata = yaml.load(open(BAKERY_CONFIGURATION_DEFAULTS))


        for fontpath in directory.UFO + directory.TTX:
            font = FontFactory.openfont(op.join(cls.operator.path, fontpath))
            for charmap, _, coverage, _ in \
                    font.get_orthographies(_library=library):
                common_name = charmap.common_name.replace('Subset ', '')
                shortname = pattern.sub('', common_name)
                if shortname not in bakerydata['subset']:
                    continue

                exec 'cls.test_charset_%s = get_test_subset_function(%s)' % (shortname, coverage)
                exec 'cls.test_charset_%s.__func__.__doc__ = "Is %s covered 100%%?"' % (shortname, common_name)
