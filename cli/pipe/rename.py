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
import os.path as op
import re

from cli.system import shutil
from cli.utils import nameTableRead
from fontTools import ttLib


class Rename(object):

    def __init__(self, bakery):
        self.project_root = bakery.project_root
        self.builddir = bakery.build_dir
        self.bakery = bakery

    def execute(self, pipedata):
        if self.bakery.forcerun:
            return

        rename_executed = False
        newfiles = []
        task = None
        for i, filepath in enumerate(pipedata['bin_files']):
            path = op.join(self.builddir, filepath)

            font = ttLib.TTFont(path)

            psname = self.get_psname(font)
            if psname:
                if op.basename(path) != psname:
                    if not rename_executed:
                        msg = 'Rename built files with PS Naming'
                        task = self.bakery.logging_task(msg)
                        rename_executed = True
                    try:
                        shutil.move(path, op.join(op.dirname(path), psname),
                                    log=self.bakery.log)
                    except:
                        if task:
                            self.bakery.logging_task_done(task, failed=True)
                        raise
                newfiles.append(filepath.replace(op.basename(filepath), psname))
            else:
                newfiles.append(filepath)

        if task:
            self.bakery.logging_task_done(task)
        pipedata['bin_files'] = newfiles
        return pipedata

    def get_psname(self, ttfont):
        stylename = re.sub(r'\s', '', self.get_style(ttfont))
        familyname = re.sub(r'\s', '', self.get_family(ttfont))
        return "{}-{}.ttf".format(familyname, stylename)

    def get_style(self, ttfont):
        # Find the style name
        style_name = nameTableRead(ttfont, 17, 2)
        # Always have a regular style
        if style_name == 'Normal' or style_name == 'Roman':
            style_name = 'Regular'
        return style_name

    def get_family(self, ttfont):
        return nameTableRead(ttfont, 16, 1)
