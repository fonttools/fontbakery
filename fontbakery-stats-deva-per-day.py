#!/usr/bin/python
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
from __future__ import print_function

import argparse
from lxml.html import HTMLParser
import defusedxml.lxml
from StringIO import StringIO
import requests
import sys

default_url = "http://www.google.com/fonts"
description = "Script to list font views per day of devanagari families."
parser = argparse.ArgumentParser(description=description)
parser.add_argument('url',
                    nargs='?',
                    default=default_url,
                    help=('font repository url'
                          ' (default = "{}")').format(default_url))


def main():
    args = parser.parse_args()

    families = [
      'Ek Mukta',
      'Hind',
      'Teko',
      'Kalam',
      'Karma',
      'Rajdhani',
      'Khand',
      'Vesper Libre',
      # this has a lot of views already from just latin
      # 'Glegoo',
      'Halant',
      'Laila',
      'Palanquin',
      'Rozha One',
      'Sarpanch'
      ]

    r = requests.get(args.url)
    if r.status_code != 200:
        print("Wrong download code", file=sys.stderr)
        sys.exit(1)

    doc = defusedxml.lxml.parse(StringIO(r.text), HTMLParser())

    total = 0
    for i, family in enumerate(families):
        el = doc.xpath('//div[contains(text(),"%s")]/..' % family)
        try:
            value = int(el[0][4].text.replace(',', ''))
            families[i] = (family, value)
            total += value
        except IndexError:
            print('ERROR: %s could not be found in stat' % family, file=sys.stderr)

    families.append(('TOTAL', total))
    return families


if __name__ == '__main__':
    print(main())
