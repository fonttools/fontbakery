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

from fontTools import ttx

from bakery_cli.scripts.font2ttf import convert
from bakery_cli.utils import shutil as shellutil, run
from bakery_cli.utils import UpstreamDirectory


class Build(object):

    def __init__(self, bakery):
        self.project_root = bakery.project_root
        self.builddir = bakery.build_dir
        self.bakery = bakery

    def otf2ttf(self, filepath, pipedata):
        fontname = filepath[:-4]

        ttfpath = '{}.ttf'.format(op.basename(fontname))

        path = '{}.otf'.format(op.basename(fontname))

        if op.exists(op.join(self.builddir, 'sources', path)):
            _ = 'fontbakery-build-font2ttf.py {0}.otf {1}\n'
            self.bakery.logging_cmd(_.format(fontname, ttfpath))
            try:
                convert(op.join(self.builddir, 'sources', path),
                        op.join(self.builddir, 'sources', ttfpath),
                        log=self.bakery.logger)
                os.remove(op.join(self.builddir, 'sources', path))
            except Exception as ex:
                self.bakery.logging_err(ex.message)
                raise

        shellutil.move(op.join(self.builddir, 'sources', ttfpath),
                       op.join(self.builddir, ttfpath),
                       log=self.bakery.logger)
        self.run_processes(ttfpath, pipedata)

    def movebin_to_builddir(self, files):
        result = []
        for a in files:
            d = op.join(self.builddir, op.basename(a)[:-4] + '.ttf')
            s = op.join(self.builddir, a[:-4] + '.ttf')

            try:
                shellutil.move(s, d, log=self.bakery.logger)
                result.append(op.basename(a)[:-4] + '.ttf')
            except:
                pass
        return result

    def print_vertical_metrics(self, binfiles):
        from bakery_cli.scripts import vmet
        fonts = [op.join(self.builddir, x) for x in binfiles]
        self.bakery.logging_raw(vmet.metricview(fonts))

    def convert(self, pipedata):
        directory = UpstreamDirectory(op.join(self.builddir, 'sources'))
        try:
            if directory.BIN:
                self.execute_bin([x for x in directory.BIN], pipedata)
            if directory.get_ttx():
                self.execute_ttx([op.join('sources', x) for x in directory.get_ttx()], pipedata)
            if directory.UFO:
                self.execute_ufo_sfd([op.join('sources', x) for x in directory.UFO], pipedata)
            if directory.SFD:
                self.execute_ufo_sfd([op.join('sources', x) for x in directory.SFD], pipedata)

            # binfiles = self.movebin_to_builddir([op.join('sources', x) for x in directory.ALL_FONTS])

            # self.print_vertical_metrics(binfiles)

            # pipedata['bin_files'] = binfiles
        except:
            raise

    def execute(self, pipedata, prefix=""):
        task = self.bakery.logging_task('Convert sources to TTF')
        if self.bakery.forcerun:
            return

        if pipedata.get('compiler') == 'make':
            import subprocess
            directory = UpstreamDirectory(op.join(self.builddir, 'sources'))
            snapshot_bin = directory.BIN

            process = subprocess.Popen(['make'], cwd=op.join(self.builddir, 'sources'))
            process.communicate()

            directory = UpstreamDirectory(op.join(self.builddir, 'sources'))
            snapshot_after_bin = directory.BIN

            for fontpath in set(snapshot_bin) ^ set(snapshot_after_bin):
                if fontpath.lower().endswith('.ttf'):
                    os.copy(op.join(self.builddir, 'sources', fontpath), self.builddir)
                    self.run_processes(op.basename(fontpath), pipedata)

            return pipedata

        self.convert(pipedata)

        return pipedata

    def run_processes(self, filename, pipedata):
        from bakery_cli.pipe.fontlint import FontLint
        from bakery_cli.pipe.pyftsubset import PyFtSubset
        from bakery_cli.pipe.optimize import Optimize
        from bakery_cli.pipe.ttfautohint import TTFAutoHint
        from bakery_cli.pipe.font_crunch import FontCrunch

        fontlint = FontLint(self.bakery)
        fontlint.run(filename, pipedata)

        optimize = Optimize(self.bakery)
        optimize.run(filename, pipedata)

        ttfautohint = TTFAutoHint(self.bakery)
        ttfautohint.run(filename, pipedata)

        pyftsubset = PyFtSubset(self.bakery)
        pyftsubset.run(filename, pipedata)

        fontcrunch = FontCrunch(self.bakery)
        fontcrunch.run(filename, pipedata)

    def execute_ttx(self, files, pipedata):
        paths = []
        for f in files:
            f = op.join(self.builddir, f)
            paths.append(f)

        self.bakery.logging_cmd('ttx {}'.format(' '.join(paths)))
        ttx.main(paths)

        for p in files:
            self.otf2ttf(p, pipedata)

    def execute_ufo_sfd(self, files, pipedata):
        _ = 'fontbakery-build-font2ttf.py %s %s'

        for filepath in files:
            ttfpath = os.path.basename(filepath)[:-4] + '.ttf'

            try:
                if self.bakery.config.get('compiler') == 'afdko':
                    import time
                    starttime = time.time()
                    command = 'makeotf -f {0} {1} -o {2}.otf'.format(op.join(self.builddir, filepath),
                                                                     self.bakery.config.get('afdko', ''),
                                                                     op.join(self.builddir, filepath)[:-4])
                    self.bakery.logging_cmd(op.join(self.builddir, op.dirname(filepath)))
                    run(command, op.join(self.builddir, op.dirname(filepath)),
                        self.bakery.logger)
                    elapsedtime = time.time() - starttime
                    self.bakery.logging_raw('Time elapsed: {}'.format(elapsedtime))
                    self.otf2ttf('{}.otf'.format(filepath[:-4]), pipedata)
                else:
                    self.bakery.logging_cmd(_ % (filepath, ttfpath))
                    convert(op.join(self.builddir, filepath),
                            op.join(self.builddir, ttfpath), log=self.bakery.logger)
                    self.run_processes(op.basename(ttfpath), pipedata)
            except Exception as ex:
                self.bakery.logging_err(ex.message)
                raise

    def execute_bin(self, files, pipedata):
        for p in files:
            if p.endswith('.otf'):
                self.otf2ttf(p, pipedata)
