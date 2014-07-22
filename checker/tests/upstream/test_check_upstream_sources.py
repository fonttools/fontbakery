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
import glob
import os
import re

from checker.base import BakeryTestCase as TestCase, tags


class ProjectUpstreamTestCase(TestCase):
    """ Common tests for upstream repository.

    .. note::

    This test case is not related to font processing. It makes only common
    checks like one - test that upstream repository contains bakery.yaml) """

    targets = ['upstream-repo']
    tool = 'FontBakery'
    path = '.'
    name = __name__

    @tags('note')
    def test_bakery_yaml_exists(self):
        """ Repository does contain bakery.yaml configuration file """
        self.assertTrue(os.path.exists(os.path.join(self.path, 'bakery.yaml')),
                        msg=('File `bakery.yaml` does not exist in root '
                             'of upstream repository'))

    @tags('note')
    def test_fontlog_txt_exists(self):
        """ Repository does contain bakery.yaml configuration file """
        self.assertTrue(os.path.exists(os.path.join(self.path, 'FONTLOG.txt')),
                        msg=('File `FONTLOG.txt` does not exist in root '
                             'of upstream repository'))

    @tags('note')
    def test_description_html_exists(self):
        """ Repository does contain bakery.yaml configuration file """
        self.assertTrue(os.path.exists(os.path.join(self.path, 'DESCRIPTION.en_us.html')),
                        msg=('File `DESCRIPTION.en_us.html` does not exist in root '
                             'of upstream repository'))

    @tags('note')
    def test_metadata_json_exists(self):
        """ Repository does contain bakery.yaml configuration file """
        self.assertTrue(os.path.exists(os.path.join(self.path, 'METADATA.json')),
                        msg=('File `METADATA.json` does not exist in root '
                             'of upstream repository'))

    def test_copyright_notices_same_across_family(self):
        """ Are all copyright notices the same in all styles? """
        ufo_dirs = []
        for root, dirs, files in os.walk(self.path):
            for d in dirs:
                fullpath = os.path.join(root, d)
                if os.path.splitext(fullpath)[1].lower() == '.ufo':
                    ufo_dirs.append(fullpath)

        copyright = None
        for ufo_folder in ufo_dirs:
            current_notice = self.lookup_copyright_notice(ufo_folder)
            if current_notice is None:
                continue
            if copyright is not None and current_notice != copyright:
                self.fail('"%s" != "%s"' % (current_notice, copyright))
                break
            copyright = current_notice

    def grep_copyright_notice(self, contents):
        match = COPYRIGHT_REGEX.search(contents)
        if match:
            return match.group(0).strip(',\r\n')
        return

    def lookup_copyright_notice(self, ufo_folder):
        current_path = ufo_folder
        try:
            contents = open(os.path.join(ufo_folder, 'fontinfo.plist')).read()
            copyright = self.grep_copyright_notice(contents)
            if copyright:
                return copyright
        except (IOError, OSError):
            pass

        while os.path.realpath(self.path) != current_path:
            # look for all text files inside folder
            # read contents from them and compare with copyright notice
            # pattern
            files = glob.glob(os.path.join(current_path, '*.txt'))
            files += glob.glob(os.path.join(current_path, '*.ttx'))
            for filename in files:
                with open(os.path.join(current_path, filename)) as fp:
                    match = COPYRIGHT_REGEX.search(fp.read())
                    if not match:
                        continue
                    return match.group(0).strip(',\r\n')
            current_path = os.path.join(current_path, '..')  # go up
            current_path = os.path.realpath(current_path)
        return


COPYRIGHT_REGEX = re.compile(r'Copyright.*?20\d{2}.*', re.U | re.I)
