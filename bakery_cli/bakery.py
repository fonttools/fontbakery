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
import logging
import os
import os.path as op
import yaml

from bakery_cli import pipe
from bakery_cli.utils import shutil


class BakeryTaskSet(object):

    def create_task(self, message):
        pass

    def close_task(self, task, failed=False):
        pass


BAKERY_CONFIGURATION_DEFAULTS = op.join(op.dirname(__file__),
                                        'bakery.defaults.yaml')
BAKERY_CONFIGURATION_NEW = op.join(op.dirname(__file__), 'bakery.new.yaml')


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


class WhitespaceRemovingFormatter(logging.Formatter):
    def format(self, record):
        import re
        record.msg = re.sub('\s+', ' ', record.msg.strip())
        return super(WhitespaceRemovingFormatter, self).format(record)


class Bakery(object):
    """ Class to handle all parts of bakery process.

    Attributes:

        root: Absolute path of directory where user project placed
        project_dir: Project directory name (eg. 12.in)
        build_dir: Build directory name (eg. 21.abcdef)
        builds_dir: Builds directory name (eg. 12.out)

    All arguments will be appended to `root`. Eg:

    >>> b = Bakery("/home/user", "projectclone", build_dir="build",
    ...            builds_dir="out")
    >>> b.build_dir
    '/home/user/out/build'
    >>> b.project_root
    '/home/user/projectclone'
    >>> b.builds_dir
    '/home/user/out'
    """

    def __init__(self, root, project_dir, builds_dir='', build_dir='build'):
        self.rootpath = op.abspath(root)

        self.build_dir = op.join(self.rootpath, builds_dir, build_dir)

        self.project_root = op.join(self.rootpath, project_dir)
        self.builds_dir = op.join(self.rootpath, builds_dir)

        self.taskset = BakeryTaskSet()

        self.pipes = [
            pipe.Copy,
            pipe.UpstreamLint,
            pipe.Build,
            pipe.Metadata,
            pipe.MetadataLint,
            pipe.PyFontaine
        ]

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # create formatter
        formatter = WhitespaceRemovingFormatter('%(message)s')

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        self.logger.addHandler(ch)

        # chf = logging.FileHandler(op.join(self.build_dir, 'buildlog.txt'))
        # chf.setFormatter(formatter)
        # chf.setLevel(logging.DEBUG)
        # self.logger.addHandler(chf)

    def init_taskset(self, taskset):
        """ Defines object to use TaskSet interface. Default: BakeryTaskSet

        TaskSet must have 2 implemented functions

        - create_task(): Task
        - close_task(task: Task, status: Boolean)
        """
        self.taskset = taskset

    def load_config(self, config):
        """ Loading settings from yaml bake configuration. """
        if isinstance(config, dict):
            self.config = config or {}
        else:
            try:
                configfile = open(config, 'r')
            except OSError:
                configfile = open(BAKERY_CONFIGURATION_DEFAULTS, 'r')
                self.logger.error(('Cannot read configuration file.'
                                   ' Using defaults'))
            self.config = yaml.safe_load(configfile)

    def save_build_state(self):
        l = open(op.join(self.rootpath, self.builds_dir, self.build_dir, 'build.state.yaml'), 'w')
        l.write(yaml.safe_dump(self.config))
        l.close()

    _interactive = False

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

    def run(self):
        if not os.path.exists(self.build_dir):
            os.makedirs(self.build_dir)
        else:
            index = 1
            b = self.build_dir
            while os.path.exists(b + '.' + str(index)):
                index += 1
            self.build_dir = b + '.' + str(index)
            os.makedirs(self.build_dir)

        self.logging_raw('\n\n\n# Bake Begins!\n')

        # run in force mode to auto count available tasks
        self.force_run(self.pipes)

        return self.normal_run(self.pipes)

    forcerun = False

    def force_run(self, pipes):
        self.forcerun = True
        for pipe_klass in pipes:
            try:
                p = pipe_klass(self)
                p.execute(self.config)
            except:
                self.save_build_state()
                raise

        return self.config

    def normal_run(self, pipes):

        self.forcerun = False
        for i, pipe_klass in enumerate(pipes):
            try:
                p = pipe_klass(self)
                p.execute(self.config)
                self.save_build_state()
            except:
                self.logging_raw('ERROR: BUILD FAILED')
                self.save_build_state()
                raise

        return self.config

    total_tasks = 0
    _counter = 1

    def incr_total_tasks(self):
        self.total_tasks += 1

    def incr_task_counter(self):
        self._counter += 1

    def logging_task(self, message):
        if self.forcerun:
            self.incr_total_tasks()
            return

        prefix = "### (%s of %s) " % (self._counter, self.total_tasks)
        self.incr_task_counter()

        self.logger.info('\n\n\n' + (prefix + message.strip()).strip())
        return self.taskset.create_task(prefix + message)

    def logging_task_done(self, task, failed=False):
        self.taskset.close_task(task, failed=failed)

    def logging_cmd(self, message):
        self.logger.info('\n$ ' + message.strip().replace(os.getcwd() + os.path.sep, ''))

    def logging_raw(self, message):
        if message.startswith('### ') or message.startswith('## '):
            message = '\n' * 3 + message.strip()
        if message.startswith('$ '):
            message = '\n' + message.strip().replace(os.getcwd() + os.path.sep, '')
        self.logger.info(message)

    def logging_err(self, message):
        self.logger.info('Error: ' + message.strip())
