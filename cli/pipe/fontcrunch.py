import fontforge
import os.path as op

from cli.system import run, shutil


class FontCrunch(object):

    def __init__(self, bakery):
        self.project_root = bakery.project_root
        self.builddir = bakery.build_dir
        self.bakery = bakery

    def execute(self, pipedata):
        task = self.bakery.logging_task('Foncrunching TTF')
        if self.bakery.forcerun:
            return

        try:
            for filename in pipedata['bin_files']:
                # convert the ttf to a ttx file - this may fail
                font = fontforge.open(op.join(self.builddir, filename))

            self.bakery.logging_task_done(task)
        except:
            self.bakery.logging_task_done(task, failed=True)
            raise
