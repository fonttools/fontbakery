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

import sys

import codecs
import datetime
import glob
import os
import os.path as op
import plistlib
import re
import subprocess
import yaml

from checker import run_set, parse_test_results
from checker.base import BakeryTestCase
from fixer import fix_font
from flask.ext.rq import job
from fontTools import ttLib
from fontaine.ext.subsets import Extension as SubsetExtension

from .utils import RedisFd


@job
def refresh_repositories(username, token):
    from bakery.app import github
    from bakery.github import GithubSessionAPI, GithubSessionException
    from bakery.settings.models import ProjectCache
    _github = GithubSessionAPI(github, token)
    try:
        repos = _github.get_repo_list()
        ProjectCache.refresh_repos(repos, username)
    except GithubSessionException, ex:
        print(ex.message)


def run(command, cwd, log):
    """ Wrapper for subprocess.Popen with custom logging support.

        :param command: shell command to run, required
        :param cwd: - current working dir, required
        :param log: - logging object with .write() method, required

    """
    # print the command on the worker console
    print("[%s]:%s" % (cwd, command))
    # log the command
    log.write('\n$ %s\n' % command)
    # Start the command
    env = os.environ.copy()
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
        log.write(stdout)
        # Log error
        if stderr:
            # print the error on the worker console
            print(stderr, end='')
            # log error
            log.write(stderr, prefix='Error: ')
        # If no output and process no longer running, stop
        if not stdout and not stderr and process.poll() is not None:
            break
    # if the command did not exit cleanly (with returncode 0)
    if process.returncode:
        msg = 'Fatal: Exited with return code %s \n' % process.returncode
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
    # print the command on the worker console
    print("[%s]:%s" % (cwd, command))
    env = os.environ.copy()
    env.update({'PYTHONPATH': os.pathsep.join(sys.path)})
    process = subprocess.Popen(command, shell=True, cwd=cwd,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               close_fds=True, env=env)
    if log:
        log.write('$ %s\n' % command)

    stdout = ''
    for line in iter(process.stdout.readline, ''):
        if log:
            log.write(line)
        stdout += line
        process.stdout.flush()
    return stdout


def get_subsets_coverage_data(source_fonts_paths):
    """ Return dictionary with subsets coverages as a value
        and common name as a key """
    from fontaine.font import FontFactory
    from fontaine.cmap import Library
    library = Library(collections=['subsets'])
    subsets = {}
    for fontpath in source_fonts_paths:
        font = FontFactory.openfont(fontpath)
        for charmap, _, coverage, _ in \
                font.get_orthographies(_library=library):
            subsets[charmap.common_name.replace('Subset ', '')] = coverage
    return subsets


def generate_subsets_coverage_list(project, log=None):
    """ Returns sorted subsets from prepared yaml file in
        tuple [(common_name, coverage),].

        If file does not exist method creates one and writes pyfontaine
        coverages data using its Font API. """
    from .app import app
    if log:
        log.write('PyFontaine subsets with coverage values\n')

    _in = joinroot('%(login)s/%(id)s.in/' % project)
    ufo_dirs, ttx_files, _ = get_sources_lists(_in)

    _out_yaml = op.join(app.config['DATA_ROOT'],
                        '%(login)s/%(id)s.out/fontaine.yml' % project)
    if op.exists(_out_yaml):
        return sorted(yaml.safe_load(open(_out_yaml, 'r')).items())

    if not op.exists(op.dirname(_out_yaml)):
        os.makedirs(op.dirname(_out_yaml))

    source_fonts_paths = []
    # `get_sources_list` returns list of paths relative to root.
    # To complete to absolute paths use python os.path.join method
    # on root and path
    for path in ufo_dirs + ttx_files:
        source_fonts_paths.append(op.join(_in, path))
    subsets = get_subsets_coverage_data(source_fonts_paths)

    contents = yaml.safe_dump(subsets)

    yamlf = codecs.open(_out_yaml, mode='w', encoding="utf-8")
    yamlf.write(contents)
    yamlf.close()

    return sorted(yaml.safe_load(open(_out_yaml, 'r')).items())


