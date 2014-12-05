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
from fontTools import ttLib
from fontTools.ttLib.tables.D_S_I_G_ import SignatureRecord

from bakery_cli.ttfont import Font
from bakery_cli.utils import normalizestr


class Fixer(object):

    def __init__(self, fontpath):
        self.font = ttLib.TTFont(fontpath)
        self.fixfont_path = '{}.fix'.format(fontpath)

    def fix(self):
        """ Make a concrete fix for the font.

        Implemented in inherited classes.

        Returns:
            :bool: false if fixes will not be saved into new file

        """
        raise NotImplementedError

    def apply(self):
        if not self.fix():
            return
        self.font.save(self.fixfont_path)


class SpecCharsForASCIIFixer(Fixer):
    """ Converts special characters like copyright, trademark signs to ascii
    name """

    def fix(self):
        for name in self.font['name'].names:
            title = Font.bin2unistring(name)
            title = normalizestr(title)
            if name.platformID == 3:
                name.string = title.encode('utf-16-be')
            else:
                name.string = title
        return True


class CreateDSIGFixer(Fixer):
    """ Create DSIG table in font if it does not exist """

    def fix(self):
        if 'DSIG' in self.font:
            return False
        newDSIG = ttLib.newTable("DSIG")
        newDSIG.ulVersion = 1
        newDSIG.usFlag = 1
        newDSIG.usNumSigs = 1
        sig = SignatureRecord()
        sig.ulLength = 20
        sig.cbSignature = 12
        sig.usReserved2 = 0
        sig.usReserved1 = 0
        sig.pkcs7 = '\xd3M4\xd3M5\xd3M4\xd3M4'
        sig.ulFormat = 1
        sig.ulOffset = 20
        newDSIG.signatureRecords = [sig]
        self.font.tables["DSIG"] = newDSIG
        return True
