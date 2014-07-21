import glob
import os
import os.path as op
import shutil

from cli.system import stdoutlog, shutil as shellutil


def copy_single_file(src, dest, log):
    """ Copies single filename from src directory to dest directory """
    if op.exists(src) and op.isfile(src):
        shellutil.copy(src, dest, log=log)
        return True


class Pipe(object):

    def __init__(self, project_root, builddir, stdout_pipe=stdoutlog):
        self.stdout_pipe = stdout_pipe
        self.project_root = project_root
        self.builddir = builddir

    def execute(self, pipedata, prefix=""):
        if copy_single_file(op.join(self.project_root, self.filename),
                            self.builddir, self.stdout_pipe):
            self.stdout_pipe.write('Copy %s' % self.filename, prefix='### %s ' % prefix)

        return pipedata


class Copy(Pipe):

    def lookup_splitted_ttx(self, fontpath):
        rootpath = op.dirname(fontpath)
        fontname = op.basename(fontpath)
        splitted_ttx_paths = []
        for path in glob.glob(op.join(self.project_root, rootpath, '%s.*.ttx' % fontname[:-4])):
            splitted_ttx_paths.append(op.join(rootpath, path))
        return splitted_ttx_paths

    def copy_to_builddir(self, process_files):
        build_source_dir = op.join(self.builddir, 'sources')
        if not op.exists(build_source_dir):
            os.makedirs(build_source_dir)

        args = ' '.join(process_files + [build_source_dir])
        self.stdout_pipe.write('$ cp -a %s\n' % args)

        for path in process_files:
            path = op.join(self.project_root, path)
            if op.isdir(path):
                shutil.copytree(path, op.join(build_source_dir, op.basename(path)))
            else:
                shutil.copy(path, build_source_dir)

        return 'sources'

    def execute(self, pipedata, prefix=""):
        self.stdout_pipe.write('Copying sources\n', prefix='### %s ' % prefix)

        process_files = list(pipedata.get('process_files', []))

        paths_to_copy = list(pipedata.get('process_files', []))
        for path in process_files:
            paths_to_copy += self.lookup_splitted_ttx(path)

        build_source_dir = self.copy_to_builddir(paths_to_copy)

        sources = []
        for path in process_files:
            filename = op.basename(path)
            sources.append(op.join(build_source_dir, filename))

        pipedata.update({'process_files': sources})

        return pipedata


class CopyLicense(Pipe):

    def execute(self, pipedata, prefix=""):
        self.stdout_pipe.write('Copy license file', prefix='### %s ' % prefix)
        if pipedata.get('license_file', None):
            # Set _in license file name
            license_file_in_full_path = pipedata['license_file']
            license_file_in = license_file_in_full_path.split('/')[-1]
            # List posible OFL and Apache filesnames
            list_of_ofl_filenames = ['Open Font License.markdown', 'OFL.txt',
                                     'OFL.md']
            listOfApacheFilenames = ['APACHE.txt', 'LICENSE']
            # Canonicalize _out license file name
            if license_file_in in list_of_ofl_filenames:
                license_file_out = 'OFL.txt'
            elif license_file_in in listOfApacheFilenames:
                license_file_out = 'LICENSE.txt'
            else:
                license_file_out = license_file_in
            # Copy license file
            _in_license = op.join(self.project_root, license_file_in_full_path)
            _out_license = op.join(self.builddir, license_file_out)

            shellutil.copy(_in_license, _out_license, log=self.stdout_pipe)
        else:
            self.stdout_pipe.write('License file not copied\n',
                                   prefix='Error: ')
        return pipedata


class CopyDescription(Pipe):

    filename = 'DESCRIPTION.en_US.html'


class CopyTxtFiles(Pipe):

    def execute(self, pipedata, prefix=""):
        if pipedata.get('txt_files_copied', None):
            self.stdout_pipe.write('Copy txt files', prefix='### %s ' % prefix)
            paths = []
            for filename in pipedata['txt_files_copied']:
                paths.append(op.join(self.project_root, filename))
                shutil.copy(op.join(self.project_root, filename),
                            self.builddir)

            args = paths + [self.builddir]
            self.stdout_pipe.write('$ cp -a %s' % ' '.join(args))
        return pipedata


class CopyFontLog(Pipe):

    filename = 'FONTLOG.txt'


class CopyMetadata(Pipe):

    filename = 'METADATA.json'


