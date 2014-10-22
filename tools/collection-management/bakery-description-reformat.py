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
from tidylib import tidy_document
import nltk.data
import lxml.etree as etree


def reformat_contents(path):
    placeholder = '[LINEBREAK]'

    try:
        doc = etree.fromstring(open(path).read(), parser=etree.HTMLParser())
    except IOError:
        return ''

    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

    for node in doc.xpath('//*'):
        if not node.text:
            continue

        node.text = placeholder.join(sent_detector.tokenize(node.text.strip()))

    doc = etree.tostring(doc, pretty_print=True)
    doc, _ = tidy_document(doc, {'show-body-only': True, 'indent-cdata': '0'})
    return doc.replace(placeholder, '\n')


if __name__ == '__main__':
    try:
        contents = reformat_contents('DESCRIPTION.en_us.html')
        print(contents, file=open('DESCRIPTION.en_us.html', 'w'))
    except IOError:
        pass