@job
def project_git_sync(project):
    """
    Sync _in git repo, or download it if it doesn't yet exist.

    :param project: :class:`~bakery.models.Project` instance
    :param log: :class:`~bakery.utils.RedisFd` as log
    """
    from .app import db, app
    project.is_ready = False
    db.session.add(project)
    db.session.commit()
    db.session.refresh(project)

    _in = joinroot('%(login)s/%(id)s.in/' % project)
    _out = joinroot('%(login)s/%(id)s.out/' % project)
    if not op.exists(_out):
        os.makedirs(_out)

    prun('rm {}'.format('fontaine.yml'), cwd=_out)
    prun('rm {}'.format('upstream.log'), cwd=_out)

    log = RedisFd(op.join(_out, 'upstream.log'))

    # Create the incoming repo directory (_in) if it doesn't exist
    if not op.exists(_in):
        # log.write('Creating Incoming Directory\n', prefix='### ')
        prun('mkdir -p %s' % _in, cwd=app.config['DATA_ROOT'], log=log)
    # Update _in if it already exists with a .git directory
    if op.exists(op.join(_in, '.git')):
        # log.write('Sync Git Repository\n', prefix='### ')
        # remove anything in the _in directory that isn't checked in
        prun('git reset --hard', cwd=_in, log=log)
        prun('git clean --force', cwd=_in, log=log)
        # pull from origin master branch
        prun('git pull origin master', cwd=_in, log=log)
    # Since it doesn't exist as a git repo, get the _in repo
    else:
        # clone the repository
        # log.write('Copying Git Repository\n', prefix='### ')
        try:
            # TODO in the future, to validate the URL string use
            # http://schacon.github.io/git/git-ls-remote.html
            # http://stackoverflow.com/questions/9610131/how-to-check-the-validity-of-a-remote-git-repository-url
            prun(('git clone --progress --depth=100'
                  ' --branch=master %(clone)s .') % project, cwd=_in, log=log)
        except:
            # if the clone action didn't work, just copy it
            # if this is a file URL, copy the files, and set up
            # the _in directory as a git repo
            if project.clone[:7] == "file://":
                # cp recursively, keeping all attributes, not following
                # symlinks, not deleting existing files, verbosely
                prun('cp -a %(clone)s .' % project, cwd=_in, log=log)
                #
                prun('git init .', cwd=_in, log=log)
                prun('git add *', cwd=_in, log=log)
                msg = "Initial commit made automatically by Font Bakery"
                prun('git commit -a -m "%s"' % msg, cwd=_in, log=log)
        # Now we have it, create an initial project state
        finally:
            config = project.config

    generate_subsets_coverage_list(project, log=log)

    revision = prun("git rev-parse --short HEAD", cwd=_in).strip()
    upstream_revision_tests(project, revision)

    log.write('End: Repository is ready. Please Setup\n', prefix='### ')
    # set project state as ready after sync is done
    project.is_ready = True
    db.session.add(project)
    db.session.commit()


def joinroot(path):
    from bakery.app import app
    return op.join(app.config['DATA_ROOT'], path)


