# coding: utf-8
# Copyright 2013 The Font Bakery Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# See AUTHORS.txt for the list of Authors and LICENSE.txt for the License.
import glob
import multiprocessing
import os
import os.path as op
import shutil


from bakery_cli.utils import shutil as shellutil
from bakery_cli.logger import logger


def copy_single_file(src, dest):
    """ Copies single filename from src directory to dest directory """
    if op.exists(src) and op.isfile(src):
        shellutil.copy(src, dest)
        return True


class Pipe(object):

    def __init__(self, bakery):
        self.project_root = bakery.project_root
        self.builddir = bakery.build_dir
        self.bakery = bakery

    def execute(self, pipedata, prefix=""):

        if op.exists(op.join(self.project_root, self.filename)):
            try:
                args = [op.join(self.project_root, self.filename),
                        self.builddir]
                copy_single_file(op.join(self.project_root, self.filename),
                                 self.builddir)
            except:
                logger.debug('Unable to copy files')
                raise

        return pipedata


def taskcopy(k, pipedata):
    k.execute(pipedata)


class Copy(Pipe):

    def lookup_splitted_ttx(self, fontpath):
        rootpath = op.dirname(fontpath)
        fontname = op.basename(fontpath)
        splitted_ttx_paths = []

        srcpath = op.join(self.project_root, rootpath,
                          '%s.*.ttx' % fontname[:-4])

        l = len(self.project_root)
        for path in glob.glob(srcpath):
            splitted_ttx_paths.append(path[l:].strip('/'))
        return splitted_ttx_paths

    def copy_to_builddir(self, process_files, destdir):
        args = ' '.join(process_files + [destdir])
        self.bakery.logging_cmd('cp -a %s' % args)

        for path in process_files:
            path = op.join(self.project_root, path)
            if op.isdir(path):
                if op.exists(op.join(destdir, op.basename(path))):
                    shutil.rmtree(op.join(destdir, op.basename(path)))
                shutil.copytree(path, op.join(destdir, op.basename(path)))
            else:
                if op.exists(op.join(destdir, op.basename(path))):
                    os.unlink(op.join(destdir, op.basename(path)))
                shutil.copy(path, destdir)

    def create_source_dir(self):
        source_dir = op.join(self.builddir, 'sources')
        if not op.exists(source_dir):
            os.makedirs(source_dir)
        return source_dir

    def copy_helper_files(self, pipedata):
        pipechain = [CopyMetadata, CopyLicense, CopyDescription, CopyFontLog,
                     CopyTxtFiles, CopyCopyright]

        for klass in pipechain:
            k = klass(self.bakery)
            p = multiprocessing.Process(target=taskcopy, args=(k, pipedata, ))
            p.start()

    def execute(self, pipedata):
        task = self.bakery.logging_task('Copy sources')
        if self.bakery.forcerun:
            return pipedata

        source_dir = self.create_source_dir()

        if pipedata.get('compiler') == 'make':
            makefile = op.join(self.project_root, 'Makefile')
            shutil.copy(makefile, source_dir)

        self.copy_helper_files(pipedata)

        try:
            if pipedata.get('compiler') != 'make':
                process_files = list(pipedata.get('process_files', []))

                paths_to_copy = list(pipedata.get('process_files', []))
                for path in process_files:
                    paths_to_copy += self.lookup_splitted_ttx(path)

                self.copy_to_builddir(paths_to_copy, source_dir)

                sources = []
                for path in process_files:
                    filename = op.basename(path)
                    sources.append(op.join(source_dir, filename))

                pipedata.update({'process_files': sources})
            else:
                for root, dirs, files in os.walk(self.project_root):
                    if root.startswith(self.builddir.rstrip('/')):
                        continue

                    # ignore git repo
                    if op.basename(root) in ['.git']:
                        continue

                    d = op.join(source_dir, root.replace(self.project_root, '').strip('/'))
                    if not op.exists(d):
                        os.makedirs(d)

                    for f in files:
                        shutil.copy(op.join(root, f), op.join(d, f))

        except Exception as ex:
            logger.debug('Unable process copy. Exception info: %s' % ex)
            raise

        return pipedata


class CopyLicense(Pipe):

    supported_licenses = ['OFL.txt', 'UFL.txt', 'APACHE.txt', 'LICENSE.txt']

    def execute(self, pipedata):
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

            try:
                shellutil.copy(_in_license, _out_license)
            except:
                pass
        else:
            # In case no license_file in bakery.yaml fontbakery-build will
            #  search for supported licenses and copy first from list.
            #  See: CopyLicense.supported_licenses attribute
            for lic in self.supported_licenses:
                src = op.join(self.project_root, lic)
                dest = op.join(self.builddir, lic)
                if os.path.exists(src):
                    shellutil.copy(src, dest)
                    pipedata['license_file'] = lic
                    break
        return pipedata


class CopyDescription(Pipe):

    filename = 'DESCRIPTION.en_us.html'


class CopyCopyright(Pipe):

    filename = 'COPYRIGHT.txt'


class CopyTxtFiles(Pipe):

    def execute(self, pipedata, prefix=""):
        if not pipedata.get('txt_files_copied'):
            return pipedata

        try:
            paths = []
            for filename in pipedata['txt_files_copied']:
                paths.append(op.join(self.project_root, filename))
                shutil.copy(op.join(self.project_root, filename),
                            self.builddir)

            args = paths + [self.builddir]
            self.bakery.logging_cmd('cp -a %s' % ' '.join(args))
        except:
            raise
        return pipedata


class CopyFontLog(Pipe):

    filename = 'FONTLOG.txt'


class CopyMetadata(Pipe):

    filename = 'METADATA.json'
