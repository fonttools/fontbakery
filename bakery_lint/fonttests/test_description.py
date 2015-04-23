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
import defusedxml.lxml
import requests

from lxml.html import HTMLParser

from bakery_lint.base import BakeryTestCase as TestCase, TestCaseOperator


class TestDescription404Links(TestCase):

    targets = ['description']
    tool = 'FontBakery'
    name = __name__

    def test_broken_links(self):
        """ Check if DESCRIPTION do not have broken links """
        try:
            contents = open(self.operator.path).read()
        except:
            self.fail('File {} does not exist'.format(self.operator.path))
        doc = defusedxml.lxml.fromstring(contents, parser=HTMLParser())
        for link in doc.xpath('//a/@href'):
            try:
                response = requests.head(link)
                self.assertEqual(response.status_code, requests.codes.ok,
                                 msg='%s is broken' % link)
            except requests.exceptions.RequestException as ex:
                self.fail('%s raises exception [%r]' % (link, ex))


def get_suite(path):
    suite = unittest.TestSuite()
    TestDescription404Links.operator = TestCaseOperator(path)
    for test in unittest.defaultTestLoader.loadTestsFromTestCase(TestDescription404Links):
        suite.addTest(test)
    return suite