def copy_ufo_files(project, build, log):
    from .app import app
    config = project.config

    param = {'login': project.login, 'id': project.id,
             'revision': build.revision, 'build': build.id}

    _in = joinroot('%(login)s/%(id)s.in/' % param)
    _out = joinroot('%(login)s/%(id)s.out/%(build)s.%(revision)s/' % param)

    path = '%(login)s/%(id)s.out/%(build)s.%(revision)s/sources/' % param
    _out_src = joinroot(path)

    log.write('Copy [and Rename] UFOs\n', prefix='### ')

    # Set the familyName
    if config['state'].get('familyname', None):
        familyName = config['state']['familyname']
    else:
        familyName = False

    # Copy UFO files from git repo to _out_src [renaming their
    # filename and metadata]
    ufo_dirs = []
    for x in config['state'].get('process_files', []):
        if x.endswith('.ufo'):
            ufo_dirs.append(x)

    for _in_ufo in ufo_dirs:
        # Decide the incoming filepath
        _in_ufo_path = op.join(_in, _in_ufo)
        # Read the _in_ufo fontinfo.plist
        _in_ufoPlist = op.join(_in_ufo_path, 'fontinfo.plist')
        _in_ufoFontInfo = plistlib.readPlist(_in_ufoPlist)
        # Get the styleName
        styleName = _in_ufoFontInfo['styleName']
        # Always have a regular style
        if styleName == 'Normal':
            styleName = 'Regular'
        # Get the familyName, if its not set
        if not familyName:
            pfn = _in_ufoFontInfo.get('openTypeNamePreferredFamilyName', '')
            familyName = pfn or _in_ufoFontInfo.get('familyName', '')
            if not familyName:
                log.write(('Please set openTypeNamePreferredFamilyName or '
                           'familyName in %s fontinfo.plist and run another'
                           ' bake process.') % _in_ufo, prefix='### ')
                raise Exception(('Please set openTypeNamePreferredFamilyName '
                                 'or familyName in %s fontinfo.plist and '
                                 'run another bake process.') % _in_ufo)

        # Remove whitespace from names
        styleNameNoWhitespace = re.sub(r'\s', '', styleName)
        familyNameNoWhitespace = re.sub(r'\s', '', familyName)
        # Decide the outgoing filepath
        _out_ufo = "%s-%s.ufo" % (familyNameNoWhitespace,
                                  styleNameNoWhitespace)
        _out_ufo_path = op.join(_out_src, _out_ufo)
        # Copy the UFOs
        run("cp -a '%s' '%s'" % (_in_ufo_path, _out_ufo_path),
            cwd=_out, log=log)

        # If we rename, change the font family name metadata
        # inside the _out_ufo
        if familyName:
            # Read the _out_ufo fontinfo.plist
            _out_ufoPlist = op.join(_out_ufo_path, 'fontinfo.plist')
            _out_ufoFontInfo = plistlib.readPlist(_out_ufoPlist)
            # Set the familyName
            _out_ufoFontInfo['familyName'] = familyName

            # Set PS Name
            # Ref: www.adobe.com/devnet/font/pdfs/5088.FontNames.pdf‎
            # < Family Name > < Vendor ID > - < Weight > < Width >
            # < Slant > < Character Set >
            psfn = "%s-%s" % (familyNameNoWhitespace, styleNameNoWhitespace)
            _out_ufoFontInfo['postscriptFontName'] = psfn
            # Set Full Name
            psfn = "%s %s" % (familyName, styleName)
            _out_ufoFontInfo['postscriptFullName'] = psfn
            # Write _out fontinfo.plist
            plistlib.writePlist(_out_ufoFontInfo, _out_ufoPlist)

    scripts_folder = op.join(app.config['ROOT'], 'scripts')
    log.write('Convert UFOs to TTFs (ufo2ttf.py)\n', prefix='### ')

    os.chdir(_out_src)
    for name in glob.glob("*.ufo"):
        name = name[:-4]  # cut .ufo
        cmd = ("python ufo2ttf.py '{out_src}{name}.ufo' "
               "'{out}{name}.ttf' '{out_src}{name}.otf'")
        cmd = cmd.format(out_src=_out_src, name=name, out=_out)
        run(cmd, cwd=scripts_folder, log=log)


