import os
import os.path as op

from cli.system import prun, shutil as shellutil
from fontTools import ttx
from scripts.font2ttf import convert


class Build(object):

    def __init__(self, bakery):
        self.project_root = bakery.project_root
        self.builddir = bakery.build_dir
        self.bakery = bakery

    def otf2ttf(self, filepath):
        fontname = filepath[:-4]

        _ = 'font2ttf.py {0}.otf {0}.ttf\n'
        self.bakery.logging_cmd(_.format(fontname))

        path = '{}.otf'.format(fontname)
        if op.exists(op.join(self.builddir, path)):
            try:
                ttfpath = '{}.ttf'.format(fontname)
                convert(op.join(self.builddir, path),
                        op.join(self.builddir, ttfpath), log=self.bakery.log)
                os.remove(op.join(self.builddir, path))
            except Exception, ex:
                self.bakery.logging_err(ex.message)
                raise

    def movebin_to_builddir(self, files):
        result = []
        for a in files:
            d = op.join(self.builddir, op.basename(a)[:-4] + '.ttf')
            s = op.join(self.builddir, a[:-4] + '.ttf')

            shellutil.move(s, d, log=self.bakery.log)
            result.append(op.basename(a)[:-4] + '.ttf')
        return result

    def execute(self, pipedata, prefix=""):
        task = self.bakery.logging_task('Convert sources to TTF')
        if self.bakery.forcerun:
            return

        ttxfiles = []
        ufo = []
        sfd = []
        bin = []
        for p in pipedata['process_files']:
            if p.endswith('.ttx'):
                ttxfiles.append(p)
            elif p.endswith('.sfd'):
                sfd.append(p)
            elif p.endswith('.ufo'):
                ufo.append(p)
            elif p.endswith('.ttf'):
                bin.append(p)
            elif p.endswith('.otf'):
                bin.append(p)

        try:
            if ttxfiles:
                self.execute_ttx(ttxfiles)
            if ufo:
                self.execute_ufo_sfd(ufo)
            if sfd:
                self.execute_ufo_sfd(sfd)
            if bin:
                self.execute_bin(bin)

            binfiles = self.movebin_to_builddir(ufo + ttxfiles + sfd + bin)

            SCRIPTPATH = op.join('scripts', 'vmet.py')
            command = ' '.join(map(lambda x: op.join(self.builddir, x), binfiles))
            prun('python %s %s' % (SCRIPTPATH, command),
                 cwd=op.abspath(op.join(op.dirname(__file__), '..', '..')),
                 log=self.bakery.log)

            pipedata['bin_files'] = binfiles
        except:
            self.bakery.logging_task_done(task, failed=True)
            raise

        self.bakery.logging_task_done(task)
        return pipedata

    def execute_ttx(self, files):
        paths = []
        for f in files:
            f = op.join(self.builddir, f)
            paths.append(f)

        self.bakery.logging_cmd('ttx %s' % ' '.join(paths))
        ttx.main(paths)

        for p in files:
            self.otf2ttf(p)

    def execute_ufo_sfd(self, files):
        for f in files:
            filepath = op.join(self.builddir, f)
            _ = 'font2ttf.py %s %s'
            self.bakery.logging_cmd(_ % (filepath,
                                         filepath[:-4] + '.ttf'))
            ttfpath = filepath[:-4] + '.ttf'

            try:
                convert(op.join(self.builddir, filepath),
                        op.join(self.builddir, ttfpath), log=self.stdout_pipe)
            except Exception, ex:
                self.bakery.logging_err(ex.message)
                raise

    def execute_bin(self, files):
        for p in files:
            if p.endswith('.otf'):
                self.otf2ttf(p)
