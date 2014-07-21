import os.path as op

from cli.system import stdoutlog, run, shutil as shellutil


class TTFAutoHint(object):

    def __init__(self, project_root, builddir, stdout_pipe=stdoutlog):
        self.stdout_pipe = stdout_pipe
        self.project_root = project_root
        self.builddir = builddir

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
        self.stdout_pipe.write('Autohint TTFs (ttfautohint)\n', prefix='### %s ' % prefix)
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
                run(cmd, cwd=self.builddir, log=self.stdout_pipe)
            except:
                self.stdout_pipe.write('TTFAutoHint is not available\n',
                                       prefix="### Error:")
                break
            pipedata['autohinting_sizes'].append({
                'fontname': op.basename(filepath),
                'origin': op.getsize(filepath),
                'processed': op.getsize(filepath[:-4] + '.autohint.ttf')
            })
            # compare filesizes TODO print analysis of this :)
            comment = "# look at the size savings of that subset process"
            cmd = "ls -l %s.*ttf %s" % (filepath[:-4], comment)
            run(cmd, cwd=self.builddir, log=self.stdout_pipe)
            shellutil.move(filepath[:-4] + '.autohint.ttf', filepath,
                           log=self.stdout_pipe)

        return pipedata