def copy_ttx_files(project, build, log):
    from .app import app
    config = project.config

    param = {'login': project.login, 'id': project.id,
             'revision': build.revision, 'build': build.id}

    _in = joinroot('%(login)s/%(id)s.in/' % param)
    _out = joinroot('%(login)s/%(id)s.out/%(build)s.%(revision)s/' % param)

    path = '%(login)s/%(id)s.out/%(build)s.%(revision)s/sources/' % param
    _out_src = joinroot(path)

    ttx_files = []
    for x in config['state'].get('process_files', []):
        if x.endswith('.ttx'):
            ttx_files.append(x)

    for ttx_file in ttx_files:
        _ttx_path = op.join(_in, ttx_file)
        if not op.exists(_ttx_path):
            run("echo file '{}' not found".format(_ttx_path),
                cwd=_out, log=log)
            continue

        font = ttLib.TTFont(None, lazy=False, recalcBBoxes=True,
                            verbose=False, allowVID=False)
        font.importXML(_ttx_path, quiet=True)
        _ttx_name = op.splitext(op.basename(_ttx_path))[0]

        def nameTableRead(font, NameID, fallbackNameID=False):
            for record in font['name'].names:
                if record.nameID == NameID:
                    if b'\000' in record.string:
                        string = record.string.decode('utf-16-be')
                        return string.encode('utf-8')
                    else:
                        return record.string

            if fallbackNameID:
                return nameTableRead(font, fallbackNameID)

        styleName = nameTableRead(font, 17, 2)
        # Always have a regular style
        if styleName == 'Normal':
            styleName = 'Regular'

        #   NameID=1 is required
        familyName = nameTableRead(font, 16, 1)
        # Remove whitespace from names
        styleNameNoWhitespace = re.sub(r'\s', '', styleName)
        familyNameNoWhitespace = re.sub(r'\s', '', familyName)

        _out_ttx_name = "{familyname}-{stylename}"
        _out_ttx_name = _out_ttx_name.format(familyname=familyNameNoWhitespace,
                                             stylename=styleNameNoWhitespace)

        if font.sfntVersion == '\x00\x01\x00\x00':  # TTF
            _out_name = '{}.ttf.ttx'.format(_out_ttx_name)
        elif font.sfntVersion == 'OTTO':  # OTF
            _out_name = '{}.otf.ttx'.format(_out_ttx_name)

        run("cp '{}' '{}'".format(_ttx_path, _out_src), cwd=_out, log=log)
        run("mv '{ttx_name}.ttx' '{out_name}'".format(ttx_name=_ttx_name,
                                                      out_name=_out_name),
            cwd=_out_src, log=log)
        run("ttx {}".format(_out_name), cwd=_out_src, log=log)
        if font.sfntVersion == '\x00\x01\x00\x00':  # TTF
            run("mv {0}.ttf.ttf {0}.ttf".format(_out_ttx_name),
                cwd=_out_src, log=log)
        elif font.sfntVersion == 'OTTO':  # OTF
            run("mv {0}.otf.otf {0}.otf".format(_out_ttx_name),
                cwd=_out_src, log=log)

        if font.sfntVersion == 'OTTO':  # OTF
            scripts_folder = op.join(app.config['ROOT'], 'scripts')
            cmd = ("python autoconvert.py '{out_src}{ttx_name}.otf'"
                   " '{out}{ttx_name}.ttf'")
            cmd = cmd.format(out_src=_out_src,
                             ttx_name=_out_ttx_name,
                             out=_out)
            run(cmd, cwd=scripts_folder, log=log)
        else:
            run("mv '{0}.ttf' '../{0}.ttf'".format(_out_ttx_name),
                _out_src, log=log)


def copy_and_rename_process(project, build, log):
    """ Setup UFOs for building """
    config = project.config

    param = {'login': project.login, 'id': project.id,
             'revision': build.revision, 'build': build.id}

    _user = joinroot('%(login)s/' % param)
    _in = joinroot('%(login)s/%(id)s.in/' % param)
    _out = joinroot('%(login)s/%(id)s.out/%(build)s.%(revision)s/' % param)

    if project.source_files_type == 'ufo':
        copy_ufo_files(project, build, log)
    else:
        copy_ttx_files(project, build, log)

    # Copy licence file
    # TODO: Infer license type from filename
    # TODO: Copy file based on license type
    if config['state'].get('license_file', None):
        # Set _in license file name
        licenseFileInFullPath = config['state']['license_file']
        licenseFileIn = licenseFileInFullPath.split('/')[-1]
        # List posible OFL and Apache filesnames
        listOfOflFilenames = ['Open Font License.markdown', 'OFL.txt',
                              'OFL.md']
        listOfApacheFilenames = ['APACHE.txt', 'LICENSE']
        # Canonicalize _out license file name
        if licenseFileIn in listOfOflFilenames:
            licenseFileOut = 'OFL.txt'
        elif licenseFileIn in listOfApacheFilenames:
            licenseFileOut = 'LICENSE.txt'
        else:
            licenseFileOut = licenseFileIn
        # Copy license file
        _in_license = op.join(_in, licenseFileInFullPath)
        _out_license = op.join(_out, licenseFileOut)
        run('cp -a "%s" "%s"' % (_in_license, _out_license),
            cwd=_user, log=log)
    else:
        log.write('License file not copied\n', prefix='Error: ')

    # Copy FONTLOG file
    _in_fontlog = op.join(_in, 'FONTLOG.txt')
    _out_fontlog = op.join(_out, 'FONTLOG.txt')
    if op.exists(_in_fontlog) and op.isfile(_in_fontlog):
        run('cp -a "%s" "%s"' % (_in_fontlog, _out_fontlog),
            cwd=_user, log=log)
    else:
        log.write('FONTLOG.txt does not exist\n', prefix='Error: ')

    # Copy DESCRIPTION.en_us.html file
    _in_desc = op.join(_in, 'DESCRIPTION.en_us.html')
    _out_desc = op.join(_out, 'DESCRIPTION.en_us.html')
    if op.exists(_in_desc) and op.isfile(_in_desc):
        run('cp -a "%s" "%s"' % (_in_desc, _out_desc), cwd=_user, log=log)
    else:
        log.write(('DESCRIPTION.en_us.html does not exist upstream, '
                   'will generate one later\n'), prefix='Error: ')

    # Copy METADATA.json file
    _in_meta = op.join(_in, 'METADATA.json')
    _out_meta = op.join(_out, 'METADATA.json')
    if op.exists(_in_meta) and op.isfile(_in_meta):
        run('cp -a "%s" "%s"' % (_in_meta, _out_meta), cwd=_user, log=log)
    else:
        log.write(('METADATA.json does not exist upstream, '
                   'will generate one later\n'), prefix='Error: ')

    # Copy any txt files selected by user
    if config['state'].get('txt_files_copied', None):
        for filename in config['state']['txt_files_copied']:
            _in_file = op.join(_in, filename)
            _out_file = op.join(_out, filename)
            run('cp -a "%s" "%s"' % (_in_file, _out_file), cwd=_user, log=log)


