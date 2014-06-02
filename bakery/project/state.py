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

import fontforge
import os
import re
import yaml
# from flask import current_app
from fontTools.ttLib import TTFont
from bakery.app import app


def walkWithoutGit(path):
    """
    Recursively walk a file system path, excluding .git folders

    :param path: path to walk down

    Returns:
        dictionary: Dictionary of file and directory strings
    """
    dictionary = {}
    currentDirectory = os.path.abspath(path)
    fileList = os.listdir(path)
    for fileName in fileList:
        currentFileName = os.path.join(currentDirectory, fileName)
        if os.path.isfile(currentFileName):
            dictionary[fileName] = {}
        elif os.path.isdir(currentFileName) and not currentFileName.endswith('.git'):
            dictionary[fileName] = walkWithoutGit(currentFileName)
    return dictionary


def load_yaml(default_yml, yml=None):
    """
    Load a YAML file.

    :param default_yml: a YAML file that may have all possible keys with default values
    :param yml: a YAML file with new values that overwrite those from the default_yml file (optional)

    Returns:
        data: the data from the YAML files
    """
    data = yaml.load(open(default_yml, 'r').read())
    if yml:
        data.update(yaml.load(open(yml, 'r').read()))
    return data


def project_state_get(project, refresh=False):  # XXX rename refresh throughout codebase to refresh_bakeryStateInternal ?
    """
    Get internal and external state of project from default, repo and local YAML files,
    check external state matches that stored in the _in repo, and
    save these states to local YAML files.

    :param project: :class:`~bakery.models.Project` instance
    :param refresh: Optional. Boolean. Force refreshing the internal state

    Returns:
        local: the internal state of the project
        state: the external state of the project
    """
    _in = os.path.join(app.config['DATA_ROOT'], '%(login)s/%(id)s.in/' % project)
    # Define bakery.yaml locations
    bakery_default_yml = os.path.join(app.config['ROOT'], 'bakery', 'bakery.defaults.yaml')
    bakery_project_yml = os.path.join(app.config['DATA_ROOT'], '%(login)s/%(id)s.in/bakery.yaml' % project)
    bakery_local_yml = os.path.join(app.config['DATA_ROOT'], '%(login)s/%(id)s.bakery.yaml' % project)
    # Define state.yaml locations
    state_default_yml = os.path.join(app.config['ROOT'], 'bakery', 'state.defaults.yaml')
    state_local_yml = os.path.join(app.config['DATA_ROOT'], '%(login)s/%(id)s.state.yaml' % project)

    # Create internal state object, 'local'
    # TODO? rename this throughout codebase to bakeryStateInternal
    # if local is already set up, load it from file, otherwise load
    # from defaults and set it up later
    if os.path.exists(state_local_yml):
        local = load_yaml(state_default_yml, state_local_yml)
    else:
        local = load_yaml(state_default_yml)
        refresh = True

    # Create external state object, 'state'
    # TODO? rename this throughout codebase to bakeryState
    # try to load the local bakery.yml from any previous runs
    # and note that it was loaded
    if os.path.exists(bakery_local_yml):
        state = load_yaml(bakery_default_yml, bakery_local_yml)
        local['status'] = 'local'
    # if it doesn't exist, try to load a bakery.yml from _in repo and note that it was loaded
    elif os.path.exists(bakery_project_yml):
        state = load_yaml(bakery_default_yml, bakery_project_yml)
        local['status'] = 'repo'
    # if neither exist, just load bakery.defaults.yaml and note that it was loaded
    else:
        state = load_yaml(bakery_default_yml)
        local['status'] = 'default'

    # note if both local and _in repo bakery.yaml files are in sync
    if os.path.exists(bakery_project_yml) and os.path.exists(bakery_local_yml):
        import filecmp
        local['bakery_yaml_in_sync'] = filecmp.cmp(bakery_project_yml, bakery_local_yml, shallow=False)

    # If local is already set up, save both states to YAML files and return them
    if not refresh:
        project_state_save(project, state, local)
        return state, local

    # otherwise, list txt and ufo files found in _in
    txt_files = []
    bin_files = []
    ufo_dirs = []
    ttx_files = []
    l = len(_in)
    for root, dirs, files in os.walk(_in):
        for f in files:
            fullpath = os.path.join(root, f)
            if os.path.splitext(fullpath)[1].lower() in ['.txt', '.md', '.markdown', 'LICENSE']:
                txt_files.append(fullpath[l:])
            if os.path.splitext(fullpath)[1].lower() in ['.ttf', '.otf']:
                bin_files.append(fullpath[l:])
            if os.path.splitext(fullpath)[1].lower() in ['.ttx', ]:
                ttx_files.append(fullpath[l:])
        for d in dirs:
            fullpath = os.path.join(root, d)
            if os.path.splitext(fullpath)[1].lower() == '.ufo':
                ufo_dirs.append(fullpath[l:])

    local['txt_files'] = txt_files
    local['bin_files'] = bin_files
    local['ufo_dirs'] = ufo_dirs
    local['ttx_files'] = ttx_files

    # If license_file not defined then choose OFL.txt or LICENSE.txt from the root of repo, if it exists
    lfn = state['license_file']
    if not lfn:
        for fn in ['OFL.txt', 'LICENSE.txt']:  # order means priority
            ffn = os.path.join(_in, fn)
            if os.path.exists(ffn) and os.path.isfile(ffn):
                state['license_file'] = fn
                break
    # and note it exists
    if os.path.exists(lfn) and os.path.isfile(lfn):
        local['license_file_found'] = True

    project_state_autodiscovery(project, state)

    # Save both states to YAML files and return them
    if project.is_ready:
        project_state_save(project, state, local)
    return state, local


