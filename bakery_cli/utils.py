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

import sys
import defusedxml.lxml
import os
import os.path as op
import re
import unicodedata


def normalizestr(string):
    string = string.replace(u'©', '(c)')
    string = string.replace(u'®', '(r)')
    return unicodedata.normalize('NFKD', string).encode('ascii', 'ignore')


class RedisFd(object):
    """ Redis File Descriptor class, publish writen data to redis channel
        in parallel to file """
    def __init__(self, name, mode='a', write_pipeline=None):
        self.filed = open(name, mode)
        self.filed.write("Start: Start of log\n")  # end of log
        self.write_pipeline = write_pipeline
        if write_pipeline and not isinstance(write_pipeline, list):
            self.write_pipeline = [write_pipeline]

    def write(self, data, prefix=''):
        if self.write_pipeline:

            for pipeline in self.write_pipeline:
                data = pipeline(data)

        if not data.endswith('\n'):
            data += '\n'

        data = re.sub('\n{3,}', '\n\n', data)
        if data:
            self.filed.write("%s%s" % (prefix, data))
            self.filed.flush()

    def close(self):
        self.filed.write("End: End of log\n")  # end of log
        self.filed.close()


class UpstreamDirectory(object):
    """ Describes structure of upstream directory

    >>> upstream = UpstreamDirectory("tests/fixtures/upstream-example")
    >>> upstream.UFO
    ['Font-Regular.ufo']
    >>> upstream.TTX
    ['Font-Light.ttx']
    >>> upstream.BIN
    ['Font-SemiBold.ttf']
    >>> upstream.METADATA
    ['METADATA.json']
    >>> sorted(upstream.LICENSE)
    ['APACHE.txt', 'LICENSE.txt']
    >>> upstream.SFD
    ['Font-Bold.sfd']
    >>> sorted(upstream.TXT)
    ['APACHE.txt', 'LICENSE.txt']
    """

    OFL = ['open font license.markdown', 'ofl.txt', 'ofl.md']
    LICENSE = ['license.txt', 'license.md', 'copyright.txt']
    APACHE = ['apache.txt', 'apache.md']
    UFL = ['ufl.txt', 'ufl.md']

    ALL_LICENSES = OFL + LICENSE + APACHE + UFL

    def __init__(self, upstream_path):
        self.upstream_path = upstream_path

        self.UFO = []
        self.TTX = []
        self.BIN = []
        self.LICENSE = []
        self.METADATA = []
        self.SFD = []
        self.TXT = []

        self.walk()

    def get_ttx(self):
        return self.TTX

    def get_binaries(self):
        return self.BIN

    def get_fonts(self):
        return self.UFO + self.TTX + self.BIN + self.SFD
    ALL_FONTS = property(get_fonts)

    def walk(self):
        l = len(self.upstream_path)
        exclude = ['build_info', ]
        for root, dirs, files in os.walk(self.upstream_path, topdown=True):
            dirs[:] = [d for d in dirs if d not in exclude]
            for f in files:
                fullpath = op.join(root, f)

                if f[-4:].lower() == '.ttx':
                    try:
                        doc = defusedxml.lxml.parse(fullpath)
                        el = doc.xpath('//ttFont[@sfntVersion]')
                        if not el:
                            continue
                    except Exception as exc:
                        print('Failed to parse "{0}". '
                              'Error: {1}'.format(fullpath, exc),
                              file=sys.stderr)
                        continue
                    self.TTX.append(fullpath[l:].strip('/'))

                if op.basename(f).lower() == 'metadata.json':
                    self.METADATA.append(fullpath[l:].strip('/'))

                if f[-4:].lower() in ['.ttf', '.otf']:
                    self.BIN.append(fullpath[l:].strip('/'))

                if f[-4:].lower() == '.sfd':
                    self.SFD.append(fullpath[l:].strip('/'))

                if f[-4:].lower() in ['.txt', '.markdown', '.md', '.LICENSE']:
                    self.TXT.append(fullpath[l:].strip('/'))

                if op.basename(f).lower() in UpstreamDirectory.ALL_LICENSES:
                    self.LICENSE.append(fullpath[l:].strip('/'))

            for d in dirs:
                fullpath = op.join(root, d)
                if op.splitext(fullpath)[1].lower() == '.ufo':
                    self.UFO.append(fullpath[l:].strip('/'))


def nameTableRead(font, NameID, fallbackNameID=False):
    for record in font['name'].names:
        if record.nameID == NameID:
            if b'\000' in record.string:
                return record.string.decode('utf-16-be').encode('utf-8')
            else:
                return record.string

    if fallbackNameID:
        return nameTableRead(font, fallbackNameID)

    return ''


def get_data_directory():
    FONTBAKERY_DATA_DIRNAME = 'fontbakery'
    try:
        #Windows code:
        d = os.path.join(os.environ["FONTBAKERY_DATA_DIRNAME"],
                         FONTBAKERY_DATA_DIRNAME)
    except KeyError:
        #Linux and Mac code:
        d = os.path.join(os.path.expanduser("~"),
                         ".local", "share", FONTBAKERY_DATA_DIRNAME)
    if not os.path.exists(d):
        os.makedirs(d)
    return d
