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
import fontforge
import os.path as op

from cli.system import run, shutil


class Optimize(object):

    def __init__(self, bakery):
        self.project_root = bakery.project_root
        self.builddir = bakery.build_dir
        self.bakery = bakery

    def execute(self, pipedata):
        task = self.bakery.logging_task('Optimizing TTF')
        if self.bakery.forcerun:
            return

        try:
            for filename in pipedata['bin_files']:
                # convert the ttf to a ttx file - this may fail
                font = fontforge.open(op.join(self.builddir, filename))
                glyphs = []
                for g in font.glyphs():
                    if not g.codepoint:
                        continue
                    glyphs.append(g.codepoint)

                from fontTools import subset
                args = [op.join(self.builddir, filename)] + glyphs
                args += ['--layout-features="*"']
                subset.main(args)

                self.bakery.logging_cmd('pyftsubset %s' % ' '.join(args))

                # compare filesizes TODO print analysis of this :)
                comment = "# look at the size savings of that subset process"
                cmd = "ls -l '%s'* %s" % (filename, comment)
                run(cmd, cwd=self.builddir, log=self.bakery.log)

                # move ttx files to src
                shutil.move(op.join(self.builddir, filename + '.subset'),
                            op.join(self.builddir, filename),
                            log=self.bakery.log)
            self.bakery.logging_task_done(task)
        except:
            self.bakery.logging_task_done(task, failed=True)
            raise
