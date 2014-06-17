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

import codecs
import datetime
import fontforge
import glob
import os
import os.path as op
import plistlib
import re
import shutil
import yaml

from checker import run_set, parse_test_results
from checker.base import BakeryTestCase
from fixer import fix_font
from flask.ext.rq import job
from fontTools import ttLib
from fontaine.ext.subsets import Extension as SubsetExtension

from .utils import RedisFd, run, prun


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


def get_subsets_coverage_data(source_fonts_paths, log=None):
    """ Return dictionary with subsets coverages as a value
        and common name as a key """
    from fontaine.font import FontFactory
    from fontaine.cmap import Library
    library = Library(collections=['subsets'])
    subsets = {}
    for fontpath in source_fonts_paths:
        try:
            font = FontFactory.openfont(fontpath)
        except AssertionError, ex:
            if log:
                log.write('Error: [%s] %s' % (fontpath, ex.message))
            continue
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
    subsets = get_subsets_coverage_data(source_fonts_paths, log)

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
    from bakery.app import db, app
    project.is_ready = False
    db.session.add(project)
    db.session.commit()
    db.session.refresh(project)

    _in = joinroot('%(login)s/%(id)s.in/' % project)
    _out = joinroot('%(login)s/%(id)s.out/' % project)
    if not op.exists(_out):
        os.makedirs(_out)

    try:
        os.remove(op.join(_out, 'fontaine.yml'))
    except OSError:
        pass

    try:
        os.remove(op.join(_out, 'upstream.log'))
    except OSError:
        pass

    log = RedisFd(op.join(_out, 'upstream.log'))
    # Create the incoming repo directory (_in) if it doesn't exist
    if not op.exists(_in):
        log.write('$ Create incoming %s...')
        try:
            os.makedirs(op.join(app.config['DATA_ROOT'], _in))
        except (OSError, IOError), e:
            log.write('[FAIL]\nError: %s' % e.message)
            raise e

    # Update _in if it already exists with a .git directory
    from git import Repo, InvalidGitRepositoryError
    try:
        repo = Repo(_in)
        log.write('$ git reset --hard\n')
        log.write(repo.git.reset(hard=True) + '\n')
        log.write('$ git clean --force\n')
        repo.git.clean(force=True)
        log.write('$ git pull origin master\n')
        repo.remotes.origin.pull()
    except InvalidGitRepositoryError:
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


class FontSourceAbstract(object):
    """ Abstract class to provide copy functional in baking process

        Inherited classes must implement `open_source` method
        and properties `style_name` and `family_name`. """

    def __init__(self, path, cwd, stdout_pipe=None):
        self.source = self.open_source(op.join(cwd, path))
        self.source_path = path
        self.cwd = cwd
        self.stdout_pipe = stdout_pipe

    def open_source(self, sourcepath):
        raise NotImplementedError

    @property
    def style_name(self):
        raise NotImplementedError

    @property
    def family_name(self):
        raise NotImplementedError

    def before_copy(self):
        """ If method returns False then bakery process halted. Default: True.

            Implement this if you need additional check before source
            path will be copied.

            Good practice to call inside self.stdout_pipe.write() method
            to make user know what is wrong with source. """
        return True

    def copy(self, destdir):
        destpath = op.join(destdir, self.get_file_name())

        _ = '$ Copy [and Rename] %s to %s... '
        self.stdout_pipe.write(_ % (self.source_path, op.basename(destpath)))

        if os.path.isdir(op.join(self.cwd, self.source_path)):
            try:
                shutil.copytree(op.join(self.cwd, self.source_path), destpath)
            except (OSError, IOError), ex:
                self.stdout_pipe.write('[FAIL]\nError: %s\n' % ex.message)
                raise
        else:
            try:
                shutil.copy(op.join(self.cwd, self.source_path), destpath)
            except (OSError, IOError), ex:
                self.stdout_pipe.write('[FAIL]\nError: %s\n' % ex.message)
                raise

        self.stdout_pipe.write('[OK]\n')

    def get_file_name(self):
        return self.postscript_fontname + self.source_path[-4:]

    @property
    def postscript_fontname(self):
        stylename = re.sub(r'\s', '', self.style_name)
        familyname = re.sub(r'\s', '', self.family_name)
        return "{}-{}".format(familyname, stylename)

    def after_copy(self, path_params):
        return


