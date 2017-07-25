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
from __future__ import print_function, unicode_literals
import argparse
import os
from fontTools import ttLib

description = 'Fixes TTF to have a dummy DSIG table'
parser = argparse.ArgumentParser(description=description)
parser.add_argument('ttf_font',
                    nargs='+',
                    help="One or more font files")
parser.add_argument('-a', '--autofix',
                    action='store_true',
                    help='Write empty DSIG table if not present in font.')

parser.add_argument('-f', '--force',
                    action='store_true',
                    help='Write empty DSIG table in any case.')

parser.add_argument('-d', '--delete',
                    action='store_true',
                    help='Delete DSIG table if present in font.')

def set_empty_dsig(ttFont):
  newDSIG = ttLib.newTable("DSIG")
  newDSIG.ulVersion = 1
  newDSIG.usFlag = 0
  newDSIG.usNumSigs = 0
  newDSIG.signatureRecords = []
  ttFont.tables["DSIG"] = newDSIG

def main():
  args = parser.parse_args()
  for path in args.ttf_font:
    if not os.path.exists(path):
      continue
    font = ttLib.TTFont(path)
    has_DSIG = "DSIG" in font
    write_DSIG = args.force or args.autofix and not has_DSIG

    if has_DSIG and args.delete:
      del font["DSIG"]
      font.save(path)
      has_DSIG = False
      print("DELETED: '{}': removed digital "
              "signature (DSIG)".format(path))

    if write_DSIG:
      set_empty_dsig(font)
      font.save(path)

      if not args.force:
        print("HOTFIX: '{}': Font lacked a digital"
              " signature (DSIG), so we just added a dummy"
              " placeholder that should be enough for the"
              " applications that require its presence in"
              " order to work properly.".format(path))
      else:
        print("FORCED: '{}': Font has a new a dummy digital "
              "signature (DSIG)".format(path))

    elif not has_DSIG and not args.delete:
      print(("ERROR: '{}': Font lacks a digital signature"
                 " (DSIG table). Some applications may required"
                 " one (even if only a dummy placeholder)"
                 " in order to work properly. Re-run this script"
                 " passing --autofix in order to hotfix the font"
                 " with a dummy signature.").format(path))
    elif has_DSIG:
      print(("INFO: '{}': Font has a digital signature"
                 " (DSIG table).").format(path))


if __name__ == '__main__':
  main()
