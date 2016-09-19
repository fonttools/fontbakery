#!/usr/bin/env python
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
import argparse
import os
from bakery_cli.fixers import CreateDSIGFixer

class CreateDSIGFixer(Fixer):
    """ Create DSIG table in font if it does not exist """

    def get_shell_command(self):
        return "fontbakery-fix-dsig.py {}".format(self.fontpath)

    def fix(self):
        if 'DSIG' in self.font:
            return False

        try:
            from fontTools.ttLib.tables.D_S_I_G_ import SignatureRecord
        except ImportError:
            error_message = ("The '{}' font does not have an existing"
                             " digital signature proving its authenticity,"
                             " so Fontbakery needs to add one. To do this"
                             " requires version 2.3 or later of Fonttools"
                             " to be installed. Please upgrade at"
                             " https://pypi.python.org/pypi/FontTools/2.4")
            logger.error(error_message.format(os.path.basename(self.fontpath)))
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




if __name__ == '__main__':
    description = 'Fixes TTF to have a dummy DSIG table'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('ttf_font', nargs='+',
                        help="Font where to create DSIG table inside")
    parser.add_argument('--autofix', action='store_true', help='Apply autofix')

    args = parser.parse_args()

    for path in args.ttf_font:
        if not os.path.exists(path):
            continue
        CreateDSIGFixer(None, path).apply()