class UFOFontSource(FontSourceAbstract):

    def open_source(self, path):
        return plistlib.readPlist(op.join(path, 'fontinfo.plist'))

    @property
    def style_name(self):
        # Get the styleName
        style_name = self.source['styleName']
        # Always have a regular style
        if style_name == 'Normal' or style_name == 'Roman':
            style_name = 'Regular'
        return style_name

    def family_name():
        doc = "The family_name property."

        def fget(self):
            pfn = self.source.get('openTypeNamePreferredFamilyName', '')
            return (self._family_name or pfn
                    or self.source.get('familyName', ''))

        def fset(self, value):
            self._family_name = value

        def fdel(self):
            del self._family_name

        return locals()
    family_name = property(**family_name())

    def before_copy(self):
        if not self.family_name:
            self.stdout_pipe.write(('[MISSED] Please set openTypeNamePreferredFamilyName or '
                                    'familyName in %s fontinfo.plist and run another'
                                    ' bake process.') % self.source_path, prefix='### ')
            return False
        return True

    def convert_ufo2ttf(self, path_params):
        from scripts import ufo2ttf
        _ = '$ Convert %s to %s... '
        self.stdout_pipe.write(_ % (self.source_path,
                                    self.postscript_fontname + '.ttf'))

        ufopath = op.join(path_params._out_src, self.get_file_name())
        ttfpath = op.join(path_params._out, self.postscript_fontname + '.ttf')
        otfpath = op.join(path_params._out, self.postscript_fontname + '.otf')

        try:
            ufo2ttf.convert(ufopath, ttfpath, otfpath)
            self.stdout_pipe.write('[OK]\n')
        except Exception, ex:
            self.stdout_pipe.write('[FAIL]\nError: %s\n' % ex.message)

    def after_copy(self, path_params):
        # If we rename, change the font family name metadata
        # inside the _out_ufo
        if self.family_name:
            # Read the _out_ufo fontinfo.plist
            _out_ufo_path = op.join(path_params._out_src, self.get_file_name())
            _out_ufoPlist = op.join(_out_ufo_path, 'fontinfo.plist')
            _out_ufoFontInfo = plistlib.readPlist(_out_ufoPlist)
            # Set the familyName
            _out_ufoFontInfo['familyName'] = self.family_name

            # Set PS Name
            # Ref: www.adobe.com/devnet/font/pdfs/5088.FontNames.pdf‎
            # < Family Name > < Vendor ID > - < Weight > < Width >
            # < Slant > < Character Set >
            psfn = self.postscript_fontname
            _out_ufoFontInfo['postscriptFontName'] = psfn
            _out_ufoFontInfo['postscriptFullName'] = psfn.replace('-', ' ')
            # Write _out fontinfo.plist
            plistlib.writePlist(_out_ufoFontInfo, _out_ufoPlist)

        self.convert_ufo2ttf(path_params)


