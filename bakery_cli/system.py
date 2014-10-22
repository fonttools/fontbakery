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
from __future__ import print_function

import os as os_origin
import shutil as shutil_origin
import subprocess
import sys


__all__ = ['os', 'shutil', 'run', 'prun']


def shell_cmd_repr(command, args):
    available_commands = {
        'move': 'mv %s',
        'copy': 'cp -a %s',
        'copytree': 'cp -a %s',
        'makedirs': 'mkdir -p %s'
    }
    return available_commands[command] % ' '.join(list(args))


class metaclass(type):

    def __getattr__(cls, value):
        if not hasattr(cls.__originmodule__, value):
            _ = "'module' object has no attribute '%s'"
            raise AttributeError(_ % value)

        attr = getattr(cls.__originmodule__, value)
        if not callable(attr):
            return attr

        def func(*args, **kwargs):
            log = kwargs.pop('log', None)
            if log:
                log.debug('\n$ ' + shell_cmd_repr(value, args))
            try:
                result = getattr(cls.__originmodule__, value)(*args, **kwargs)
                return result
            except Exception as e:
                if log:
                    log.debug('Error: %s' % e.message)
                raise e

        return func


class osmetaclass(metaclass):
    __originmodule__ = os_origin


class shutilmetaclass(metaclass):
    __originmodule__ = shutil_origin


class shutil(object):
    __metaclass__ = shutilmetaclass


class os(object):
    __metaclass__ = osmetaclass


def run(command, cwd, log):
    """ Wrapper for subprocess.Popen with custom logging support.

        :param command: shell command to run, required
        :param cwd: - current working dir, required
        :param log: - logging object with .write() method, required

    """
    # Start the command
    env = os.environ.copy()

    log.info('$ %s\n' % command)
    env.update({'PYTHONPATH': os.pathsep.join(sys.path)})
    process = subprocess.Popen(command, shell=True, cwd=cwd,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               close_fds=True, env=env)
    while True:
        # Read output and errors
        stdout = process.stdout.readline()
        stderr = process.stderr.readline()
        # Log output
        if stdout.strip():
            log.debug(stdout)
        # Log error
        if stderr:
            # log error
            log.error('Error: ' + stderr)
        # If no output and process no longer running, stop
        if not stdout and not stderr and process.poll() is not None:
            break
    # if the command did not exit cleanly (with returncode 0)
    if process.returncode:
        msg = 'Fatal: Exited with return code %s \n' % process.returncode
        # Log the exit status
        log.error(msg)
        # Raise an error on the worker
        raise StandardError(msg)


def prun(command, cwd, log=None):
    """
    Wrapper for subprocess.Popen that capture output and return as result

        :param command: shell command to run
        :param cwd: current working dir
        :param log: loggin object with .write() method

    """
    env = os.environ.copy()
    env.update({'PYTHONPATH': os.pathsep.join(sys.path)})
    process = subprocess.Popen(command, shell=True, cwd=cwd,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               close_fds=True, env=env)
    if log:
        log.info('$ %s\n' % command)

    stdout = ''
    for line in iter(process.stdout.readline, ''):
        if log:
            log.debug(line)
        stdout += line
        process.stdout.flush()
    return stdout
