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
import re
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
DATA_ROOT = os.path.join(ROOT, 'data')

def run(command, cwd, log):
    """ Wrapper for subprocess.Popen with custom logging support.

        :param command: shell command to run, required
        :param cwd: - current working dir, required
        :param log: - logging object with .write() method, required

    """
    # print the command on the worker console
    print command
    # log the command
    log.write('\nCommand: %s\n' % command)
    # Start the command
    p = subprocess.Popen(command, shell = True, cwd = cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    while True:
        # Read output and errors
        stdout = p.stdout.readline()
        stderr = p.stderr.readline()
        # Log output
        log.write(stdout)
        # Log error
        if stderr:
            # print the error on the worker console
            print stderr,
            # log error
            log.write(stderr, prefix = 'Error: ')
        # If no output and process no longer running, stop
        if not stdout and not stderr and p.poll() != None:
            break
    # if the command did not exit cleanly (with returncode 0)
    if p.returncode:
        msg = 'Fatal: Exited with return code %s \n' % p.returncode
        # Log the exit status
        log.write(msg)
        # Raise an error on the worker
        raise StandardError(msg)

def prun(command, cwd, log=None):
    """
    
    THIS METHOD IS DEPRECATED
    
    Wrapper for subprocess.Popen that capture output and return as result

        :param command: shell command to run
        :param cwd: current working dir
        :param log: loggin object with .write() method

    """
    p = subprocess.Popen(command, shell = True, cwd = cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
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
    # Create the incoming repo directory (_in) if it doesn't exist
    if not os.path.exists(_in):
        log.write('Creating Incoming Directory\n', prefix = 'Header: ')
        run('mkdir -p %s' % _in, cwd = DATA_ROOT, log=log)
    # Update _in if it already exists with a .git directory
    if os.path.exists(os.path.join(_in, '.git')):
        log.write('Sync Git Repository\n', prefix = 'Header: ')
        # remove anything in the _in directory that isn't checked in
        run('git reset --hard', cwd = _in, log=log)
        # pull from origin master branch
        run('git pull origin master', cwd = _in, log=log)
    # Since it doesn't exist as a git repo, get the _in repo
    else:
        # clone the repository
        log.write('Copying Git Repository\n', prefix = 'Header: ')
        try:
            # TODO: use the git check url command (in issue tracker) first
            run('git clone --depth=100 --quiet --branch=master %(clone)s .' % project, cwd = _in, log=log)
        # if the clone action didn't work, just copy it 
        except:
            # if this is a file URL, copy the files, and set up the _in directory as a git repo
            if project.clone[:7] == "file://":
                # cp recursively, keeping all attributes, not following symlinks, not deleting existing files, verbosely
                run('cp -anv %(clone)s .' % project, cwd = _in, log=log)
                # 
                run('git init .', cwd = _in, log=log)
                run('git add *', cwd = _in, log=log)
                msg = "Initial commit made automatically by Font Bakery"
                run('git commit -a -m "%s"' % msg, cwd = _in, log=log)

def copy_and_rename_ufos_process(project, log):
    """
    Setup UFOs for building
    """
    config = project.config
    _user = os.path.join(DATA_ROOT, '%(login)s/' % project)
    _in = os.path.join(DATA_ROOT, '%(login)s/%(id)s.in/' % project)
    _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/' % project)
    _out_src = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/src/' % project)
    _out_log = os.path.join(DATA_ROOT, '%(login)s/%(id)s.process.log' % project)

    log.write('Copy [and Rename] UFOs\n', prefix = 'Header: ')

    # Set the familyName
    if config['state'].get('familyname', None):
        familyName = config['state']['familyname']
    else:
        familyName = False

    # Copy UFO files from git repo to _out_src [renaming their filename and metadata]
    for _in_ufo in config['state']['ufo']:
        # Decide the incoming filepath
        _in_ufo_path = os.path.join(_in, _in_ufo) 
        # Read the _in_ufo fontinfo.plist
        _in_ufoPlist = os.path.join(_in_ufo_path, 'fontinfo.plist')
        _in_ufoFontInfo = plistlib.readPlist(_in_ufoPlist)
        # Get the styleName
        styleName = _in_ufoFontInfo['styleName']
        # Always have a regular style
        if styleName == 'Normal':
            styleName = 'Regular'
        # Get the familyName, if its not set
        if not familyName:
            familyName = _in_ufoFontInfo['familyName']
        # Remove whitespace from names
        styleNameNoWhitespace = re.sub(r'\s', '', styleName)
        familyNameNoWhitespace = re.sub(r'\s', '', familyName)
        # Decide the outgoing filepath
        _out_ufo = "%s-%s.ufo" % (familyNameNoWhitespace, styleNameNoWhitespace)
        _out_ufo_path = os.path.join(_out_src, _out_ufo)
        # Copy the UFOs
        run("cp -R '%s' '%s'" % (_in_ufo_path, _out_ufo_path), cwd=_out, log=log)
        # If we rename, change the font family name metadata inside the _out_ufo
        if familyName:
            # Read the _out_ufo fontinfo.plist
            _out_ufoPlist = os.path.join(_out_ufo_path, 'fontinfo.plist')
            _out_ufoFontInfo = plistlib.readPlist(_out_ufoPlist)
            # Set the familyName
            _out_ufoFontInfo['familyName'] = familyName
            # Set PS Name 
            # Ref: www.adobe.com/devnet/font/pdfs/5088.FontNames.pdf‎< Family Name > < Vendor ID > - < Weight > < Width > < Slant > < Character Set >
            _out_ufoFontInfo['postscriptFontName'] = familyNameNoWhitespace + '-' + styleNameNoWhitespace
            # Set Full Name
            _out_ufoFontInfo['postscriptFullName'] = familyName + ' ' + styleName
            # Write _out fontinfo.plist
            plistlib.writePlist(_out_ufoFontInfo, _out_ufoPlist)

    # Copy licence file
    # TODO: Infer license type from filename
    # TODO: Copy file based on license type
    if config['state'].get('license_file', None):
        # Set _in license file name
        licenseFileIn = config['state']['license_file']
        # List posible OFL and Apache filesnames
        listOfOflFilenames = ['Open Font License.markdown', 'OFL.txt', 'OFL.md']
        listOfApacheFilenames = ['APACHE.txt', 'LICENSE']
        # Canonicalize _out license file name
        if licenseFileIn in listOfOflFilenames:
            licenseFileOut = 'OFL.txt'
        elif licenseFileIn in listOfApacheFilenames:
            licenseFileOut = 'LICENSE.txt'
        else:
            licenseFileOut = licenseFileIn
        # Copy license file
        _in_license = os.path.join(_in, licenseFileIn)
        _out_license = os.path.join(_out, licenseFileOut)
        run('cp "%s" "%s"' % (_in_license, _out_license), cwd = _user, log=log)
    else:
        log.write('License file not copied\n', prefix = 'Error: ')

    # Copy FONTLOG file
    _in_fontlog = os.path.join(_in, 'FONTLOG.txt')
    _out_fontlog = os.path.join(_out, 'FONTLOG.txt')
    if os.path.exists(_in_fontlog):
        run('cp "%s" "%s"' % (_in_fontlog, _out_fontlog), cwd = _user, log=log)
    else:
        log.write('FONTLOG file does not exist\n', prefix = 'Error: ')


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

    if config['state'].get('ttfautohint', None):
        log.write('Autohint TTFs (ttfautohint)\n', prefix = 'Header: ')
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
        log.write('Autohint not used\n', prefix = 'Header: ')
        run("mv src/*.ttf .", cwd=_out, log=log)

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
        cmd = "ttx -i -q '%s.ttf'" % filename
        run(cmd, cwd=_out, log=log)
        # move the original ttf to the side
        cmd = "mv '%s.ttf' '%s.ttf.orig'" % (filename, filename)
        run(cmd, cwd=_out, log=log)
        # convert the ttx back to a ttf file - this may fail
        cmd = "ttx -i -q '%s.ttx'" % filename
        run(cmd, cwd=_out, log=log)
        # compare filesizes TODO print analysis of this :)
        cmd = "ls -l '%s.ttf'*" % filename
        run(cmd, cwd=_out, log=log)
        # remove the original (duplicate) ttf
        cmd = "rm  '%s.ttf.orig'" % filename
        run(cmd, cwd=_out, log=log)
        # move ttx files to src
        cmd = "mv '%s.ttx' %s" % (filename, _out_src)
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
    _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/' % project)
    _out_src = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/src/' % project)
    # setup is set after 'bake' button is first pressed
    if project.config['local'].get('setup', None):
        # Ensure _out exists
        if not os.path.exists(_out):
            os.makedirs(_out_src)
        log.write('Bake Begins!\n', prefix = 'Header: ')
        copy_and_rename_ufos_process(project, log)
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
    _user = os.path.join(DATA_ROOT, '%(login)s/' % project)
    _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/' % project)
    _out_src = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/src/' % project)
    _out_log = os.path.join(DATA_ROOT, '%(login)s/%(id)s.process.log' % project)

    # If about to bake the project, rotate the _out dir if it exists
    # and copy the log. (We do this now before the log file is opened)
    if process:
        if os.path.exists(_out):
            # Recursively figure out the top out number
            project.revision = 1
            _out_old = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out-%(revision)s' % project)
            while os.path.exists(_out_old):
                project.revision += 1
                _out_old = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out-%(revision)s' % project)
            # Move the directory
            shutil.move(_out, _out_old)
            # Remake the directory 
            os.makedirs(_out_src)
            # Copy the log
            _out_old_log = os.path.join(_out_old, 'process.log')
            shutil.copyfile(_out_log, _out_old_log)

    # Ensure _user exists
    if not os.path.exists(_user):
        os.makedirs(_user)
    # create log file and open it with Redis
    log = RedisFd(os.path.join(DATA_ROOT, '%(login)s/%(id)s.process.log' % {
            'id': project.id,
            'login': project.login, }
            ),
        'w')
    # Sync the project, if given sync parameter (default no)
    if sync:
        project_git_sync(project, log = log)
        # This marks the project has downloaded
        if not project.is_ready:
            set_ready(project)
    # Bake the project, if given the project parameter (default yes)
    if process:
        process_project(project, log = log)
    # Close the log file
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