class TTXFontSource(FontSourceAbstract):

    @staticmethod
    def nameTableRead(font, NameID, fallbackNameID=False):
        for record in font['name'].names:
            if record.nameID == NameID:
                if b'\000' in record.string:
                    string = record.string.decode('utf-16-be')
                    return string.encode('utf-8')
                else:
                    return record.string

        if fallbackNameID:
            return TTXFontSource.nameTableRead(font, fallbackNameID)

    def open_source(self, path):
        font = ttLib.TTFont(None, lazy=False, recalcBBoxes=True,
                            verbose=False, allowVID=False)
        font.importXML(path, quiet=True)
        return font

    @property
    def style_name(self):
        # Find the style name
        style_name = TTXFontSource.nameTableRead(self.source, 17, 2)
        # Always have a regular style
        if style_name == 'Normal' or style_name == 'Roman':
            style_name = 'Regular'
        return style_name

    def family_name():
        doc = "The family_name property."

        def fget(self):
            return (self._family_name
                    or TTXFontSource.nameTableRead(self.source, 16, 1))

        def fset(self, value):
            self._family_name = value

        def fdel(self):
            del self._family_name

        return locals()
    family_name = property(**family_name())

    def compile_ttx(self, path_params):
        run("ttx {}.ttx".format(self.postscript_fontname),
            cwd=path_params._out_src,
            log=self.stdout_pipe)

    def convert_otf2ttf(self, path_params):
        _ = '$ Converting {}.otf to {}.ttf...'
        self.stdout_pipe.write(_.format(self.postscript_fontname))

        try:
            path = op.join(path_params._out_src, self.postscript_fontname + '.otf')
            font = fontforge.open(path)

            path = op.join(path_params._out, self.postscript_fontname + '.ttf')
            font.generate(path)
            self.stdout_pipe.write('[OK]\n')
        except Exception, ex:
            self.stdout_pipe.write('[FAIL]\nError: %s\n' % ex.message)

    def after_copy(self, path_params):
        out_name = self.postscript_fontname + '.ttf'

        self.compile_ttx(path_params)

        if self.source.sfntVersion == 'OTTO':  # OTF
            self.convert_otf2ttf(path_params)
        # If TTF already, move it up
        else:
            try:
                _ = '$ Move %s to ../%s...'
                self.stdout_pipe.write(_ % (out_name, out_name))
                shutil.move(op.join(path_params._out_src, out_name),
                            op.join(path_params._out, out_name))
                self.stdout_pipe.write('[OK]\n')
            except (OSError, IOError), ex:
                self.stdout_pipe.write('[FAIL]\nError: %s\n' % ex.message)


class BINFontSource(TTXFontSource):

    def open_source(self, path):
        return ttLib.TTFont(path, lazy=False, recalcBBoxes=True,
                            verbose=False, allowVID=False)

    def compile_ttx(self, path_params):
        """ Override TTXFontSource compile_ttx method as BINFontSource
            based on compiled already fonts """
        pass


class SFDFontSource(FontSourceAbstract):

    def open_source(self, path):
        return fontforge.open(path)

    def family_name():
        doc = "The family_name property."

        def fget(self):
            return self._family_name or self.source.sfnt_names[1][2]

        def fset(self, value):
            self._family_name = value

        def fdel(self):
            del self._family_name
        return locals()
    family_name = property(**family_name())

    @property
    def style_name(self):
        return self.source.sfnt_names[2][2]

    def after_copy(self, path_params):
        from scripts import ufo2ttf
        _ = '$ Convert %s to %s... '
        self.stdout_pipe.write(_ % (self.source_path,
                                    self.postscript_fontname + '.ttf'))

        ufopath = op.join(path_params._out_src, self.get_file_name())
        ttfpath = op.join(path_params._out, self.postscript_fontname + '.ttf')
        otfpath = op.join(path_params._out, self.postscript_fontname + '.otf')

        try:
            ufo2ttf.convert(ufopath, ttfpath, otfpath)
            self.stdout_pipe.write('[OK]\n')
        except Exception, ex:
            self.stdout_pipe.write('[FAIL]\nError: %s\n' % ex.message)


