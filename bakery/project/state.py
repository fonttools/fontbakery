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

import yaml
import os
# from flask import current_app

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..'))
DATA_ROOT = os.path.join(ROOT, 'data')

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


def load_yaml(default_yml, yml = None):
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

def project_state_get(project, refresh = False): # XXX rename refresh throughout codebase to refresh_bakeryStateInternal ?
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
    _in = os.path.join(DATA_ROOT, '%(login)s/%(id)s.in/' % project)
    _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/' % project)
    # Define bakery.yaml locations
    bakery_default_yml = os.path.join(ROOT, 'bakery', 'bakery.defaults.yaml')
    bakery_project_yml = os.path.join(DATA_ROOT, '%(login)s/%(id)s.in/bakery.yaml' % project)
    bakery_local_yml = os.path.join(DATA_ROOT, '%(login)s/%(id)s.bakery.yaml' % project)
    # Define state.yaml locations
    state_default_yml = os.path.join(ROOT, 'bakery', 'state.defaults.yaml')
    state_local_yml = os.path.join(DATA_ROOT, '%(login)s/%(id)s.state.yaml' % project)

    # Create internal state object, 'local'
    # TODO? rename this throughout codebase to bakeryStateInternal
    # if local is already set up, load it from file, otherwise load from defaults and set it up later
    if os.path.exists(state_local_yml):
        local = load_yaml(state_default_yml, state_local_yml)
    else:
        local = load_yaml(state_default_yml)
        refresh = True

    # Create external state object, 'state'
    # TODO? rename this throughout codebase to bakeryState
    # try to load the local bakery.yml from any previous runs and note that it was loaded
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
    ufo_dirs = []
    l = len(_in)
    for root, dirs, files in os.walk(_in):
        for f in files:
            fullpath = os.path.join(root, f)
            if os.path.splitext(fullpath)[1].lower() in ['.txt', '.md', '.markdown', 'LICENSE']:
                txt_files.append(fullpath[l:])
        for d in dirs:
            fullpath = os.path.join(root, d)
            if os.path.splitext(fullpath)[1].lower() == '.ufo':
                ufo_dirs.append(fullpath[l:])
    local['txt_files'] = txt_files
    local['ufo_dirs'] = ufo_dirs

    # If license_file not defined then choose OFL.txt or LICENSE.txt from the root of repo, if it exists
    if not state['license_file']:
        for fn in ['OFL.txt', 'LICENSE.txt']: # order means priority
            if os.path.exists(os.path.join(_in, fn)):
                state['license_file'] = fn
                break
    # and note it exists
    if os.path.exists(state['license_file']):
        local['license_file_found'] = True

    # Save both states to YAML files and return them
    if project.is_ready:
        project_state_save(project, state, local)
    return state, local

def project_state_save(project, state = None, local = None):
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

    bakery_local_yml = os.path.join(DATA_ROOT, '%(login)s/%(id)s.bakery.yaml' % project)
    state_local_yml = os.path.join(DATA_ROOT, '%(login)s/%(id)s.state.yaml' % project)

    f = open(bakery_local_yml, 'w')
    f.write(yaml.safe_dump(state))
    f.close()

    l = open(state_local_yml, 'w')
    l.write(yaml.safe_dump(local))
    l.close()
