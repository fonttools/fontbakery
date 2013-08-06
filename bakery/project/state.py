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
from flask import current_app

def check_yaml(login, project_id):
    DATA_ROOT = current_app.config.get('DATA_ROOT')

    yml = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.in/' % locals(), 'bakery.yaml')
    if not os.path.exists(yml):
        return 0
    return 1

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
    data = yaml.load(open(default_yml, 'r').read())
    if yml:
        data.update(yaml.load(open(yml, 'r').read()))
    return data

def project_state_get(login, project, refresh=False):
    ROOT = current_app.config.get('ROOT')
    DATA_ROOT = current_app.config.get('DATA_ROOT')

    bakery_project_yml = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.in/bakery.yaml' % project)
    bakery_local_yml = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.bakery.yaml' % project)
    bakery_default_yml = os.path.join(ROOT, 'bakery', 'bakery.defaults.yaml')

    state_local_yml = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.state.yaml' % project)
    state_default_yml = os.path.join(ROOT, 'bakery', 'state.defaults.yaml')

    if os.path.exists(state_local_yml):
        local = load_yaml(state_default_yml, state_local_yml)
    else:
        local = load_yaml(state_default_yml)
        refresh = True

    # if project have its own bakery.yaml in git repo then use it
    # if no, then use local bakery.$(project_id).yaml
    # or fallback to default. This only can happends during development tests
    # because I deleted it manually.

    if os.path.exists(bakery_project_yml):
        state = load_yaml(bakery_default_yml, bakery_project_yml)
        local['status'] = 'repository'
    elif os.path.exists(bakery_local_yml):
        state = load_yaml(bakery_default_yml, bakery_local_yml)
        local['status'] = 'local'
    else:
        state = load_yaml(bakery_default_yml)
        local['status'] = 'default'

    _in = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.in/' % project)

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

    local['tree'] = rwalk(os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.in/' % locals()))

    return state, local

def project_state_save(login, project, state, local):
    DATA_ROOT = current_app.config.get('DATA_ROOT')

    # don't publish this property to user
    if state.get('source', None):
        del state['source']
    yml = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.bakery.yaml' % project)
    local_yml = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.state.yaml' % project)

    f = open(yml, 'w')
    f.write(yaml.safe_dump(project.state))
    f.close()

    l = open(local_yml, 'w')
    l.write(yaml.safe_dump(project.local))
    l.close()


def status(login, project_id):
    if not check_yaml(login, project_id):
        return 0