def license_filter(licenses, files):
    return filter(lambda fn: os.path.basename(fn).lower() in licenses, files)


def nameTableRead(font, NameID, fallbackNameID=False):
    for record in font['name'].names:
        if record.nameID == NameID:
            if b'\000' in record.string:
                return record.string.decode('utf-16-be').encode('utf-8')
            else:
                return record.string

    if fallbackNameID:
        return nameTableRead(font, fallbackNameID)

    return ''


class StateAutodiscover:

    OFL = ['open font license.markdown', 'ofl.txt', 'ofl.md']
    LICENSE = ['license.txt', 'license.md', 'copyright.txt']
    APACHE = ['apache.txt', 'apache.md']
    UFL = ['ufl.txt', 'ufl.md']
    TRADEMARKS = ['trademarks.txt']

    COPYRIGHT_REGEX = re.compile(r'Copyright \(c\) \d{4}.*', re.U | re.I)
    RFN_REGEX = re.compile(r'with Reserved Font Names.*', re.U | re.I)

    TRADEMARK_PERMREGEX = re.compile(r'Permission is granted to Google, Inc', re.I | re.U)
    TRADEMARK_REGEX = re.compile(r'.* (is a|are registered) trademarks? .*', re.U | re.I)

    def __init__(self, folder, default_state=None):
        self.files = []
        for dirpath, dirnames, filenames in os.walk(folder):
            self.files.extend(map(lambda fn: os.path.join(dirpath, fn), filenames))

        self.licenses = license_filter(StateAutodiscover.LICENSE, self.files)
        self.ofl_licenses = license_filter(StateAutodiscover.OFL, self.files)
        self.apache_licenses = license_filter(StateAutodiscover.APACHE, self.files)
        self.ufl_licenses = license_filter(StateAutodiscover.UFL, self.files)
        self.trademarks = license_filter(StateAutodiscover.TRADEMARKS, self.files)

        self.all_licenses = self.licenses + self.ofl_licenses + self.apache_licenses + self.ufl_licenses
        self.ottffiles = filter(lambda fn: os.path.splitext(fn)[1].lower() in ['.ttf', '.otf'], self.files)

        self.default_state = default_state

    def copyright_license(self):
        """ Returns license of project.

            Looking for license files OFL.txt, APACHE.txt, UFL.txt. If they
            do not exist it reads file LICENSE and check for license
            string patterns.
        """
        if self.default_state and self.default_state.get('copyright_license'):
            return self.default_state.get('copyright_license')
        if self.ofl_licenses:
            return 'ofl'
        if self.apache_licenses:
            return 'apache'
        if self.ufl_licenses:
            return 'ufl'
        for license in self.licenses:
            # read license file and search for template
            # for OFL, APACHE or UFL
            contents = open(license).read()
            if contents.lower().find('open font license version 1.1'):
                return 'ofl'
            elif contents.lower().find('apache license, version 2.0'):
                return 'apache'
            elif contents.lower().find('ubuntu font licence version 1.0'):
                return 'ufl'
        return 'undetected' if self.licenses else ''

    def copyright_notice(self):
        """ Returns copyright notice of project.

            This method looks for copyright string pattern. First all licenses
            are being looked for. If no pattern found in it looks for existing
            otf and ttf files.
        """
        if self.default_state and self.default_state.get('copyright_notice'):
            return self.default_state.get('copyright_notice')
        for license in self.all_licenses:
            contents = open(license).read()
            match = StateAutodiscover.COPYRIGHT_REGEX.search(contents)
            if not match:
                continue
            return match.group(0).strip(',\r\n')

        for ottf in self.ottffiles:
            contents = nameTableRead(TTFont(ottf), 0).strip()
            if not contents:
                continue
            match = StateAutodiscover.COPYRIGHT_REGEX.search(contents)
            if not match:
                continue
            return match.group(0).strip(',\r\n')

    def rfn_asserted(self):
        """ Returns 'yes' if licenses contains any references
            to Reserved Font Name.
        """
        if self.default_state and self.default_state.get('rfn_asserted'):
            return self.default_state.get('rfn_asserted')
        for license in self.all_licenses:
            contents = open(license).read()
            match = StateAutodiscover.RFN_REGEX.search(contents)
            if not match:
                continue
            return 'yes'
        for ottf in self.ottffiles:
            contents = nameTableRead(TTFont(ottf), 0) or ''
            match = StateAutodiscover.RFN_REGEX.search(contents)
            if not match:
                continue
            return 'yes'
        return 'no'

    def rfn_permission(self):
        """ Returns trademark notice of project. """
        if self.default_state and self.default_state.get('rfn_permission'):
            return self.default_state.get('rfn_permission')
        for tm_path in self.trademarks:
            return bool('reserved font name' in open(tm_path).read().lower())
        for ottf in self.ottffiles:
            contents = nameTableRead(TTFont(ottf), 7) or ''
            return bool('reserved font name' in contents)
        return False

    def trademark_notice(self):
        """ Returns trademark notice of project. """
        if self.default_state and self.default_state.get('trademark_notice'):
            return self.default_state.get('trademark_notice')
        for tm_path in self.trademarks:
            match = StateAutodiscover.TRADEMARK_REGEX.search(open(tm_path).read())
            if not match:
                continue
            return match.group(0).strip(',\r\n')
        for ottf in self.ottffiles:
            contents = nameTableRead(TTFont(ottf), 7) or ''
            match = StateAutodiscover.TRADEMARK_REGEX.search(contents)
            if not match:
                continue
            return match.group(0).strip(',\r\n')
        return ''

    def trademark_permission(self):
        for filepath in self.trademarks:
            match = StateAutodiscover.TRADEMARK_PERMREGEX.search(open(filepath).read())
            if not match:
                continue
            return match.group(0).strip(',\r\n')
        for ottf in self.ottffiles:
            contents = nameTableRead(TTFont(ottf), 7) or ''
            match = StateAutodiscover.TRADEMARK_PERMREGEX.search(contents)
            if not match:
                continue
            return match.group(0).strip(',\r\n')
        return ''

    def source_cff_filetype(self):
        cff_fyletypes = []
        for filename in self.files:
            fn, ext = os.path.splitext(filename)
            if fn.lower().endswith('-otf'):
                cff_fyletypes.append(ext.upper().strip('.'))
        # in bakery.yaml store list of extensions separated by comma
        return ', '.join(list(set(cff_fyletypes)))

    def source_drawing_filetype(self):
        # a source file with filename ending in -.* in the repo
        ttf_fyletypes = []
        for filename in self.files:
            fn, ext = os.path.splitext(filename)
            if fn.lower().endswith('-ttf'):
                ttf_fyletypes.append(ext.upper().strip('.'))
        # in bakery.yaml store list of extensions separated by comma
        return ', '.join(list(set(ttf_fyletypes)))

    def source_ttf_filetype(self):
        # a source file with filename ending in -.* in the repo
        ttf_fyletypes = []
        for filename in self.files:
            fn, ext = os.path.splitext(filename)
            if fn.lower().endswith('-ttf'):
                ttf_fyletypes.append(ext.upper().strip('.'))
        # in bakery.yaml store list of extensions separated by comma
        return ', '.join(list(set(ttf_fyletypes)))

    def check_for_ttfautohint_glyph(self, fontpath):
        font = fontforge.open(fontpath)
        is_existed = bool('.ttfautohint' in font)
        font.close()
        return is_existed

    def hinting_level(self):
        if filter(lambda fn: os.path.basename(fn) == '.ttfautohint', self.files):
            return '4'

        for ottf in self.ottffiles:
            # Searches for .ttfautohint glyph inside. If glyph exists
            # then returns hinting_level to '3'
            is_glyph_existed = self.check_for_ttfautohint_glyph(ottf)
            if is_glyph_existed:
                return '4'
            ttfont = TTFont(ottf)
            try:
                if ttfont.getTableData("prep") is None:
                    return '2'
            except KeyError:
                return '2'
            prepAsm = ttfont.getTableData("prep")
            prepText = fontforge.unParseTTInstrs(prepAsm)
            prepMagic = "PUSHW_1\n 511\nSCANCTRL\nPUSHB_1\n 4\nSCANTYPE"
            if prepText.strip() == prepMagic:
                return '2'
        return '1'


