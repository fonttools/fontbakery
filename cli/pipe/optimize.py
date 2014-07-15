import fontforge
import os.path as op

from cli.system import stdoutlog, run, shutil


class Optimize(object):

    def __init__(self, project_root, builddir, stdout_pipe=stdoutlog):
        self.project_root = project_root
        self.builddir = builddir
        self.stdout_pipe = stdout_pipe

    def execute(self, pipedata):
        self.stdout_pipe.write('Optimizing TTF', prefix='### ')

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

            self.stdout_pipe.write('$ pyftsubset %s' % ' '.join(args))

            # compare filesizes TODO print analysis of this :)
            comment = "# look at the size savings of that subset process"
            cmd = "ls -l '%s'* %s" % (filename, comment)
            run(cmd, cwd=self.builddir, log=self.stdout_pipe)

            # move ttx files to src
            shutil.move(op.join(self.builddir, filename + '.subset'),
                        op.join(self.builddir, filename),
                        log=self.stdout_pipe)
