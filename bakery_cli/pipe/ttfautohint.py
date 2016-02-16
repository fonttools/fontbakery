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

from bakery_cli.utils import run, shutil, ttfautohint_installed


class TTFAutoHint(object):

    def __init__(self, bakery):
        self.project_root = bakery.project_root
        self.builddir = bakery.build_dir
        self.bakery = bakery

    def run(self, pipedata):
        if not pipedata.get('ttfautohint', '') or not ttfautohint_installed():
            return False

        from bakery_cli.utils import ProcessedFile
        filepath = ProcessedFile()

        self.bakery.logging_raw('### Autohint TTFs (ttfautohint) {}\n'.format(filepath))

        params = pipedata['ttfautohint']
        filepath = op.join(self.project_root, self.builddir, filepath)
        cmd = ("ttfautohint {params} {name}"
               " '{name}.fix'").format(params=params.strip(),
                                       name=filepath)
        try:
            run(cmd, cwd=self.builddir)
        except:
            return False

        if 'autohinting_sizes' not in pipedata:
            pipedata['autohinting_sizes'] = []

        origsize = op.getsize(filepath)
        autohintsize = op.getsize(filepath + '.fix')

        pipedata['autohinting_sizes'].append({
            'fontname': op.basename(filepath),
            'origin': origsize,
            'processed': autohintsize
        })
        # compare filesizes TODO print analysis of this :)
        comment = "# look at the size savings of that subset process"

        run("ls -la {0} {0}.fix | awk '{{ print $5 \"\t\" $9 }}'".format(filepath))

        comment = "# copy back optimized ttf to original filename"
        self.bakery.logging_cmd(comment)

        shutil.move(filepath + '.fix', filepath)
        return 1

    def execute(self, pipedata, prefix=""):
        """ Run ttfautohint with project command line settings

        For each ttf file in result src folder, outputting them in
        the _out root, or just copy the ttfs there.
        """
        # $ ttfautohint -l 7 -r 28 -G 50 -x 13 -w "G" \
        #               -I original_font.ttf final_font.ttf
        params = pipedata.get('ttfautohint', '')
        if not params:
            return pipedata

        self.bakery.logging_task('Autohint TTFs (ttfautohint)')

        if self.bakery.forcerun:
            return

        for filepath in pipedata['bin_files']:
            if not self.run(filepath, pipedata):
                break

        return pipedata
