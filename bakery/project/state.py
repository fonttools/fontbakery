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

def rwalk(path):
    h = {}
    cd = os.path.abspath(path)
    fs = os.listdir(path)
    for f in fs:
        cf = os.path.join(cd, f)
        if os.path.isfile(cf):
            h[f] = {}
        elif os.path.isdir(cf) and not cf.endswith('.git'):
            h[f] = rwalk(cf)
    return h

def load_yaml(default_yml, yml = None):
    """
    Load a YAML file from a defaults file that defines the keys TODO
    """
    data = yaml.load(open(default_yml, 'r').read())
    if yml:
        data.update(yaml.load(open(yml, 'r').read()))
    return data

def project_state_get(project, refresh = False):

    bakery_project_yml = os.path.join(DATA_ROOT, '%(login)s/%(id)s.in/bakery.yaml' % project)
    bakery_local_yml = os.path.join(DATA_ROOT, '%(login)s/%(id)s.bakery.yaml' % project)
    bakery_default_yml = os.path.join(ROOT, 'bakery', 'bakery.defaults.yaml')

    state_local_yml = os.path.join(DATA_ROOT, '%(login)s/%(id)s.state.yaml' % project)
    state_default_yml = os.path.join(ROOT, 'bakery', 'state.defaults.yaml')

    if os.path.exists(state_local_yml):
        local = load_yaml(state_default_yml, state_local_yml)
    else:
        local = load_yaml(state_default_yml)
        refresh = True

    # if project have its own bakery.yaml in git repo then use it
    # if no, then use local bakery.$(id).yaml
    # or fallback to default. This only can happends during development tests
    # because I deleted it manually.

    state = load_yaml(bakery_default_yml)
    local['status'] = 'default'
    if os.path.exists(bakery_project_yml):
        state = load_yaml(bakery_default_yml, bakery_project_yml)
        local['status'] = 'repo'
        # local['setup'] = True
    if os.path.exists(bakery_local_yml):
        state = load_yaml(bakery_default_yml, bakery_local_yml)
        local['status'] = 'local'

    if not refresh:
        return state, local

    _in = os.path.join(DATA_ROOT, '%(login)s/%(id)s.in/' % project)

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

    # if lincense_file not defined then choose OFL.txt or LICENSE.txt from the root of repo
    if not state['license_file']:
        for fn in ['OFL.txt', 'LICENSE.txt']: # order means priority
            if os.path.exists(os.path.join(_in, fn)):
                state['license_file'] = fn
                break

    if os.path.exists(state['license_file']):
        local['license_file_found'] = True

    local['tree'] = rwalk(os.path.join(DATA_ROOT, '%(login)s/%(id)s.in/' % project))

    project_state_save(project, state, local)

    return state, local

def project_state_save(project, state = None, local = None):
    if not state:
        state = project.config['state']
    if not local:
        local = project.config['local']

    state_yml = os.path.join(DATA_ROOT, '%(login)s/%(id)s.bakery.yaml' % project)
    local_yml = os.path.join(DATA_ROOT, '%(login)s/%(id)s.state.yaml' % project)

    f = open(state_yml, 'w')
    f.write(yaml.safe_dump(state))
    f.close()

    l = open(local_yml, 'w')
    l.write(yaml.safe_dump(local))
    l.close()

