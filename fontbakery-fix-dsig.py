#!/usr/bin/env python
# coding: utf-8
# Copyright 2013,2016 The Font Bakery Authors.
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
from fontTools import ttLib

description = 'Fixes TTF to have a dummy DSIG table'
parser = argparse.ArgumentParser(description=description)
parser.add_argument('ttf_font',
                    nargs='+',
                    help="One or more font files")
parser.add_argument('--autofix',
                    action='store_true',
                    help='Apply autofix')


def main():
  args = parser.parse_args()
  for path in args.ttf_font:
    if not os.path.exists(path):
      continue
    font = ttLib.TTFont(path)
    if "DSIG" not in font:
      try:
        if args.autofix:
          from fontTools.ttLib.tables.D_S_I_G_ import SignatureRecord
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
          font.tables["DSIG"] = newDSIG
          font.save(path)
          print(("HOTFIX: '{}': The font lacks a digital"
                 " signature (DSIG), so we just added a dummy"
                 " placeholder that should be enough for the"
                 " applications that require its presence in"
                 " order to work properly.").format(path))
        else:
          print(("ERROR: '{}': This font lacks a digital signature"
                 " (DSIG table). Some applications may required"
                 " one (even if only a dummy placeholder)"
                 " in order to work properly. Re-run this script"
                 " passing --autofix in order to hotfix the font"
                 " with a dummy signature.").format(path))

      except ImportError:
        error_message = ("ERROR '{}': The font lacks a"
                         " digital signature (DSIG), so OpenType features"
                         " will not be available in some applications that"
                         " use its presense as a (stupid) heuristic."
                         " So we need to add one. But for that we'll need "
                         "Fonttools v2.3+ so you need to upgrade it. Try:"
                         " $ pip install --upgrade fontTools; or see"
                         " https://pypi.python.org/pypi/FontTools")
        print (error_message.format(path))

if __name__ == '__main__':
  main()
