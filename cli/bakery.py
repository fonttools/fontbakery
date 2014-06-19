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
import os
import os.path as op

from cli.source import get_fontsource


class Bakery(object):
    """ Go through all baking process, from copying to optimizing
        resulted ttf files """

    def __init__(self, builddir='build', config={}, stdout_pipe=None):
        self.builddir = builddir
        self.config = config
        self.stdout_pipe = stdout_pipe

    def prepare_sources(self, path):
        fontsource = get_fontsource(op.basename(path),
                                    op.dirname(path), self.stdout_pipe)
        fontsource.family_name = self.config.get('familyname', '')

        if not fontsource.before_copy():
            return

        build_source_dir = op.join(self.builddir, 'sources')
        if not op.exists(build_source_dir):
            os.makedirs(build_source_dir)

        fontsource.copy(build_source_dir)

        fontsource.after_copy(self.builddir)
        return fontsource

    def run(self, files):
        if not isinstance(files, list):
            files = [files]

        for path in files:
            self.prepare_sources(path)

