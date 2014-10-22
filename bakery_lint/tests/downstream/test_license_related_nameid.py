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
import os

from bakery_lint.base import BakeryTestCase as TestCase, autofix
from fontTools import ttLib


def getNameRecordValue(nameRecord):
    if nameRecord.isUnicode():
        return nameRecord.string.decode('utf-16-be')
    return nameRecord.string


class TestNameIdCopyright(TestCase):

    targets = ['result']
    name = __name__
    tool = 'lint'

    # Collection of namerecords that will be removed from table `name`
    namerecords = []

    def containsSubstr(self, nameRecord, substr):
        return substr in getNameRecordValue(nameRecord)

    @autofix('bakery_cli.pipe.autofix.remove_description_with_substr')
    def test_name_id_copyright(self):
        """ Is there `opyright` substring nameID in nameId (10) ? """
        font = ttLib.TTFont(self.operator.path)
        self.namerecords = [f for f in font['name'].names
                            if self.containsSubstr(f, 'opyright') and f.nameID == 10]
        self.assertFalse(bool(self.namerecords))


class TestNameIdOFLLicense(TestCase):

    targets = ['result']
    name = __name__
    tool = 'lint'

    @autofix('bakery_cli.pipe.autofix.replace_license_with_short')
    def test_name_id_of_license(self):
        """ Is there OFL in nameId (13) ? """
        path = os.path.join(os.path.dirname(__file__), '..', 'licenses', 'OFL.license')
        text = open(path).read()

        placeholderPath = os.path.join(os.path.dirname(__file__), '..', 'licenses', 'OFL.placeholder')
        self.placeholderText = open(placeholderPath).read()

        fontLicensePath = os.path.join(os.path.dirname(self.operator.path), 'OFL.txt')

        font = ttLib.TTFont(self.operator.path)
        for nameRecord in font['name'].names:
            if nameRecord.nameID == 13:
                value = getNameRecordValue(nameRecord)
                self.assertFalse(value != self.placeholderText and os.path.exists(fontLicensePath),
                    u'License file OFL.txt exists but NameID value is not specified for that')
                self.assertFalse(text in value)


class TestNameIdOFLLicenseURL(TestCase):

    targets = ['result']
    name = __name__
    tool = 'lint'

    @autofix('bakery_cli.pipe.autofix.replace_licenseurl')
    def test_name_id_of_license_url(self):
        """ Is there OFL in nameId (13) ? """
        path = os.path.join(os.path.dirname(__file__), '..', 'licenses', 'OFL.license')
        text = open(path).read()

        placeholderPath = os.path.join(os.path.dirname(__file__), '..', 'licenses', 'OFL.placeholder')
        placeholderText = open(placeholderPath).read()

        placeholderUrlPath = os.path.join(os.path.dirname(__file__), '..', 'licenses', 'OFL.url')
        self.placeholderUrlText = open(placeholderUrlPath).read()

        fontLicensePath = os.path.join(os.path.dirname(self.operator.path), 'OFL.txt')

        font = ttLib.TTFont(self.operator.path)

        isLicense = False

        licenseUrlNameRecord = None
        for nameRecord in font['name'].names:
            if nameRecord.nameID == 13:
                value = getNameRecordValue(nameRecord)
                isLicense = os.path.exists(fontLicensePath) or text in value
            if nameRecord.nameID == 14:
                licenseUrlNameRecord = nameRecord

        self.assertFalse(isLicense and getNameRecordValue(licenseUrlNameRecord) != self.placeholderUrlText)


class TestNameIdApacheLicense(TestCase):

    targets = ['result']
    name = __name__
    tool = 'lint'

    @autofix('bakery_cli.pipe.autofix.replace_license_with_short')
    def test_name_id_apache_license(self):
        """ Is there Apache in nameId (13) ? """
        path = os.path.join(os.path.dirname(__file__), '..', 'licenses', 'APACHE.license')
        text = open(path).read()

        placeholderPath = os.path.join(os.path.dirname(__file__), '..', 'licenses', 'APACHE.placeholder')
        self.placeholderText = open(placeholderPath).read()

        fontLicensePath = os.path.join(os.path.dirname(self.operator.path), 'LICENSE.txt')

        font = ttLib.TTFont(self.operator.path)
        for nameRecord in font['name'].names:
            if nameRecord.nameID == 13:
                value = getNameRecordValue(nameRecord)
                self.assertFalse(value != self.placeholderText and os.path.exists(fontLicensePath),
                    u'License file LICENSE.txt exists but NameID value is not specified for that')
                self.assertFalse(text in value)


class TestNameIdApacheLicenseURL(TestCase):

    targets = ['result']
    name = __name__
    tool = 'lint'

    @autofix('bakery_cli.pipe.autofix.replace_licenseurl')
    def test_name_id_apache_license_url(self):
        """ Is there OFL in nameId (13) ? """
        path = os.path.join(os.path.dirname(__file__), '..', 'licenses', 'APACHE.license')
        text = open(path).read()

        placeholderPath = os.path.join(os.path.dirname(__file__), '..', 'licenses', 'APACHE.placeholder')
        placeholderText = open(placeholderPath).read()

        placeholderUrlPath = os.path.join(os.path.dirname(__file__), '..', 'licenses', 'APACHE.url')
        self.placeholderUrlText = open(placeholderUrlPath).read()

        fontLicensePath = os.path.join(os.path.dirname(self.operator.path), 'LICENSE.txt')

        font = ttLib.TTFont(self.operator.path)

        isLicense = False

        licenseUrlNameRecord = None
        for nameRecord in font['name'].names:
            if nameRecord.nameID == 13:
                value = getNameRecordValue(nameRecord)
                isLicense = os.path.exists(fontLicensePath) or text in value
            if nameRecord.nameID == 14:
                licenseUrlNameRecord = nameRecord

        self.assertFalse(isLicense and getNameRecordValue(licenseUrlNameRecord) != self.placeholderUrlText)
