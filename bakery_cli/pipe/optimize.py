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

from bakery_cli.utils import shutil, run, UpstreamDirectory


class Optimize(object):
    """ Run optimization process for font """

    def __init__(self, bakery):
        self.project_root = bakery.project_root
        self.builddir = bakery.build_dir
        self.bakery = bakery

    def execute(self, pipedata):
        self.bakery.logging_task('Optimizing TTF')
        if self.bakery.forcerun:
            return

        for filename in UpstreamDirectory(self.builddir).BIN:
            self.run(op.join(self.builddir, filename), pipedata)

    def run(self, filename, pipedata):
        if 'optimize' in pipedata and not pipedata['optimize']:
            return

        self.bakery.logging_raw('### Optimize TTF {}'.format(filename))
        # copied from https://code.google.com/p/noto/source/browse/nototools/subset.py
        from fontTools.subset import Options, Subsetter, load_font, save_font

        options = Options()
        options.layout_features = ["*"]
        options.name_IDs = ["*"]
        options.hinting = True
        options.legacy_kern = True
        options.notdef_outline = True
        options.no_subset_tables += ['DSIG']
        options.drop_tables = list(set(options._drop_tables_default) - set(['DSIG']))

        cmd_options = ('--glyphs=*'
                       ' --layout-features=*'
                       ' --name-IDs=*'
                       ' --hinting'
                       ' --legacy-kern --notdef-outline'
                       ' --no-subset-tables+=DSIG'
                       ' --drop-tables-=DSIG')

        font = load_font(op.join(self.builddir, filename), options)

        cmdline = 'pyftsubset {1} {0}'.format(cmd_options, op.join(self.builddir, filename))
        self.bakery.logging_cmd(cmdline)

        subsetter = Subsetter(options=options)
        subsetter.populate(glyphs=font.getGlyphOrder())
        subsetter.subset(font)
        save_font(font, op.join(self.builddir, filename + '.fix'), options)

        # compare filesizes TODO print analysis of this :)
        comment = "# look at the size savings of that subset process"
        self.bakery.logging_cmd(comment)
        run("ls -la {0} {0}.fix | awk '{{ print $5 \"\t\" $9 }}'".format(op.join(self.builddir, filename)))

        comment = "# copy back optimized ttf to original filename"
        self.bakery.logging_cmd(comment)
        shutil.move(op.join(self.builddir, filename + '.fix'),
                    op.join(self.builddir, filename))