def ttfautohint_process(project, build, log):
    """
    Run ttfautohint with project command line settings for each
    ttf file in result src folder, outputting them in the _out root,
    or just copy the ttfs there.
    """
    # $ ttfautohint -l 7 -r 28 -G 0 -x 13 -w "" \
    #               -W -c original_font.ttf final_font.ttf
    config = project.config

    param = {'login': project.login, 'id': project.id,
             'revision': build.revision, 'build': build.id}

    _out = joinroot('%(login)s/%(id)s.out/%(build)s.%(revision)s/' % param)

    if config['state'].get('ttfautohint', None):
        log.write('Autohint TTFs (ttfautohint)\n', prefix='### ')
        params = config['state']['ttfautohint']
        os.chdir(_out)
        for name in glob.glob("*.ttf"):
            name = name[:-4]  # cut .ttf
            run("mv '{name}.ttf' '{name}.autohint.ttf'".format(name=name),
                cwd=_out, log=log)
            cmd = ("ttfautohint {params} '{name}.autohint.ttf' "
                   "'{name}.ttf'").format(params=params, name=name)
            run(cmd, cwd=_out, log=log)
            run("rm '{name}.autohint.ttf'".format(name=name),
                cwd=_out, log=log)


def ttx_process(project, build, log):
    """ Roundtrip TTF files through TTX to compact their filesize """
    param = {'login': project.login, 'id': project.id,
             'revision': build.revision, 'build': build.id}

    _out = joinroot('%(login)s/%(id)s.out/%(build)s.%(revision)s/' % param)
    _out_src = joinroot(('%(login)s/%(id)s.out/'
                         '%(build)s.%(revision)s/sources/') % param)

    log.write('Compact TTFs with ttx\n', prefix='### ')

    os.chdir(_out_src)
    for name in glob.glob("*.ufo"):
        name = name[:-4]  # cut .ufo
        filename = op.join(_out, name)
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


def execute_pyftsubset(subset, name, _out, glyphs="", log=None, args=""):
    cmd = ("pyftsubset %(out)s.ttf %(glyphs)s"
           " --notdef-outline --recommended-glyphs"
           " --name-IDs='*' --hinting")
    if args:
        cmd += " " + args
    cmd = cmd % {'glyphs': glyphs.replace('\n', ' '),
                 'out': op.join(_out, name)}
    run(cmd, cwd=_out, log=log)
    cmd = 'mv %(out)s.ttf.subset %(out)s.%(subset)s'
    run(cmd % {'subset': subset, 'out': op.join(_out, name)},
        cwd=_out, log=log)


