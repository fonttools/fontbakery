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

from fontaine.ext.subsets import Extension as SubsetExtension
from fontTools import ttLib

from bakery_cli.utils import re_range


def bin2unistring(string):
    if b'\000' in string:
        string = string.decode('utf-16-be')
        return string.encode('utf-8')
    else:
        return string


class PyFtSubset(object):

    def __init__(self, bakery):
        self.project_root = bakery.project_root
        self.builddir = bakery.build_dir
        self.bakery = bakery

    def execute_pyftsubset(self, pipedata, subsetname, name, glyphs="", args=""):
        from fontTools.subset import Subsetter, Options, load_font, save_font
        target_file = '{0}.{1}'.format(op.join(self.builddir, name)[:-4],
                                       subsetname)

        options = Options()
        cmd_options = ''
        if pipedata.get('pyftsubset'):
            cmd_options = pipedata['pyftsubset']
            options.parse_opts(pipedata['pyftsubset'].split())

        if pipedata.get('pyftsubset.%s' % subsetname):
            cmd_options = pipedata['pyftsubset.%s' % subsetname]
            options.parse_opts(pipedata['pyftsubset.%s' % subsetname].split())

        font = load_font(op.join(self.builddir, name), options)

        unicodes = re_range([int(g.replace('U+', ''), 16) for g in glyphs.split()])
        self.bakery.logging_cmd('pyftsubset --unicodes="{0}" {2} {1}'.format(unicodes, name,
                                                                             cmd_options))

        subsetter = Subsetter(options=options)
        subsetter.populate(unicodes=[int(g.replace('U+', ''), 16) for g in glyphs.split()])
        subsetter.subset(font)

        self.bakery.logging_cmd('mv {0}.subset {1}'.format(name, target_file))
        save_font(font, target_file, options)

    def execute(self, pipedata):
        self.bakery.logging_task('Subset TTFs (pyftsubset)')
        if self.bakery.forcerun:
            return

        for name in pipedata['bin_files']:
            self.run(name, pipedata)

    def run(self, name, pipedata):
        # create menu subset with glyph for text of family name
        if pipedata.get('pyftsubset') is False:
            return

        self.bakery.logging_raw('### Subset TTFs (pyftsubset) {}\n'.format(name))

        ttfont = ttLib.TTFont(op.join(self.builddir, name))
        L = map(lambda X: (X.nameID, X.string), ttfont['name'].names)
        D = dict(L)

        string = bin2unistring(D.get(16) or D.get(1))
        menu_glyphs = '\n'.join(['U+%04x' % ord(c) for c in string])

        for subset in pipedata.get('subset', []):
            glyphs = SubsetExtension.get_glyphs(subset)

            # The every subsets must include the "latin" subset
            if subset != 'latin':
                glyphs += '\n{}'.format(SubsetExtension.get_glyphs('latin'))
            self.execute_pyftsubset(pipedata, subset, name, glyphs=glyphs)

            # If any subset other than latin or latin-ext has been
            #   generated when the subsetting is done, this string should
            #   additionally include some characters corresponding to each
            #   of those subsets.
            G = SubsetExtension.get_glyphs(subset + '-menu')
            if G:
                menu_glyphs += '\n{}'.format(G)

        self.execute_pyftsubset(pipedata, 'menu', name, glyphs=menu_glyphs)

