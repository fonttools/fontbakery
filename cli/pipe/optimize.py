import fontforge
import os.path as op

from cli.system import run, shutil


class Optimize(object):

    def __init__(self, bakery):
        self.project_root = bakery.project_root
        self.builddir = bakery.build_dir
        self.bakery = bakery

    def execute(self, pipedata):
        self.bakery.logging_task('Optimizing TTF')
        if self.bakery.forcerun:
            return

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

            self.bakery.logging_cmd('pyftsubset %s' % ' '.join(args))

            # compare filesizes TODO print analysis of this :)
            comment = "# look at the size savings of that subset process"
            cmd = "ls -l '%s'* %s" % (filename, comment)
            run(cmd, cwd=self.builddir, log=self.bakery.log)

            # move ttx files to src
            shutil.move(op.join(self.builddir, filename + '.subset'),
                        op.join(self.builddir, filename),
                        log=self.bakery.log)