def subset_process(project, build, log):
    config = project.config

    param = {'login': project.login, 'id': project.id,
             'revision': build.revision, 'build': build.id}

    _out = joinroot('%(login)s/%(id)s.out/%(build)s.%(revision)s/' % param)
    _out_src = joinroot(('%(login)s/%(id)s.out/'
                         '%(build)s.%(revision)s/sources/') % param)

    log.write('Subset TTFs (pyftsubset)\n', prefix='### ')

    for subset in config['state']['subset']:
        glyphs = open(SubsetExtension.get_subset_path(subset)).read()
        os.chdir(_out_src)
        for name in list(glob.glob("*.ufo")) + list(glob.glob("*.ttx")):
            if name.endswith('.ttx') and project.source_files_type == 'ttx':
                # after copy_ttx_files executed in source directory
                # resulted truetype files does have double extension
                # e.g. FontFamily-WeightStyle.ttf.ttx
                name = name[:-4]

            name = name[:-4]  # cut .ufo|.ttx
            execute_pyftsubset(subset, name, _out, glyphs=glyphs, log=log)

            # create menu subset
            execute_pyftsubset('menu', name, _out, log=log,
                               args='--text="%s"' % op.basename(name))
    # remove +latin from the subset name
    os.chdir(_out)
    files = glob.glob('*+latin*')
    for filename in files:
        newfilename = filename.replace('+latin', '')
        run("mv \"%s\" \"%s\"" % (filename, newfilename), cwd=_out, log=log)


def generate_metadata_process(project, build, log):
    """ Generate METADATA.json using genmetadata.py """
    from .app import app
    param = {'login': project.login, 'id': project.id,
             'revision': build.revision, 'build': build.id}

    _out = joinroot('%(login)s/%(id)s.out/%(build)s.%(revision)s/' % param)

    cmd = "python %(wd)s/scripts/genmetadata.py '%(out)s'"
    log.write('Generate METADATA.json (genmetadata.py)\n', prefix='### ')
    run(cmd % {'wd': app.config['ROOT'], 'out': _out}, cwd=_out, log=log)


def fontaine_process(project, build, log):
    """ Run pyFontaine on ttf files """
    param = {'login': project.login, 'id': project.id,
             'revision': build.revision, 'build': build.id}

    _out = joinroot('%(login)s/%(id)s.out/%(build)s.%(revision)s/' % param)

    log.write('pyFontaine (fontaine/main.py)\n', prefix='### ')
    os.chdir(_out)
    files = glob.glob('*.ttf')
    for file in files:
        cmd = "pyfontaine --text '%s' >> 'sources/fontaine.txt'" % file
        try:
            run(cmd, cwd=_out, log=log)
        except StandardError:
            log.write('PyFontaine raised exception. Check latest version.\n')
            # Ignore pyfontaine if it raises error
            pass
    # TODO also save the totals for the dashboard....
    #   log.write('Running Fontaine on Results\n', prefix='### ')
    #   fonts = utils.project_fontaine(project)
    #   project.config['state']['fontaine'] = fonts
    #   project.save_state()


# register yaml serializer for tests result objects.


def repr_testcase(dumper, data):
    def method_doc(doc):
        if doc is None:
            return 'None'
        else:
            return " ".join(doc.encode('utf-8', 'xmlcharrefreplace').split())
    return dumper.represent_mapping(u'tag:yaml.org,2002:map', {
        'methodDoc': method_doc(data._testMethodDoc),
        'tool': data.tool,
        'name': data.name,
        'methodName': data._testMethodName,
        'targets': data.targets,
        'tags': getattr(data, data._testMethodName).tags,
        'err_msg': getattr(data, '_err_msg', '')
    })

yaml.SafeDumper.add_multi_representer(BakeryTestCase, repr_testcase)


