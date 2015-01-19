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
import unittest

from bakery_cli import utils


class TestCase(unittest.TestCase):

    def failure_run(self, test_klass, test_method=None):
        result = _run_font_test(test_klass, test_method)

        if result.errors:
            self.fail(result.errors[0][1])

        self.assertTrue(bool(result.failures))

    def success_run(self, test_klass, test_method=None):
        result = _run_font_test(test_klass, test_method)

        if result.errors:
            self.fail(result.errors[0][1])

        if result.failures:
            self.fail(result.failures[0][1])

        self.assertFalse(bool(result.failures))


def _run_font_test(testcase_klass, test_method):
    from bakery_lint.base import BakeryTestRunner, BakeryTestResult
    runner = BakeryTestRunner(resultclass=BakeryTestResult)
    tests = unittest.defaultTestLoader.loadTestsFromTestCase(testcase_klass)

    suite = unittest.TestSuite()
    for i, test in enumerate(tests):
        if test_method and test._testMethodName != test_method:
            continue
        suite.addTest(test)
    return runner.run(suite)


class TestSuggestNameTestCase(TestCase):

    def test_suggest_name_testcase_bold_italic(self):
        fontdata = {
            'names': [
                {'nameID': 1, 'string': 'Roboto'},
            ],
            'OS/2': {
                'fsSelection': 0b10001,  # Bold & Italic
                # As font is Bold this value is always 700
                'usWeightClass': 700,
            },
            'head': {
                'macStyle': 0b11,  # Bold & Italic
            },
            'CFF': {
                'Weight': 400,  # This value have to be fixed to 700
            }
        }
        fontdata = utils.fix_all_names(fontdata, 'Roboto')
        self.assertEqual(fontdata['OS/2']['usWeightClass'], 700)
        self.assertEqual(fontdata['CFF']['Weight'],
                         fontdata['OS/2']['usWeightClass'])
        self.assertEqual([
            [1, 'Roboto'],
            [2, 'Bold Italic'],
            [4, 'Roboto Bold Italic'],
            [6, 'Roboto-BoldItalic'],
            [16, 'Roboto'],
            [17, 'Bold Italic'],
            [18, 'Roboto Bold Italic']], [[x['nameID'], x['string']]
                                          for x in fontdata['names']])

    def test_suggest_name_testcase_light(self):

        fontdata = {
            'names': [
                {'nameID': 1, 'string': 'Roboto'},
            ],
            'OS/2': {
                'fsSelection': 0,  # Regular
                'usWeightClass': 300,  # Light
            },
            'head': {
                'macStyle': 0,  # Regular
            },
            'CFF': {
                'Weight': 400,  # This value have to be fixed to 300
            }
        }
        fontdata = utils.fix_all_names(fontdata, 'Roboto')
        self.assertEqual(fontdata['OS/2']['usWeightClass'], 300)
        self.assertEqual(fontdata['CFF']['Weight'],
                         fontdata['OS/2']['usWeightClass'])
        self.assertEqual([
            [1, 'Roboto Light'],
            [2, 'Regular'],
            [4, 'Roboto Light'],
            [6, 'Roboto-Light'],
            [16, 'Roboto'],
            [17, 'Light'],
            [18, 'Roboto Light']], [[x['nameID'], x['string']]
                                    for x in fontdata['names']])

    def test_suggest_name_testcase_light_italic(self):

        fontdata = {
            'names': [
                {'nameID': 1, 'string': 'Roboto'},
            ],
            'OS/2': {
                'fsSelection': 0b00001,  # Regular
                'usWeightClass': 300,  # Light
            },
            'head': {
                'macStyle': 0b10,  # Italic
            },
            'CFF': {
                'Weight': 400,  # This value have to be fixed to 300
            }
        }
        fontdata = utils.fix_all_names(fontdata, 'Roboto')
        self.assertEqual(fontdata['OS/2']['usWeightClass'], 300)
        self.assertEqual(fontdata['CFF']['Weight'],
                         fontdata['OS/2']['usWeightClass'])
        self.assertEqual([
            [1, 'Roboto Light'],
            [2, 'Italic'],
            [4, 'Roboto Light Italic'],
            [6, 'Roboto-LightItalic'],
            [16, 'Roboto'],
            [17, 'Light Italic'],
            [18, 'Roboto Light Italic']], [[x['nameID'], x['string']]
                                           for x in fontdata['names']])

    def test_suggest_name_testcase_light_bold(self):

        fontdata = {
            'names': [
                {'nameID': 1, 'string': 'Roboto'},
            ],
            'OS/2': {
                'fsSelection': 0b10000,  # Regular
                'usWeightClass': 700,  # Bold
            },
            'head': {
                'macStyle': 0b01,  # Italic
            },
            'CFF': {
                'Weight': 400,  # This value have to be fixed to 300
            }
        }
        fontdata = utils.fix_all_names(fontdata, 'Roboto')
        self.assertEqual(fontdata['OS/2']['usWeightClass'], 700)
        self.assertEqual(fontdata['CFF']['Weight'],
                         fontdata['OS/2']['usWeightClass'])
        self.assertEqual([
            [1, 'Roboto'],
            [2, 'Bold'],
            [4, 'Roboto Bold'],
            [6, 'Roboto-Bold'],
            [16, 'Roboto'],
            [17, 'Bold'],
            [18, 'Roboto Bold']], [[x['nameID'], x['string']]
                                   for x in fontdata['names']])

    def test_suggest_name_testcase_black(self):

        fontdata = {
            'names': [
                {'nameID': 1, 'string': 'Family'},
            ],
            'OS/2': {
                'fsSelection': 0b00000,  # Regular
                'usWeightClass': 900,  # Bold
            },
            'head': {
                'macStyle': 0b00,  # Italic
            },
            'CFF': {
                'Weight': 400,  # This value have to be fixed to 300
            }
        }
        fontdata = utils.fix_all_names(fontdata, 'Family')
        self.assertEqual(fontdata['OS/2']['usWeightClass'], 900)
        self.assertEqual(fontdata['CFF']['Weight'],
                         fontdata['OS/2']['usWeightClass'])
        self.assertEqual([
            [1, 'Family Black'],
            [2, 'Regular'],
            [4, 'Family Black'],
            [6, 'Family-Black'],
            [16, 'Family'],
            [17, 'Black'],
            [18, 'Family Black']], [[x['nameID'], x['string']]
                                    for x in fontdata['names']])
