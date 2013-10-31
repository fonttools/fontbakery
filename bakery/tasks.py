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
import os
import glob
import subprocess
from flask.ext.rq import job
import plistlib
from .utils import RedisFd
import re
import shutil
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
DATA_ROOT = os.path.join(ROOT, 'data')

def run(command, cwd, log):
    """ Wrapper for subprocess.Popen with custom logging support.

        :param command: shell command to run, required
        :param cwd: - current working dir, required
        :param log: - logging object with .write() method, required

    """
    # print the command on the worker console
    print(command)
    # log the command
    log.write('\n$ %s\n' % command)
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
            print(stderr, end = '')
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
    Wrapper for subprocess.Popen that capture output and return as result

        :param command: shell command to run
        :param cwd: current working dir
        :param log: loggin object with .write() method

    """
    p = subprocess.Popen(command, shell = True, cwd = cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    stdout = p.communicate()[0]
    if log:
        log.write('$ %s' % command)
        log.write(stdout)
    return stdout

@job
def project_git_sync(project):
    """
    Sync _in git repo, or download it if it doesn't yet exist.

    :param project: :class:`~bakery.models.Project` instance
    :param log: :class:`~bakery.utils.RedisFd` as log
    """
    _in = os.path.join(DATA_ROOT, '%(login)s/%(id)s.in/' % project)
    # Create the incoming repo directory (_in) if it doesn't exist
    if not os.path.exists(_in):
        # log.write('Creating Incoming Directory\n', prefix = '### ')
        run('mkdir -p %s' % _in, cwd = DATA_ROOT)
    # Update _in if it already exists with a .git directory
    if os.path.exists(os.path.join(_in, '.git')):
        # log.write('Sync Git Repository\n', prefix = '### ')
        # remove anything in the _in directory that isn't checked in
        prun('git reset --hard', cwd = _in)
        prun('git clean --force', cwd = _in)
        # pull from origin master branch
        prun('git pull origin master', cwd = _in)
    # Since it doesn't exist as a git repo, get the _in repo
    else:
        # clone the repository
        # log.write('Copying Git Repository\n', prefix = '### ')
        try:
            # TODO in the future, use http://schacon.github.io/git/git-ls-remote.html to validate the URL string
            # http://stackoverflow.com/questions/9610131/how-to-check-the-validity-of-a-remote-git-repository-url
            prun('git clone --depth=100 --quiet --branch=master %(clone)s .' % project, cwd = _in)
        # if the clone action didn't work, just copy it
        except:
            # if this is a file URL, copy the files, and set up the _in directory as a git repo
            if project.clone[:7] == "file://":
                # cp recursively, keeping all attributes, not following symlinks, not deleting existing files, verbosely
                prun('cp -a %(clone)s .' % project, cwd = _in)
                #
                prun('git init .', cwd = _in)
                prun('git add *', cwd = _in)
                msg = "Initial commit made automatically by Font Bakery"
                prun('git commit -a -m "%s"' % msg, cwd = _in)
        # Now we have it, create an initial project state
        finally:
            config = project.config

def copy_and_rename_ufos_process(project, build, log):
    """
    Setup UFOs for building
    """
    config = project.config

    param = { 'login': project.login, 'id': project.id,
        'revision': build.revision, 'build': build.id }

    _user = os.path.join(DATA_ROOT, '%(login)s/' % param)
    _in = os.path.join(DATA_ROOT, '%(login)s/%(id)s.in/' % param)
    _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/%(revision)s.%(build)s/' % param)
    _out_src = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/%(revision)s.%(build)s/src/' % param)

    log.write('Copy [and Rename] UFOs\n', prefix = '### ')

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
        run("cp -a '%s' '%s'" % (_in_ufo_path, _out_ufo_path), cwd=_out, log=log)

        # Fix common lack of nbspace issue
        log.write('Fix nbsp in UFOs\n', prefix = '### ')
        cmd = str("%s/venv/bin/python %s/scripts/fix-addnbsp.py '%s'") % (ROOT, ROOT, _out_ufo_path)
        run(cmd, cwd=_out, log=log)

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
        licenseFileInFullPath = config['state']['license_file']
        licenseFileIn = licenseFileInFullPath.split('/')[-1]
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
        _in_license = os.path.join(_in, licenseFileInFullPath)
        _out_license = os.path.join(_out, licenseFileOut)
        run('cp -a "%s" "%s"' % (_in_license, _out_license), cwd = _user, log=log)
    else:
        log.write('License file not copied\n', prefix = 'Error: ')

    # Copy FONTLOG file
    _in_fontlog  = os.path.join(_in,  'FONTLOG.txt')
    _out_fontlog = os.path.join(_out, 'FONTLOG.txt')
    if os.path.exists(_in_fontlog) and os.path.isfile(_in_fontlog):
        run('cp -a "%s" "%s"' % (_in_fontlog, _out_fontlog), cwd = _user, log=log)
    else:
        log.write('FONTLOG.txt does not exist\n', prefix = 'Error: ')

    # Copy DESCRIPTION.en_us.html file
    _in_desc  = os.path.join(_in,  'DESCRIPTION.en_us.html')
    _out_desc = os.path.join(_out, 'DESCRIPTION.en_us.html')
    if os.path.exists(_in_desc) and os.path.isfile(_in_desc):
        run('cp -a "%s" "%s"' % (_in_desc, _out_desc), cwd = _user, log=log)
    else:
        log.write('DESCRIPTION.en_us.html does not exist upstream, will generate one later\n', prefix = 'Error: ')

    # Copy METADATA.json file
    _in_meta  = os.path.join(_in,  'METADATA.json')
    _out_meta = os.path.join(_out, 'METADATA.json')
    if os.path.exists(_in_meta) and os.path.isfile(_in_meta):
        run('cp -a "%s" "%s"' % (_in_meta, _out_meta), cwd = _user, log=log)
    else:
        log.write('METADATA.json does not exist upstream, will generate one later\n', prefix = 'Error: ')

    # Copy any txt files selected by user
    if config['state'].get('txt_files_copied', None):
        for filename in config['state']['txt_files_copied']:
            _in_file  = os.path.join(_in,  filename)
            _out_file = os.path.join(_out, filename)
            run('cp -a "%s" "%s"' % (_in_file, _out_file), cwd = _user, log=log)

def generate_fonts_process(project, build, log):
    """
    Generate TTF files from UFO files using ufo2ttf.py
    """

    param = { 'login': project.login, 'id': project.id,
        'revision': build.revision, 'build': build.id }

    _in = os.path.join(DATA_ROOT, '%(login)s/%(id)s.in/' % param)
    _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/%(revision)s.%(build)s/' % param)
    _out_src = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/%(revision)s.%(build)s/src/' % param)

    scripts_folder = os.path.join(ROOT, 'scripts')

    log.write('Convert UFOs to TTFs (ufo2ttf.py)\n', prefix = '### ')

    os.chdir(_out_src)
    for name in glob.glob("*.ufo"):
        name = name[:-4] # cut .ufo
        cmd = "python ufo2ttf.py '%(out_src)s%(name)s.ufo' '%(out_src)s%(name)s.ttf' '%(out_src)s%(name)s.otf'" % {
            'out_src': _out_src,
            'name': name,
        }
        run(cmd, cwd = scripts_folder, log=log)

def ttfautohint_process(project, build, log):
    """
    Run ttfautohint with project command line settings for each
    ttf file in result src folder, outputting them in the _out root,
    or just copy the ttfs there.
    """
    # $ ttfautohint -l 7 -r 28 -G 0 -x 13 -w "" -W -c original_font.ttf final_font.ttf
    config = project.config

    param = { 'login': project.login, 'id': project.id,
        'revision': build.revision, 'build': build.id }

    _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/%(revision)s.%(build)s/' % param)
    _out_src = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/%(revision)s.%(build)s/src/' % param)

    if config['state'].get('ttfautohint', None):
        log.write('Autohint TTFs (ttfautohint)\n', prefix = '### ')
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
        log.write('Autohint not used\n', prefix = '### ')
        run("mv src/*.ttf .", cwd=_out, log=log)

def ttx_process(project, build, log):
    """
    Roundtrip TTF files through TTX to compact their filesize
    """

    param = { 'login': project.login, 'id': project.id,
        'revision': build.revision, 'build': build.id }

    _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/%(revision)s.%(build)s/' % param)
    _out_src = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/%(revision)s.%(build)s/src/' % param)

    log.write('Compact TTFs with ttx\n', prefix = '### ')

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


def subset_process(project, build, log):
    config = project.config

    param = { 'login': project.login, 'id': project.id,
        'revision': build.revision, 'build': build.id }

    _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/%(revision)s.%(build)s/' % param)
    _out_src = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/%(revision)s.%(build)s/src/' % param)

    log.write('Subset TTFs (subset.py)\n', prefix = '### ')

    for subset in config['state']['subset']:
        os.chdir(_out_src)
        for name in glob.glob("*.ufo"):
            name = name[:-4] # cut .ufo
            # python ~/googlefontdirectory/tools/subset/subset.py \
            #   --null --nmr --roundtrip --script --subset=$subset \
            #   $font.ttf $font.$subset >> $font.$subset.log \
            # 2>> $font.$subset.log; \
            cmd = str("%(wd)s/venv/bin/python %(wd)s/scripts/subset.py" + \
                 " --subset=%(subset)s" + \
                 " --null --nmr --roundtrip --script" + \
                 " '%(out)s.ttf'" + \
                 " '%(out)s.%(subset)s'") % {
                    'subset':subset,
                    'out': os.path.join(_out, name),
                    'name': name,
                    'wd': ROOT
                    }
            run(cmd, cwd=_out, log=log)
            cmd = str("%(wd)s/venv/bin/python %(wd)s/scripts/subset.py" + \
                 " --subset=%(subset)s" + \
                 " --null --nmr --roundtrip --script --opentype-features" + \
                 " '%(out)s.ttf'" + \
                 " '%(out)s.%(subset)s-opentype'") % {
                    'subset':subset,
                    'out': os.path.join(_out, name),
                    'name': name,
                    'wd': ROOT
                    }
            run(cmd, cwd=_out, log=log)
    os.chdir(_out)
    files = glob.glob('*+latin*')
    for filename in files:
        newfilename = filename.replace('+latin', '')
        run("mv '%s' '%s'" % (filename, newfilename), cwd=_out, log=log)

def generate_metadata_process(project, build, log):
    """
    Generate METADATA.json using genmetadata.py
    """

    param = { 'login': project.login, 'id': project.id,
        'revision': build.revision, 'build': build.id }

    _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/%(revision)s.%(build)s/' % param)

    cmd = "%(wd)s/venv/bin/python %(wd)s/scripts/genmetadata.py '%(out)s'"
    log.write('Generate METADATA.json (genmetadata.py)\n', prefix = '### ')
    run(cmd % {'wd': ROOT, 'out': _out}, cwd=_out, log=log)
    # TODO Fix the genmetadata.py script so that it always outputs in the same order;
    # currently when you run it a 2nd time, it places dateAdded at the end, which is
    # what most METADATA.json files have, so it should just happen. Workaround is
    # to run it twice ;)
    run(cmd % {'wd': ROOT, 'out': _out}, cwd=_out, log=log)

def lint_process(project, build, log):
    """
    Run lint.jar on ttf files
    """
    param = { 'login': project.login, 'id': project.id,
        'revision': build.revision, 'build': build.id }

    _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/%(revision)s.%(build)s/' % param)

    log.write('Lint (lint.jar)\n', prefix = '### ')
    # java -jar dist/lint.jar "$(dirname $metadata)"
    cmd = "java -jar %(wd)s/scripts/lint.jar '%(out)s'"
    run(cmd % {'wd': ROOT, 'out': _out}, cwd=_out, log=log)
    # Mark this project as building successfully
    # TODO: move this from here to the new checker lint process completing all required checks successfully
    project.config['local']['status'] = 'built'

def fontaine_process(project, build, log):
    """
    Run pyFontaine on ttf files
    """
    param = { 'login': project.login, 'id': project.id,
        'revision': build.revision, 'build': build.id }

    _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/%(revision)s.%(build)s/' % param)

    log.write('pyFontaine (fontaine/main.py)\n', prefix = '### ')
    os.chdir(_out)
    files = glob.glob('*.ttf')
    for file in files:
        cmd = "python %s/venv/lib/python2.7/site-packages/fontaine/main.py --text '%s' >> 'src/fontaine.txt'" % (ROOT, file)
    run(cmd, cwd=_out, log=log)
    # TODO also save the totals for the dashboard....
    #   log.write('Running Fontaine on Results\n', prefix = '### ')
    #   fonts = utils.project_fontaine(project)
    #   project.config['state']['fontaine'] = fonts
    #   project.save_state()


def upstream_tests(project, build, log):
    import checker.upstream_runner

    param = { 'login': project.login, 'id': project.id,
        'revision': build.revision, 'build': build.id }

    _in = os.path.join(DATA_ROOT, '%(login)s/%(id)s.in/' % project)
    _out_yaml = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/%(revision)s.%(build)s.utests.yaml' % param)

    result = {}
    os.chdir(_in)
    for font in project.config['local']['ufo_dirs']:
        result[font] = checker.upstream_runner.run_set(os.path.join(_in, font))

    l = open(_out_yaml, 'w')
    l.write(yaml.safe_dump(result))
    l.close()

def result_tests(project, build, log):
    import checker.result_runner

    param = { 'login': project.login, 'id': project.id,
        'revision': build.revision, 'build': build.id }

    _out_src = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/%(revision)s.%(build)s/src/' % param)
    _out_yaml = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/%(revision)s.%(build)s.rtests.yaml' % param)

    result = {}
    os.chdir(_out_src)
    for font in glob.glob("*.ttf"):
        result[font] = checker.result_runner.run_set(os.path.join(_out_src, font))

    l = open(_out_yaml, 'w')
    l.write(yaml.safe_dump(result))
    l.close()


@job
def process_project(project, build, revision):
    """
    Bake the project, building all fonts according to the project setup.

    :param project: :class:`~bakery.models.Project` instance
    :param log: :class:`~bakery.utils.RedisFd` as log
    """

    param = { 'login': project.login, 'id': project.id,
        'revision': build.revision, 'build': build.id }
    _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/%(revision)s.%(build)s/' % param)
    _out_src = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/%(revision)s.%(build)s/src/' % param)
    _out_log = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/process.%(revision)s.%(build)s.log' % param)

    log = RedisFd(_out_log, 'w')

    # Ensure longest path exists
    if not os.path.exists(_out_src):
        os.makedirs(_out_src)

    # setup is set after 'bake' button is first pressed
    if project.config['local'].get('setup', None):
        # this code change upstream repository
        run("git co %s" % revision, cwd=_out, log=log)
        log.write('Bake Begins!\n', prefix = '### ')
        copy_and_rename_ufos_process(project, build, log)
        generate_fonts_process(project, build, log)
        ttfautohint_process(project, build, log)
        ttx_process(project, build, log)
        subset_process(project, build, log)
        generate_metadata_process(project, build, log)
        lint_process(project, build, log)
        fontaine_process(project, build, log)
        upstream_tests(project, build, log)
        result_tests(project, build, log)
        log.write('Bake Succeeded!\n', prefix = '### ')
        set_done(build)


    log.close()


def set_done(build):
    """ Set done flag for build """
    from flask import current_app
    assert current_app
    from .extensions import db
    db.init_app(current_app)
    build.is_done = True
    db.session.add(build)
    db.session.commit()