def get_fontsource(path, cwd, log):
    """ Returns instance of XXXFontSource class based on path extension.

        It supports only three XXXFontSource classes for the moment:

        >>> get_fontsource('test.ufo')
        <UFOFontSource instance>

        >>> get_fontsource('test.ttx')
        <TTXFontSource instance>

        >>> get_fontsource('test.ttf')
        <BINFontSource instance>

        >>> get_fontsource('test.otf')
        <BINFontSource instance>

        >>> get_fontsource('test.sfd')
        <SFDFontSource instance>
    """
    if path.endswith('.ufo'):
        return UFOFontSource(path, cwd, log)
    elif path.endswith('.ttx'):
        return TTXFontSource(path, cwd, log)
    elif path.endswith('.ttf') or path.endswith('.otf'):
        return BINFontSource(path, cwd, log)
    elif path.endswith('.sfd'):
        return SFDFontSource(path, cwd, log)
    else:
        log.write('[MISSED] Unsupported sources file: %s\n' % path,
                  prefix='Error: ')


def process_copy(path, path_params, family_name, log):
    fontsource = get_fontsource(path, path_params._in, log)
    fontsource.family_name = family_name  # initial family name

    if not fontsource.before_copy():
        return

    fontsource.copy(path_params._out_src)

    fontsource.after_copy(path_params)
    return fontsource


class PathParam:

    def __init__(self, project, build):
        param = {'login': project.login, 'id': project.id,
                 'revision': build.revision, 'build': build.id}

        self._in = joinroot('%(login)s/%(id)s.in/' % param)
        self._out = joinroot('%(login)s/%(id)s.out/%(build)s.%(revision)s/' % param)

        path = '%(login)s/%(id)s.out/%(build)s.%(revision)s/sources/' % param
        self._out_src = joinroot(path)


def copy_and_rename_process(project, build, log):
    """ Setup UFOs for building """
    config = project.config

    param = {'login': project.login, 'id': project.id,
             'revision': build.revision, 'build': build.id}

    _user = joinroot('%(login)s/' % param)
    _in = joinroot('%(login)s/%(id)s.in/' % param)
    _out = joinroot('%(login)s/%(id)s.out/%(build)s.%(revision)s/' % param)

    path_params = PathParam(project, build)
    for x in config['state'].get('process_files', []):
        process_copy(x, path_params, config['state'].get('familyname', None),
                     log)

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
           " --notdef-outline --name-IDs='*' --hinting")
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

    log.write('pyFontaine TTFs\n', prefix='### ')
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

    git_checkout(_in, revision)

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


def git_checkout(path, revision, log=None):
    try:
        from git import Repo, InvalidGitRepositoryError
        repo = Repo(path)
        repo.git.checkout(revision)
        if log:
            log.write("git checkout %s\n" % revision)
    except InvalidGitRepositoryError:
        pass


@job
def process_project(project, build, revision, force_sync=False):
    """
    Bake the project, building all fonts according to the project setup.

    :param project: :class:`~bakery.models.Project` instance
    :param log: :class:`~bakery.utils.RedisFd` as log
    """
    from bakery.app import app
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
        git_checkout(_in, revision, log)

        # this code change upstream repository
        try:
            # run("git checkout %s" % revision, cwd=_in, log=log)
            log.write('Bake Begins!\n', prefix='# ')
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
            # zip out folder with revision
            # TODO: move these variable definitions inside zipdir() so they are the same as other bake methods
            _out_src = op.join(app.config['DATA_ROOT'],
                               ('%(login)s/%(id)s.out/'
                                '%(build)s.%(revision)s') % param)
            _out_url = app.config['DATA_URL'] + '%(login)s/%(id)s.out' % param
            zipdir(_out_src, _out_url, log)
        finally:
            # save that project is done
            set_done(build)
            log.write('Bake Succeeded!\n', prefix='# ')

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
    log.write('#### Link to archive [%s.zip](%s/%s.zip)\n' % (basename,
                                                             url, basename))


def set_done(build):
    """ Set done flag for build """
    from bakery.app import db
    build.is_done = True
    db.session.add(build)
    db.session.commit()
