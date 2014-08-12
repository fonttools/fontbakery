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

import lxml.etree
from StringIO import StringIO
import requests
import sys


def main():
    families = ['Ek Mukta', 'Hind', 'Teko', 'Kalam', 'Karma', 'Rajdhani',
                'Khand', 'Vesper Libre']

    r = requests.get('http://www.google.com/fonts/stats?key=WebFonts2010')
    if r.status_code != 200:
        print("Wrong download code", file=sys.stderr)
        sys.exit(1)

    parser = lxml.etree.HTMLParser()
    doc = lxml.etree.parse(StringIO(r.text), parser)

    total = 0
    for i, family in enumerate(families):
        el = doc.xpath('//div[contains(text(),"%s")]/..' % family)
        try:
            value = int(el[0][4].text.replace(',', ''))
            families[i] = (family, value)
            total = total + value
        except IndexError:
            print('ERROR: %s could not be found in stat' % family, sys.stderr)

    families.append(('TOTAL', total))
    return families


if __name__ == '__main__':
    print(main())
