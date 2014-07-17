import os
import os.path as op

from cli.system import shutil, stdoutlog
from fontaine.ext.subsets import Extension as SubsetExtension
from fontTools import ttLib


def bin2unistring(string):
    if b'\000' in string:
        string = string.decode('utf-16-be')
        return string.encode('utf-8')
    else:
        return string


class PyFtSubset(object):

    def __init__(self, project_root, builddir, stdout_pipe=stdoutlog):
        self.stdout_pipe = stdout_pipe
        self.project_root = project_root
        self.builddir = builddir

    def execute_pyftsubset(self, pipedata, subsetname, name, glyphs="", args=""):
        from fontTools import subset
        argv = [op.join(self.builddir, name)] + glyphs.split()
        # argv += ['--notdef-outline', '--name-IDs="*"', '--hinting']

        override_argv = []
        if pipedata.get('pyftsubset'):
            override_argv = pipedata['pyftsubset'].split()

        if pipedata.get('pyftsubset.%s' % subsetname):
            override_argv = pipedata['pyftsubset.%s' % subsetname].split()

        argv = argv + override_argv
        subset.main(argv)

        self.stdout_pipe.write('$ pyftsubset %s' % ' '.join(argv))

        # need to move result .subset file to avoid overwrite with
        # next subset
        shutil.move(op.join(self.builddir, name) + '.subset',
                    op.join(self.builddir, name)[:-4] + '.' + subsetname,
                    log=self.stdout_pipe)

    def execute(self, pipedata):
        self.stdout_pipe.write('Subset TTFs (pyftsubset)\n', prefix='### ')

        os.chdir(op.join(self.builddir, 'sources'))
        for name in pipedata['bin_files']:
            # create menu subset with glyph for text of family name
            ttfont = ttLib.TTFont(op.join(self.builddir, name))
            L = map(lambda X: (X.nameID, X.string), ttfont['name'].names)
            D = dict(L)

            string = bin2unistring(D.get(16) or D.get(1))
            menu_glyphs = ['U+%04x' % ord(c) for c in string]

            for subset in pipedata.get('subset', []):
                glyphs = SubsetExtension.get_glyphs(subset)

                # The Devanagari subset must include the latin unicode set too
                if subset == 'devanagari':
                    G = SubsetExtension.get_glyphs('latin')
                    glyphs += ' ' + ' '.join(G.split())
                self.execute_pyftsubset(pipedata, subset, name, glyphs=glyphs)

                # If any subset other than latin or latin-ext has been
                #   generated when the subsetting is done, this string should
                #   additionally include some characters corresponding to each
                #   of those subsets.
                G = SubsetExtension.get_glyphs(subset + '-menu')
                if G:
                    menu_glyphs += G.split()

            self.execute_pyftsubset(pipedata, 'menu', name,
                                    glyphs='\n'.join(menu_glyphs))