def get_sources_lists(rootpath):
    """ Return list of lists of UFO, TTX and METADATA.json """
    ufo_dirs = []
    ttx_files = []
    metadata_files = []
    l = len(rootpath)
    for root, dirs, files in os.walk(rootpath):
        for f in files:
            fullpath = op.join(root, f)
            if op.splitext(fullpath[l:])[1].lower() in ['.ttx', ]:
                ttx_files.append(fullpath[l:])
            if f.lower() == 'metadata.json':
                metadata_files.append(fullpath[:l])
        for d in dirs:
            fullpath = op.join(root, d)
            if op.splitext(fullpath)[1].lower() == '.ufo':
                ufo_dirs.append(fullpath[l:])
    return ufo_dirs, ttx_files, metadata_files


def upstream_revision_tests(project, revision):
    """ This function run upstream tests set on
    project.config['local']['ufo_dirs'] set in selected git revision.
    This mean that success (aka getting any result) should be occasional
    particular case. Because data and
    set of folders are changing during font development process.

    :param project: Project instance
    :param revision: Git revision
    :param force: force to make tests again
    :return: dictionary with serialized tests results formatted
             by `repr_testcase`
    """
    param = {'login': project.login, 'id': project.id, 'revision': revision}

    _in = joinroot('%(login)s/%(id)s.in/' % project)
    _out_folder = joinroot('%(login)s/%(id)s.out/utests/' % param)
    _out_yaml = op.join(_out_folder, '%(revision)s.yaml' % param)

    if op.exists(_out_yaml):
        return yaml.safe_load(open(_out_yaml, 'r'))

    if not op.exists(_out_folder):
        os.makedirs(_out_folder)

    result = {}
    os.chdir(_in)
    prun("git checkout %s" % revision, cwd=_in)

    result[project.clone] = run_set(_in, 'upstream-repo')

    ufo_dirs, ttx_files, metadata_files = get_sources_lists(_in)

    for font in ufo_dirs:
        if op.exists(op.join(_in, font)):
            result[font] = run_set(op.join(_in, font), 'upstream')

    for metadata_path in metadata_files:
        result[metadata_path] = run_set(metadata_path, 'metadata')

    for font in ttx_files:
        if op.exists(op.join(_in, font)):
            result[font] = run_set(op.join(_in, font), 'upstream-ttx')

    result['Consistency fonts'] = run_set(_in, 'consistency')

    l = codecs.open(_out_yaml, mode='w', encoding="utf-8")
    l.write(yaml.safe_dump(result))
    l.close()

    return yaml.safe_load(open(_out_yaml, 'r'))


def result_tests(project, build, log=None):
    param = {'login': project.login, 'id': project.id,
             'revision': build.revision, 'build': build.id}

    _out_src = joinroot('%(login)s/%(id)s.out/%(build)s.%(revision)s/' % param)
    path = '%(login)s/%(id)s.out/%(build)s.%(revision)s.rtests.yaml' % param
    _out_yaml = joinroot(path)

    if op.exists(_out_yaml):
        return yaml.safe_load(open(_out_yaml, 'r'))

    result = {}
    os.chdir(_out_src)
    for font in glob.glob("*.ttf"):
        result[font] = run_set(op.join(_out_src, font), 'result', log=log)

    if not result:
        return

    # Comment during debug
    l = open(_out_yaml, 'w')
    l.write(yaml.safe_dump(result))
    l.close()

    d = yaml.safe_load(open(_out_yaml, 'r'))
    # os.remove(_out_yaml)
    return d


def result_fixes(project, build, log=None):
    from .app import app
    param = {'login': project.login, 'id': project.id,
             'revision': build.revision, 'build': build.id}

    _out_src = op.join(app.config['DATA_ROOT'],
                       '%(login)s/%(id)s.out/%(build)s.%(revision)s/' % param)
    _out_yaml = op.join(app.config['DATA_ROOT'],
                        ('%(login)s/%(id)s.out/'
                         '%(build)s.%(revision)s.rtests.yaml') % param)

    fix_font(_out_yaml, _out_src, log=log)


def discover_dashboard(project, build, log):
    from .app import app
    param = {'login': project.login, 'id': project.id,
             'revision': build.revision, 'build': build.id}

    _yaml = op.join(app.config['DATA_ROOT'],
                    '%(login)s/%(id)s.bakery.yaml' % param)

    _out_src = op.join(app.config['DATA_ROOT'],
                       ('%(login)s/%(id)s.out/'
                        '%(build)s.%(revision)s/') % param)

    cmd = "python {wd}/scripts/discovery.py '{out}' '{yaml}'".format(
        wd=app.config['ROOT'], out=_out_src, yaml=_yaml)
    log.write('Discovery Dashboard data\n', prefix='### ')
    run(cmd, cwd=_out_src, log=log)


