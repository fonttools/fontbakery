import os.path as op

from cli.system import run, shutil as shellutil


class TTFAutoHint(object):

    def __init__(self, bakery):
        self.project_root = bakery.project_root
        self.builddir = bakery.build_dir
        self.bakery = bakery

    def execute(self, pipedata, prefix=""):
        """ Run ttfautohint with project command line settings

        For each ttf file in result src folder, outputting them in
        the _out root, or just copy the ttfs there.
        """
        # $ ttfautohint -l 7 -r 28 -G 0 -x 13 -w "" \
        #               -W -c original_font.ttf final_font.ttf
        params = pipedata.get('ttfautohint', '')
        if not params:
            return pipedata

        self.bakery.logging_task('Autohint TTFs (ttfautohint)')

        if self.bakery.forcerun:
            return

        if 'autohinting_sizes' not in pipedata:
            pipedata['autohinting_sizes'] = []

        for filepath in pipedata['bin_files']:
            filepath = op.join(self.project_root,
                               self.builddir, filepath)
            cmd = ("ttfautohint {params} {source}"
                   " '{name}.autohint.ttf'").format(params=params.strip(),
                                                    name=filepath[:-4],
                                                    source=filepath)
            try:
                run(cmd, cwd=self.builddir, log=self.bakery.log)
            except:
                self.bakery.logging_err('TTFAutoHint is not available')
                break
            pipedata['autohinting_sizes'].append({
                'fontname': op.basename(filepath),
                'origin': op.getsize(filepath),
                'processed': op.getsize(filepath[:-4] + '.autohint.ttf')
            })
            # compare filesizes TODO print analysis of this :)
            comment = "# look at the size savings of that subset process"
            cmd = "ls -l %s.*ttf %s" % (filepath[:-4], comment)
            run(cmd, cwd=self.builddir, log=self.bakery.log)
            shellutil.move(filepath[:-4] + '.autohint.ttf', filepath,
                           log=self.bakery.log)

        return pipedata
