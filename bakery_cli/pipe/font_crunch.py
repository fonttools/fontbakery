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
import fnmatch
import os

from fontcrunch import fontcrunch

from bakery_cli.utils import shutil


class FontCrunch(object):

    def __init__(self, bakery):
        self.project_root = bakery.project_root
        self.builddir = bakery.build_dir
        self.bakery = bakery

    def run(self, pipedata):
        if not pipedata.get('fontcrunch'):
            return  # run fontcrunch only if user set flag in config

        from bakery_cli.utils import ProcessedFile
        filename = ProcessedFile()
        
        filename = os.path.join(self.builddir, filename)
        self.bakery.logging_raw('### Fontcrunch {}\n'.format(filename))

        fontcrunch.optimize(filename, '{}.crunched'.format(filename))
        shutil.move('{}.crunched'.format(filename), filename)
        return 1

    def execute(self, pipedata):
        if not pipedata.get('fontcrunch'):
            return  # run fontcrunch only if user set flag in config

        self.bakery.logging_task('Fontcrunch TTF')
        if self.bakery.forcerun:
            return

        for filename in [os.path.join(self.builddir, x) \
                         for x in pipedata['bin_files']]:
            self.run(filename, pipedata)
