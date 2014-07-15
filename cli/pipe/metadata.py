import os

from scripts import genmetadata
from cli.system import stdoutlog


class Metadata(object):

    def __init__(self, project_root, builddir, stdout_pipe=stdoutlog):
        self.project_root = project_root
        self.builddir = builddir
        self.stdout_pipe = stdout_pipe

    def execute(self, pipedata):
        self.stdout_pipe.write('Generate METADATA.json (genmetadata.py)\n',
                               prefix='### ')
        try:
            os.chdir(self.builddir)
            # reassign ansiprint to our own method
            genmetadata.ansiprint = self.ansiprint
            genmetadata.run(self.builddir)
        except Exception, e:
            self.stdout_pipe.write(e.message + '\n', prefix="### Error:")
            raise

    def ansiprint(self, message, color):
        self.stdout_pipe.write(message + '\n')
