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

import redis
import os
import glob
import subprocess
from flask.ext.rq import job
import plistlib
import checker.runner
from utils import RedisFd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
DATA_ROOT = os.path.join(ROOT, 'data')

def run(command, cwd = None, log = None):
    # command — to run,
    # cwd - current working dir
    # log — file descriptor with .write() method

    if log:
        log.write('Command: %s\n' % command)

    p = subprocess.Popen(command, shell = True, cwd = cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    while True:
        stdout = p.stdout.readline()
        stderr = p.stderr.readline()
        log.write(stdout)
        if stderr:
            log.write(stderr, prefix = 'Error: ')

        if not stdout and not stderr and p.poll() != None:
            break

    if p.returncode:
        log.write('Fatal: Execution error command "%s" returned %s code' % (command, p.returncode))
        raise ValueError

def prun(command, cwd, log=None):
    p = subprocess.Popen(command, shell = True, cwd = cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout = p.communicate()[0]
    if log:
        log.write('Command: %s' % command)
        log.write(stdout)
    return stdout

@job
def sync_and_process(project, connection = None):
    if connection:
        conn = redis.Redis(**connection)
    else:
        conn = None

    # create user folder
    if not os.path.exists(os.path.join(DATA_ROOT, project.login)):
        os.makedirs(os.path.join(DATA_ROOT, project.login))

    log = RedisFd(os.path.join(DATA_ROOT, '%(login)s/%(id)s.process.log' % {
            'id': project.id,
            'login': project.login, }
            ),
        'w', conn, "build_%s" % project.id)

    project_git_sync(project, log = log)
    process_project(project, conn = conn, log = log)

    log.close()

@job
def git_clean(project):
    return
    # CLEAN_SH = '' #"""cd %(root)s && rm -rf %(login)s/%(id)s.in/ && rm -rf %(login)s/%(id)s.out/"""
    # params = locals()
    # params['root'] = DATA_ROOT
    # run(CLEAN_SH % params)


@job
def project_git_sync(project, log):
    """
    Sync git repo, or download it if it doesn't yet exist
    """
    log.write('Sync Git Repository\n', prefix = 'Header: ')

    # Create the incoming repo dir if it doesn't exist
    _in = os.path.join(DATA_ROOT, '%(login)s/%(id)s.in/' % project)
    if not os.path.exists(_in):
        run('mkdir -p %s' % _in, cwd = DATA_ROOT, log=log)

    # If no .git folder exists in project folder, download repo
    if not os.path.exists(os.path.join(_in, '.git')):
        run('git clone --depth=100 --quiet --branch=master %(clone)s .' % project, cwd = _in, log=log)
    # Else, reset the repo and pull down latest updates
    else:
        run('git reset --hard', cwd = _in, log=log)
        run('git pull origin master', cwd = _in, log=log)

    # child = prun('git rev-parse --short HEAD', cwd=_in)
    # hashno = child.stdout.readline().strip()
    # make current out folder

@job
def process_project(project, conn, log):
    """
    The Baking Commands - the central functionality of this software :)
    """
    # login — user login
    # project_id - database project_id
    # conn - redis connection

    log.write('Copy [and Rename] UFOs\n', prefix = 'Header: ')
    copy_and_rename_ufos_process(project, log)

    # autoprocess is set after setup is completed once
    if project.setup_complete():
        log.write('Build Begins!\n', prefix = 'Header: ')

        log.write('Convert UFOs to TTFs (ufo2ttf.py)\n', prefix = 'Header: ')
        generate_fonts_process(project, log)

        log.write('Autohint TTFs (ttfautohint)\n', prefix = 'Header: ')
        ttfautohint_process(project, log)

        log.write('Compact TTFs with ttx\n', prefix = 'Header: ')
        ttx_process(project, log)

        log.write('Subset TTFs (subset.py)\n', prefix = 'Header: ')
        subset_process(project, log)

        log.write('Generate METADATA.json (genmetadata.py)\n', prefix = 'Header: ')
        generate_metadata_process(project, log)

        log.write('Lint (lint.jar)\n', prefix = 'Header: ')
        lint_process(project, log)

        log.write('Build Succeeded!\n', prefix = 'Header: ')

def copy_and_rename_ufos_process(project, log):
    """
    Set up UFOs for building
    """
    state = project.state
    _user = os.path.join(DATA_ROOT, '%(login)s/' % project)
    _in = os.path.join(DATA_ROOT, '%(login)s/%(id)s.in/' % project)
    _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/' % project)
    _out_src = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/src/' % project)

    # Make the out directory if it doesn't exist
    if not os.path.exists(_out_src):
        run('mkdir -p %s' % (_out_src), cwd = _user, log=log)
    # And rotate it out if it does
    else:
        i = 1
        _out_old = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out' % project) + 'old-' + str(i)
        while os.path.exists(_out_old):
            i += 1
            _out_old = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out' % project) + 'old-' + str(i)
        run('mv %s %s' % (_out, _out_old), cwd = _user, log=log)
        run('mkdir -p %s' % (_out_src), cwd = _user, log=log)

    # Copy UFO files from git repo to out/src/ dir
    for ufo, name in state['out_ufo'].items():
        if state['rename']:
            ufo_folder = name+'.ufo'
        else:
            ufo_folder = ufo.split('/')[-1]
        run("cp -R '%s' '%s'" % (os.path.join(_in, ufo), os.path.join(_out_src, ufo_folder)), log=log)
        # TODO DC: In future this should follow GDI naming for big families
        if state['rename']:
            finame = os.path.join(_out_src, ufo_folder, 'fontinfo.plist')
            finfo = plistlib.readPlist(finame)
            finfo['familyName'] = name
            plistlib.writePlist(finfo, finame)


def generate_fonts_process(project, log):
    """
    Generate TTF files from UFO files using ufo2ttf.py
    """
    state = project.state
    _in = os.path.join(DATA_ROOT, '%(login)s/%(id)s.in/' % project)
    _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/src/' % project)

    scripts_folder = os.path.join(ROOT, 'scripts')

    for name in state['out_ufo'].values():
        cmd = "python ufo2ttf.py '%(out)s.ufo' '%(out)s.ttf' '%(out)s.otf'" % {
            'out': os.path.join(_out, name),
        }
        run(cmd, cwd = scripts_folder, log=log)


def generate_metadata_process(project, log):
    _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/' % project)
    cmd = "%(wd)s/venv/bin/python %(wd)s/scripts/genmetadata.py '%(out)s'"
    run(cmd % {'wd': ROOT, 'out': _out}, cwd=_out, log=log)


def lint_process(project, log):
    _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/' % project)
    # java -jar dist/lint.jar "$(dirname $metadata)"
    cmd = "java -jar %(wd)s/scripts/lint.jar '%(out)s'"
    run(cmd % {'wd': ROOT, 'out': _out}, cwd=_out, log=log)


def ttfautohint_process(project, log):
    # $ ttfautohint -l 7 -r 28 -G 0 -x 13 -w "" -W -c original_font.ttf final_font.ttf
    config = project.config
    _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/' % project)
    if config['state'].get('ttfautohint', None):
        params = config['state']['ttfautohint']
        os.chdir(_out)
        for name in glob.glob("*.ufo"):
            cmd = "ttfautohint %(params)s '%(src)s.ttf' '%(out)s.ttf'" % {
                'params': params,
                'out': os.path.join(_out, name),
                'src': os.path.join(_out, 'src', name),
            }
            run(cmd % {'wd': ROOT, 'out': _out}, cwd=_out, log=log)
    else:
        run("cp src/*.ttf .", cwd=_out, log=log)


def subset_process(project, log):
    state = project.state
    _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/' % project)
    for subset in state['subset']:
        for name in state['out_ufo'].values():
            # python ~/googlefontdirectory/tools/subset/subset.py \
            #   --null --nmr --roundtrip --script --subset=$subset \
            #   $font.ttf $font.$subset >> $font.$subset.log \
            # 2>> $font.$subset.log; \

            cmd = str("%(wd)s/venv/bin/python %(wd)s/scripts/subset.py --null " + \
                  "--nmr --roundtrip --script --subset=%(subset)s '%(out)s.ttf'" + \
                  " %(out)s.%(subset)s") % {
                'subset':subset,
                'out': os.path.join(_out, name),
                'name': name,
                'wd': ROOT
            }
            run(cmd, cwd=_out, log=log)
    os.chdir(_out)
    files = glob.glob('*+latin')
    for filename in files:
        newfilename = filename.replace('+latin', '')
        run("mv '%s' '%s'" % (filename, newfilename), cwd=_out, log=log)


def ttx_process(project, log):
    state = project.state
    _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/' % project)
    for name in state['out_ufo'].values():
        filename = os.path.join(_out, name)
        # convert the ttf to a ttx file - this may fail
        cmd = "ttx -i '%s.ttf'" % filename
        run(cmd, cwd=_out, log=log)
        # move the original ttf to the side
        cmd = "mv '%s.ttf' '%s.ttf.orig'" % (filename, filename)
        run(cmd, cwd=_out, log=log)
        # convert the ttx back to a ttf file - this may fail
        cmd = "ttx -i '%s.ttx'" % filename
        run(cmd, cwd=_out, log=log)
        # compare filesizes TODO print analysis of this :)
        cmd = "ls -l '%s.ttf'*" % filename
        run(cmd, cwd=_out, log=log)
        # remove the original (duplicate) ttf
        cmd = "rm  '%s.ttf.orig'" % filename
        run(cmd, cwd=_out, log=log)


def project_tests(project):
    state = project.config['state']
    _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/src/' % project)
    result = {}
    for name in state['ufo']:
        result[name] = checker.runner.run_set(os.path.join(_out, name+'.ufo'))
    return result

