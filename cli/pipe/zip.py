import os
import os.path as op
import zipfile


class Zip(object):

    def __init__(self, bakery):
        self.project_root = bakery.project_root
        self.builds_root = bakery.builds_dir
        self.bakery = bakery

    def execute(self, pipedata, prefix=""):
        self.bakery.logging_task('ZIP result for download')
        if self.bakery.forcerun:
            return

        name = op.basename(self.bakery.build_dir)

        self.bakery.logging_cmd('zip -r {0}.zip {0}'.format(name))

        zipf = zipfile.ZipFile(op.join(self.builds_root, name + '.zip'), 'w')
        for root, dirs, files in os.walk(op.join(self.builds_root, name)):
            root = root.replace(op.join(self.builds_root, name), '').lstrip('/')
            for file in files:
                arcpath = op.join(name, root, file)
                self.bakery.logging_raw('add %s\n' % arcpath)
                zipf.write(op.join(self.builds_root, name, root, file), arcpath)
        zipf.close()

        pipedata['zip'] = '%s.zip' % name
