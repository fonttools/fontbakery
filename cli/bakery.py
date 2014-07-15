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
import codecs
import os.path as op
import yaml

from checker import run_set
from cli.system import os, shutil, stdoutlog
from cli import pipe


BAKERY_CONFIGURATION_DEFAULTS = op.join(op.dirname(__file__), 'defaults.yaml')


def copy_single_file(src, dest, log):
    """ Copies single filename from src directory to dest directory """
    if op.exists(src) and op.isfile(src):
        shutil.copy(src, dest, log=log)


def bin2unistring(string):
    if b'\000' in string:
        string = string.decode('utf-16-be')
        return string.encode('utf-8')
    else:
        return string


class Bakery(object):
    """ Class to handle all parts of bakery process.

        Attributes:
            builddir: Path where to place baked fonts.
                If it does not exists object will create this one.
            config: Path to yaml file describing bake configuration.
                It has to be placed in the root of project directory.
            stdout_pipe: Optional attribute to make bakery process
                loggable.

                It is a class that must have defined `write` method. Eg:

                class stdlog:

                    @staticmethod
                    def write(msg, prefix=''):
                        pass
    """

    def __init__(self, config, project_root, builddir='build', stdout_pipe=stdoutlog):
        self.builddir = os.path.abspath(builddir)
        self.project_root = project_root
        self.stdout_pipe = stdout_pipe
        self.interactive = False
        self.errors_in_footer = []

        if isinstance(config, dict):
            self.config = config or {}
        else:
            self.config = self.load_config(config)

        self.state = {}
        self.state['autohinting_sizes'] = []

    def load_config(self, configfilepath):
        try:
            configfile = open(configfilepath, 'r')
        except OSError:
            configfile = open(BAKERY_CONFIGURATION_DEFAULTS, 'r')
            self.stdout_pipe.write(('Cannot read configuration file.'
                                    ' Using defaults'))
        return yaml.safe_load(configfile)

    def save_build_state(self):
        l = open(op.join(self.builddir, 'build.state.yaml'), 'w')
        l.write(yaml.safe_dump(self.state))
        l.close()

    def interactive():
        doc = "If True then user will be asked to apply autofix"

        def fget(self):
            return self._interactive

        def fset(self, value):
            self._interactive = value

        def fdel(self):
            del self._interactive

        return locals()
    interactive = property(**interactive())

    def run(self, with_upstream=False):

        pipes = [
            pipe.Copy,
            pipe.Build,
            pipe.FontLint,
            pipe.Optimize,
            pipe.AutoFix,
            pipe.CopyLicense,
            pipe.CopyFontLog,
            pipe.CopyDescription,
            pipe.CopyMetadata,
            pipe.CopyTxtFiles,
            pipe.TTFAutoHint,
            pipe.PyFtSubset,
            pipe.PyFontaine,
            pipe.Metadata
        ]

        for pipe_klass in pipes:
            p = pipe_klass(self.project_root, self.builddir, self.stdout_pipe)
            p.execute(self.config)

        self.save_build_state()

        return

    def upstream_tests(self):
        result = {}
        source_dir = op.join(self.builddir, 'sources')
        self.stdout_pipe.write('Run upstream tests\n', prefix='### ')

        result['/'] = run_set(source_dir, 'upstream-repo')
        for font in self.config.get('process_files', []):
            if font[-4:] in '.ttx':
                result[font] = run_set(op.join(source_dir, font),
                                       'upstream-ttx', log=self.stdout_pipe)
            else:
                result[font] = run_set(op.join(source_dir, font),
                                       'upstream', log=self.stdout_pipe)

        _out_yaml = op.join(source_dir, '.upstream.yaml')

        l = codecs.open(_out_yaml, mode='w', encoding="utf-8")
        l.write(yaml.safe_dump(result))
        l.close()
