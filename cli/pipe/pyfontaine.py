import codecs
import os.path as op

from fontaine.cmap import Library
from fontaine.builder import Builder, Director


class PyFontaine(object):

    def __init__(self, bakery):
        self.project_root = bakery.project_root
        self.builddir = bakery.build_dir
        self.bakery = bakery

    def execute(self, pipedata):
        self.bakery.logging_task('pyFontaine TTFs')
        if self.bakery.forcerun:
            return

        library = Library(collections=['subsets'])
        director = Director(_library=library)

        fonts = []
        for font in pipedata['bin_files']:
            fonts.append(op.join(self.builddir, font))

        _ = ('fontaine --collections subsets --text %s'
             ' > sources/fontaine.txt\n') % ' '.join(fonts)
        self.bakery.logging_cmd(_)
        try:
            fontaine_log = op.join(self.builddir, 'sources', 'fontaine.txt')
            fp = codecs.open(fontaine_log, 'w', 'utf-8')
        except OSError:
            self.bakery.logging_err("Open fontaine log to write")
            return

        try:
            result = Builder.text_(director.construct_tree(fonts))
            fp.write(result.output)
        except:
            self.bakery.logging_err(('PyFontaine raised exception.'
                                     ' Check latest version.'))
            raise