def project_state_autodiscovery(project, state):
    """
    Tries to autodiscovery project properties and save it to bakery.yaml.

    :param project: :class:`~bakery.models.Project` instance
    :param state: The external state of this project.
    """
    projectdir = os.path.join(app.config['DATA_ROOT'], '%(login)s/%(id)s.in' % project)

    autodiscover = StateAutodiscover(projectdir, default_state=state)
    state['copyright_license'] = autodiscover.copyright_license()
    state['copyright_notice'] = autodiscover.copyright_notice()
    state['rfn_asserted'] = autodiscover.rfn_asserted()
    state['rfn_permission'] = str(autodiscover.rfn_permission())
    state['trademark_notice'] = autodiscover.trademark_notice()
    state['trademark_permission'] = autodiscover.trademark_permission()
    state['source_cff_filetype'] = autodiscover.source_cff_filetype()
    state['source_drawing_filetype'] = autodiscover.source_drawing_filetype()
    state['source_ttf_filetype'] = autodiscover.source_ttf_filetype()
    state['hinting_level'] = autodiscover.hinting_level()
    return state


def project_state_save(project, state=None, local=None):
    """
    Save project state in bakery.yaml and state.yaml files.

    :param project: :class:`~bakery.models.Project` instance
    :param state: Optional, the external state of this project. If not given, will be loaded from project
    :param local: Optional, the internal state of this project. If not given, will be loaded from project
    """
    if not state:
        state = project.config['state']
    if not local:
        local = project.config['local']

    bakery_local_yml = os.path.join(app.config['DATA_ROOT'], '%(login)s/%(id)s.bakery.yaml' % project)
    state_local_yml = os.path.join(app.config['DATA_ROOT'], '%(login)s/%(id)s.state.yaml' % project)

    f = open(bakery_local_yml, 'w')
    f.write(yaml.safe_dump(state))
    f.close()

    l = open(state_local_yml, 'w')
    l.write(yaml.safe_dump(local))
    l.close()
