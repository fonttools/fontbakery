import os

from scripts import genmetadata


class Metadata(object):

    def __init__(self, bakery):
        self.project_root = bakery.project_root
        self.builddir = bakery.build_dir
        self.bakery = bakery

    def execute(self, pipedata, prefix=""):
        self.bakery.logging_task('Generate METADATA.json (genmetadata.py)')
        if self.bakery.forcerun:
            return
        try:
            os.chdir(self.builddir)
            # reassign ansiprint to our own method
            genmetadata.ansiprint = self.ansiprint
            genmetadata.run(self.builddir)
        except Exception, e:
            self.bakery.logging_err(e.message)
            raise

    def ansiprint(self, message, color):
        self.bakery.logging_raw(message + '\n')
