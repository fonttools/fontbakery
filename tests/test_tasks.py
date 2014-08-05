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
""" To run this tests use `nosetests tests.test_tasks` from command line """
import os.path as op
import unittest

from bakery.app import app
from bakery.tasks import get_subsets_coverage_data


class TaskTestCase(unittest.TestCase):

    def test_subsets_coverage_data(self):
        path = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        self.assertTrue(get_subsets_coverage_data([path], ''))

        path = op.join(app.config['ROOT'], 'tests/fixtures/src/Font-Bold.ttx')
        self.assertTrue(get_subsets_coverage_data([path], ''))