@job
def process_project(project, build, revision, force_sync=False):
    """
    Bake the project, building all fonts according to the project setup.

    :param project: :class:`~bakery.models.Project` instance
    :param log: :class:`~bakery.utils.RedisFd` as log
    """
    from .app import app, db
    if force_sync:
        project_git_sync(project)

    param = {'login': project.login, 'id': project.id,
             'revision': build.revision, 'build': build.id}
    _in = joinroot('%(login)s/%(id)s.in/' % param)
    _out_src = op.join(app.config['DATA_ROOT'],
                       ('%(login)s/%(id)s.out/'
                        '%(build)s.%(revision)s/sources/') % param)
    _out_log = op.join(app.config['DATA_ROOT'],
                       ('%(login)s/%(id)s.out/'
                        '%(build)s.%(revision)s.process.log') % param)

    # Make logest path
    os.makedirs(_out_src)

    log = RedisFd(_out_log, 'w')

    # setup is set after 'bake' button is first pressed

    if project.config['local'].get('setup', None):
        # this code change upstream repository
        try:
            run("git checkout %s" % revision, cwd=_in, log=log)
            log.write('Bake Begins!\n', prefix='### ')
            copy_and_rename_process(project, build, log)
            ttfautohint_process(project, build, log)
            ttx_process(project, build, log)
            subset_process(project, build, log)
            generate_metadata_process(project, build, log)
            fontaine_process(project, build, log)
            # result_tests doesn't needed here, but since it is anyway
            # background task make cache file for future use
            result_tests(project, build, log)
            # apply fixes
            result_fixes(project, build, log)
            # discover_dashboard(project, build, log)
            log.write('Bake Succeeded!\n', prefix='### ')

            # zip out folder with revision
            param = {'login': project.login, 'id': project.id,
                     'revision': build.revision, 'build': build.id}
            _out_src = op.join(app.config['DATA_ROOT'],
                               ('%(login)s/%(id)s.out/'
                                '%(build)s.%(revision)s') % param)
            _out_url = app.config['DATA_URL'] + '%(login)s/%(id)s.out' % param
            zipdir(_out_src, _out_url, log)
        finally:
            # save that project is done
            build.is_done = True
            db.session.add(build)
            db.session.commit()

    log.close()


@job
def process_description_404(project, build):
    """ Background task to check links in DESCRIPTION.en_us.html file

        This method generates yaml file `*.*.404links.yaml` inside
        repo out directory. """
    param = {'login': project.login, 'id': project.id,
             'revision': build.revision, 'build': build.id}
    _out = joinroot('%(login)s/%(id)s.out/%(build)s.%(revision)s/' % param)
    path = op.join(_out, 'DESCRIPTION.en_us.html')

    _out_yaml = joinroot('%(login)s/%(id)s.out/%(build)s.%(revision)s.404links.yaml' % param)

    result = {}
    test_results = run_set(path, 'description')
    result = parse_test_results(test_results)
    result['updated'] = datetime.datetime.now()

    # Comment during debug
    l = open(_out_yaml, 'w')
    l.write(yaml.safe_dump(result))
    l.close()

    d = yaml.safe_load(open(_out_yaml, 'r'))
    # os.remove(_out_yaml)
    return d


def zipdir(path, url, log):
    import zipfile
    basename = op.basename(path)
    zipfile_path = op.join(path, '..', '%s.zip' % basename)
    zipf = zipfile.ZipFile(zipfile_path, 'w')
    for root, dirs, files in os.walk(path):
        root = root.replace(path, '').lstrip('/')
        for file in files:
            arcpath = op.join(basename, root, file)
            zipf.write(op.join(root, file), arcpath)
            log.write('add %s\n' % arcpath)
    zipf.close()
    log.write('### Link to archive [%s.zip](%s/%s.zip)\n' % (basename,
                                                             url, basename))


def set_done(build):
    """ Set done flag for build """
    from .app import db
    build.is_done = True
    db.session.add(build)
    db.session.commit()
