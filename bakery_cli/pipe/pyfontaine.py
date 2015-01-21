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
import codecs
import os.path as op

from fontaine.cmap import Library
from fontaine.builder import Builder, Director

from bakery_cli.utils import UpstreamDirectory


def targettask(pyfontaine, pipedata, task):
    try:
        library = Library(collections=['subsets'])
        director = Director(_library=library)

        sourcedir = op.join(pyfontaine.builddir)
        directory = UpstreamDirectory(sourcedir)

        fonts = []
        for font in directory.ALL_FONTS:
            if font.startswith('sources'):
                continue
            fonts.append(op.join(pyfontaine.builddir, font))

        _ = ('fontaine --collections subsets --text %s'
             ' > fontaine.txt\n') % ' '.join(fonts)
        pyfontaine.bakery.logging_cmd(_)

        fontaine_log = op.join(pyfontaine.builddir, 'fontaine.txt')
        fp = codecs.open(fontaine_log, 'w', 'utf-8')

        result = Builder.text_(director.construct_tree(fonts))
        fp.write(result.output)
        pyfontaine.bakery.logging_raw('end of pyfontaine process\n')
    except Exception as ex:
        pyfontaine.bakery.logging_raw('pyfontaine error: {}'.format(ex))
        pyfontaine.bakery.logging_raw('pyfontaine process has been failed\n')


class PyFontaine(object):

    def __init__(self, bakery):
        self.project_root = bakery.project_root
        self.builddir = bakery.build_dir
        self.bakery = bakery

    def execute(self, pipedata):
        task = self.bakery.logging_task('pyfontaine')
        if self.bakery.forcerun:
            return

        targettask(self, pipedata, task)
