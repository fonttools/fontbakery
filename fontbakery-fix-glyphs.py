#!/usr/bin/env python2
# Copyright 2016 The Fontbakery Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from __future__ import unicode_literals
import argparse
import glyphsLib

args = argparse.ArgumentParser(
    description='Report issues on .glyphs font files')
args.add_argument('font', nargs="+")
#args.add_argument('--autofix', default=False,
#                  action='store_true', help='Apply autofix')

def customparam(data, name):
  for param in data['customParameters']:
    if param['name'] == name:
      return param['value']

if __name__ == '__main__':
  arg = args.parse_args()

  for font in arg.font:
    with open(font, 'rb') as glyphs_file:
      data = glyphsLib.load(glyphs_file)
      print('Copyright: "{}"'.format(data["copyright"]))
      print('VendorID: "{}"'.format(customparam(data, "vendorID")))
      print('fsType: {}'.format(customparam(data, "fsType")[0]))
      print('license: "{}"'.format(customparam(data, "license")))
      print('licenseURL: "{}"'.format(customparam(data, "licenseURL")))
  # TODO: handle these other fields:
  #
  # for master/instance in masters-or-instances:
  #   print: 8 Vertical Metrics
  #
  # Instance ExtraLight weightClass set to 275
  # Instances italicAngle set to 0, if the master/instance slant value is not 0
  # Instance named Regular (400) for families with a single instance
  # Instance Bold style linking set for families with a 400 and 700 instance





