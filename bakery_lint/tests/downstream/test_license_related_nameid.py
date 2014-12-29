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
from bakery_cli.fixers import ReplaceOFLLicenseURL, ReplaceApacheLicenseURL, \
    ReplaceOFLLicenseWithShortLine, ReplaceApacheLicenseWithShortLine
from fontTools import ttLib


def getNameRecordValue(nameRecord):
    if nameRecord.isUnicode():
        return nameRecord.string.decode('utf-16-be')
    return nameRecord.string


class TestNameIdCopyright(TestCase):

    targets = ['result']
    name = __name__
    tool = 'lint'

    def containsSubstr(self, nameRecord, substr):
        return substr in getNameRecordValue(nameRecord)

    @autofix('bakery_cli.fixers.RemoveNameRecordWithOpyright')
    def test_name_id_copyright(self):
        """ Is there `opyright` substring nameID in nameId (10) ? """
        font = ttLib.TTFont(self.operator.path)
        records = [f for f in font['name'].names
                   if self.containsSubstr(f, 'opyright') and f.nameID == 10]
        self.assertFalse(bool(records))


class TestNameIdOFLLicense(TestCase):

    targets = ['result']
    name = __name__
    tool = 'lint'

    @autofix('bakery_cli.fixers.ReplaceOFLLicenseWithShortLine')
    def test_name_id_of_license(self):
        """ Is there OFL in nameId (13) ? """
        fixer = ReplaceOFLLicenseWithShortLine(self.operator.path)

        placeholder = fixer.get_placeholder()

        path = os.path.join(os.path.dirname(self.operator.path), 'OFL.txt')
        licenseexists = os.path.exists(path)

        for nameRecord in fixer.font['name'].names:
            if nameRecord.nameID == 13:
                value = getNameRecordValue(nameRecord)
                if value != placeholder and licenseexists:
                    self.fail('License file OFL.txt exists but NameID'
                              ' value is not specified for that.')


class TestNameIdOFLLicenseURL(TestCase):

    targets = ['result']
    name = __name__
    tool = 'lint'

    @autofix('bakery_cli.fixers.ReplaceOFLLicenseURL')
    def test_name_id_of_license_url(self):
        """ Is there OFL in nameId (13) ? """
        fixer = ReplaceOFLLicenseURL(self.operator.path)

        text = open(fixer.get_licensecontent_filename()).read()

        fontLicensePath = os.path.join(os.path.dirname(self.operator.path),
                                       'OFL.txt')

        isLicense = False

        for nameRecord in fixer.font['name'].names:
            if nameRecord.nameID == 13:  # check license nameID only
                value = getNameRecordValue(nameRecord)
                isLicense = os.path.exists(fontLicensePath) or text in value

        self.assertFalse(isLicense and bool(fixer.validate()))


class TestNameIdApacheLicense(TestCase):

    targets = ['result']
    name = __name__
    tool = 'lint'

    @autofix('bakery_cli.fixers.ReplaceApacheLicenseWithShortLine')
    def test_name_id_apache_license(self):
        """ Is there Apache in nameId (13) ? """
        fixer = ReplaceApacheLicenseWithShortLine(self.operator.path)

        placeholder = fixer.get_placeholder()

        path = os.path.join(os.path.dirname(self.operator.path), 'LICENSE.txt')
        licenseexists = os.path.exists(path)

        for nameRecord in fixer.font['name'].names:
            if nameRecord.nameID == 13:
                value = getNameRecordValue(nameRecord)
                if value != placeholder and licenseexists:
                    self.fail('License file LICENSE.txt exists but NameID'
                              ' value is not specified for that.')


class TestNameIdApacheLicenseURL(TestCase):

    targets = ['result']
    name = __name__
    tool = 'lint'

    @autofix('bakery_cli.fixers.ReplaceApacheLicenseURL')
    def test_name_id_apache_license_url(self):
        """ Is there OFL in nameId (13) ? """
        fixer = ReplaceApacheLicenseURL(self.operator.path)

        text = open(fixer.get_licensecontent_filename()).read()

        fontLicensePath = os.path.join(os.path.dirname(self.operator.path),
                                       'LICENSE.txt')

        isLicense = False

        for nameRecord in fixer.font['name'].names:
            if nameRecord.nameID == 13:  # check license nameID only
                value = getNameRecordValue(nameRecord)
                isLicense = os.path.exists(fontLicensePath) or text in value

        self.assertFalse(isLicense and bool(fixer.validate()))
