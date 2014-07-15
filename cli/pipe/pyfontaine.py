import codecs
import os.path as op

from cli.system import stdoutlog
from fontaine.cmap import Library
from fontaine.builder import Builder, Director


class PyFontaine(object):

    def __init__(self, project_root, builddir, stdout_pipe=stdoutlog):
        self.project_root = project_root
        self.builddir = builddir
        self.stdout_pipe = stdout_pipe

    def execute(self, pipedata):
        self.stdout_pipe.write('pyFontaine TTFs\n', prefix='### ')

        library = Library(collections=['subsets'])
        director = Director(_library=library)

        fonts = []
        for font in pipedata['bin_files']:
            fonts.append(op.join(self.builddir, font))

        _ = ('fontaine --collections subsets --text %s'
             ' > sources/fontaine.txt\n') % ' '.join(fonts)
        self.stdout_pipe.write(_, prefix='$ ')
        try:
            fontaine_log = op.join(self.builddir, 'sources', 'fontaine.txt')
            fp = codecs.open(fontaine_log, 'w', 'utf-8')
        except OSError:
            self.stdout_pipe.write("Failed to open fontaine log to write")
            return

        try:
            result = Builder.text_(director.construct_tree(fonts))
            fp.write(result.output)
        except:
            self.stdout_pipe.write(('PyFontaine raised exception.'
                                    ' Check latest version.\n'))
            raise
