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

import os
import glob
import subprocess
from flask.ext.rq import job
import plistlib
from utils import RedisFd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
DATA_ROOT = os.path.join(ROOT, 'data')

def run(command, cwd, log):
    """ Wrapper for subprocess.Popen with custom logging support.

        :param command: shell command to run, required
        :param cwd: - current working dir, required
        :param log: - logging object with .write() method, required

    """
    log.write('\nCommand: %s\n' % command)
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
        log.write('Fatal: Execution error!\nFatal: $ %s\nFatal: This command exited with exit status: %s \n' % (command, p.returncode))
        # close file before exit
        log.close()
        raise ValueError

def prun(command, cwd, log=None):
    """
    
    THIS METHOD IS DEPRECATED
    
    Wrapper for subprocess.Popen that capture output and return as result

        :param command: shell command to run
        :param cwd: current working dir
        :param log: loggin object with .write() method

    """
    p = subprocess.Popen(command, shell = True, cwd = cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout = p.communicate()[0]
    if log:
        log.write('Command: %s' % command)
        log.write(stdout)
    return stdout

@job
def project_git_sync(project, log):
    """
    Sync _in git repo, or download it if it doesn't yet exist.

    :param project: :class:`~bakery.models.Project` instance
    :param log: :class:`~bakery.utils.RedisFd` as log
    """
    _in = os.path.join(DATA_ROOT, '%(login)s/%(id)s.in/' % project)

    log.write('Sync Git Repository\n', prefix = 'Header: ')

    # Create the incoming repo dir if it doesn't exist
    if not os.path.exists(_in):
        run('mkdir -p %s' % _in, cwd = DATA_ROOT, log=log)
    # Either download the _in repo
    if not os.path.exists(os.path.join(_in, '.git')):
        run('git clone --depth=100 --quiet --branch=master %(clone)s .' % project, cwd = _in, log=log)
    # Or reset _in and pull down latest updates
    else:
        # remove anything in the _in directory that isn't checked in
        run('git reset --hard', cwd = _in, log=log)
        # pull from origin master branch
        run('git pull origin master', cwd = _in, log=log)

def copy_and_rename_ufos_process(project, log):
    """
    Setup UFOs for building
    """
    config = project.config
    _user = os.path.join(DATA_ROOT, '%(login)s/' % project)
    _in = os.path.join(DATA_ROOT, '%(login)s/%(id)s.in/' % project)
    _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/' % project)
    _out_src = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/src/' % project)

    log.write('Copy [and Rename] UFOs\n', prefix = 'Header: ')

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


    if config['state'].get('familyname', None):
        familyname = config['state']['familyname']
    else:
        familyname = ''

    # Copy UFO files from git repo to out/src/ dir

    for ufo_in in config['state']['ufo']:
        # If we rename, change the filename
        if familyname:
            fontInfoFile = os.path.join(_in, ufo_in, 'fontinfo.plist')
            fontInfo = plistlib.readPlist(fontInfoFile)
            styleName = fontInfo['styleName']
            # we should always have a regular style
            if styleName == 'Normal':
                styleName = 'Regular'
            ufo_out = "%s-%s.ufo" % (familyname, styleName)
        else:
            _out_name = ufo.split('/')[-1]
        # Copy the UFOs
        run("cp -R '%s' '%s'" % (os.path.join(_in, ufo), os.path.join(_out_src, _out_name)), cwd=_user, log=log)
        # If we rename, change the font family name metadata
        # TODO DC: In future this should follow GDI naming for big families
        if familyname:
            fontInfoFile = os.path.join(_out_src, ufo_out, 'fontinfo.plist')
            fontInfo = plistlib.readPlist(fontInfoFile)
            # we should always have a regular style
            if fontInfo['styleName'] == 'Normal':
                fontInfo['styleName'] = 'Regular'
            #
            # XXX TODO: This code isn't tested
            #
            fontInfo['familyName'] = familyname
            fontInfo['postscriptFontName'] = familyname + '-' + fontInfo['styleName']
            fontInfo['postscriptFullName'] = familyname + ' ' + fontInfo['styleName']
            plistlib.writePlist(fontInfo, fontInfoFile)

def generate_fonts_process(project, log):
    """
    Generate TTF files from UFO files using ufo2ttf.py
    """
    _in = os.path.join(DATA_ROOT, '%(login)s/%(id)s.in/' % project)
    _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/' % project)
    _out_src = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/src/' % project)
    scripts_folder = os.path.join(ROOT, 'scripts')

    log.write('Convert UFOs to TTFs (ufo2ttf.py)\n', prefix = 'Header: ')

    os.chdir(_out_src)
    for name in glob.glob("*.ufo"):
        name = name[:-4] # cut .ufo
        cmd = "python ufo2ttf.py '%(out_src)s%(name)s.ufo' '%(out_src)s%(name)s.ttf' '%(out_src)s%(name)s.otf'" % {
            'out_src': _out_src,
            'name': name,
        }
        run(cmd, cwd = scripts_folder, log=log)

def ttfautohint_process(project, log):
    """
    Run ttfautohint with project command line settings for each
    ttf file in result src folder, outputting them in the _out root,
    or just copy the ttfs there.
    """
    # $ ttfautohint -l 7 -r 28 -G 0 -x 13 -w "" -W -c original_font.ttf final_font.ttf
    config = project.config
    _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/' % project)
    _out_src = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/src/' % project)

    log.write('Autohint TTFs (ttfautohint)\n', prefix = 'Header: ')

    if config['state'].get('ttfautohint', None):
        params = config['state']['ttfautohint']
        os.chdir(_out_src)
        for name in glob.glob("*.ufo"):
            name = name[:-4] # cut .ufo
            cmd = "ttfautohint %(params)s '%(src)s.ttf' '%(out)s.ttf'" % {
                'params': params,
                'out': os.path.join(_out, name),
                'src': os.path.join(_out_src, name),
            }
            run(cmd, cwd=_out, log=log)
    else:
        run("cp src/*.ttf .", cwd=_out, log=log)

def ttx_process(project, log):
    """
    Roundtrip TTF files through TTX to compact their filesize
    """
    _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/' % project)
    _out_src = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/src/' % project)

    log.write('Compact TTFs with ttx\n', prefix = 'Header: ')

    os.chdir(_out_src)
    for name in glob.glob("*.ufo"):
        name = name[:-4] # cut .ufo
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

def subset_process(project, log):
    config = project.config
    _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/' % project)
    _out_src = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/src/' % project)

    log.write('Subset TTFs (subset.py)\n', prefix = 'Header: ')

    for subset in config['state']['subset']:
        os.chdir(_out_src)
        for name in glob.glob("*.ufo"):
            name = name[:-4] # cut .ufo
            # python ~/googlefontdirectory/tools/subset/subset.py \
            #   --null --nmr --roundtrip --script --subset=$subset \
            #   $font.ttf $font.$subset >> $font.$subset.log \
            # 2>> $font.$subset.log; \

            cmd = str("%(wd)s/venv/bin/python %(wd)s/scripts/subset.py --null " + \
                  "--nmr --roundtrip --script --subset=%(subset)s '%(out)s.ttf'" + \
                  " '%(out)s.%(subset)s'") % {
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

def generate_metadata_process(project, log):
    """
    Generate METADATA.json using genmetadata.py
    """
    _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/' % project)
    cmd = "%(wd)s/venv/bin/python %(wd)s/scripts/genmetadata.py '%(out)s'"
    log.write('Generate METADATA.json (genmetadata.py)\n', prefix = 'Header: ')
    run(cmd % {'wd': ROOT, 'out': _out}, cwd=_out, log=log)

def lint_process(project, log):
    """
    Run lint.jar on ttf files
    """
    _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/' % project)
    log.write('Lint (lint.jar)\n', prefix = 'Header: ')
    # java -jar dist/lint.jar "$(dirname $metadata)"
    cmd = "java -jar %(wd)s/scripts/lint.jar '%(out)s'"
    run(cmd % {'wd': ROOT, 'out': _out}, cwd=_out, log=log)
    # Mark this project as building successfully
    # TODO: move this from here to the new checker lint process completing all required checks successfully
    project.config['local']['status'] = 'built'

@job
def process_project(project, log):
    """
    Bake the project, building all fonts according to the project setup.

    :param project: :class:`~bakery.models.Project` instance
    :param log: :class:`~bakery.utils.RedisFd` as log
    """
    # login — user login
    # project_id - database project_id

    copy_and_rename_ufos_process(project, log)

    # autoprocess is set after setup is completed once
    if project.config['local'].get('setup', None):
        log.write('Bake Begins!\n', prefix = 'Header: ')
        generate_fonts_process(project, log)
        ttfautohint_process(project, log)
        ttx_process(project, log)
        subset_process(project, log)
        generate_metadata_process(project, log)
        lint_process(project, log)
        log.write('Bake Succeeded!\n', prefix = 'Header: ')

def set_ready(project):
    from flask import current_app
    assert current_app
    from .extensions import db
    db.init_app(current_app)
    project.is_ready = True
    db.session.add(project)
    db.session.commit()

@job
def sync_and_process(project, process = True, sync = False):
    """
    Sync and process (Bake) the project.

    :param project: :class:`~bakery.models.Project` instance
    :param sync: Boolean. Sync the project. Defaults to off. 
    :param process: Boolean. Process (Bake) the project. Default to on.
    """
    # create user folder
    if not os.path.exists(os.path.join(DATA_ROOT, project.login)):
        os.makedirs(os.path.join(DATA_ROOT, project.login))
    # create log file and open it with Redis
    log = RedisFd(os.path.join(DATA_ROOT, '%(login)s/%(id)s.process.log' % {
            'id': project.id,
            'login': project.login, }
            ),
        'w')
    # Sync the project, if given sync parameter (default no)
    if sync:
        project_git_sync(project, log = log)
    # Bake the project, if given the project parameter (default yes)
    if process:
        process_project(project, log = log)

    if not project.is_ready:
        set_ready(project)

    log.close()

def project_upstream_tests(project):
    import checker.upstream_runner
    _out_src = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/src/' % project)
    result = {}
    os.chdir(_out_src)
    for name in glob.glob("*.ufo"):
        result[name] = checker.upstream_runner.run_set(os.path.join(_out_src, name))
    return result

def project_result_tests(project):
    import checker.result_runner
    _out_src = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/' % project)
    result = {}
    os.chdir(_out_src)
    for name in glob.glob("*.ttf"):
        result[name] = checker.result_runner.run_set(os.path.join(_out_src, name))
    return result
