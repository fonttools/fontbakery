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

import logging
import redis
import os
import glob
import subprocess
import yaml
from flask import json # require Flask > 0.10
from flask.ext.rq import job
import plistlib
import checker.runner
from utils import RedisFd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
DATA_ROOT = os.path.join(ROOT, 'data')

logger = logging.getLogger('bakery.tasks')
logger.setLevel(logging.INFO)

def run(command, cwd = None, log = None):
    # command — to run,
    # cwd - current working dir
    # log — file descriptor with .write() method

    if log:
        log.write('\nCommand: %s\n' % command)

    p = subprocess.Popen(command, shell = True, cwd = cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    while True:
        stdout = p.stdout.readline()
        stderr = p.stderr.readline()
        log.write(stdout)
        if stderr:
            log.write(stderr)

        if not stdout and not stderr and not p.poll():
            break

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
    project_git_sync(login = project.login, project_id = project.id, clone = project.clone)
    process_project(login = project.login, project_id = project.id, conn = conn)

@job
def git_clean(login, project_id):
    return
    # CLEAN_SH = '' #"""cd %(root)s && rm -rf %(login)s/%(project_id)s.in/ && rm -rf %(login)s/%(project_id)s.out/"""
    # params = locals()
    # params['root'] = DATA_ROOT
    # run(CLEAN_SH % params)

def check_yaml(login, project_id):
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

def project_state_get(login, project_id, full=False):
    project_yml = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.in/bakery.yaml' % locals())
    local_yml = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.bakery.yaml' % locals())
    default_yml = os.path.join(ROOT, 'bakery', 'bakery.defaults.yaml')

    # if project have its own bakery.yaml in git repo then use it
    # if no, then use local bakery.$(project_id).yaml
    # or fallback to default. This only can happends during development tests

    if os.path.exists(project_yml):
        state = yaml.load(open(default_yml, 'r').read())
        state.update(yaml.load(open(project_yml, 'r').read()))
        state['source'] = 'project'
    elif os.path.exists(local_yml):
        state = yaml.load(open(default_yml, 'r').read())
        state.update(yaml.load(open(local_yml, 'r').read()))
        state['source'] = 'local'
    else:
        state = yaml.load(open(default_yml, 'r').read())
        state['source'] = 'default'

    if not full:
        return state

    dir_in = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.in/' % locals())

    txt_files = []
    ufo_dirs = []
    l = len(dir_in)
    for root, dirs, files in os.walk(dir_in):
        for f in files:
            fullpath = os.path.join(root, f)
            if os.path.splitext(fullpath)[1].lower() in ['.txt', '.md', '.markdown', 'LICENSE']:
                txt_files.append(fullpath[l:])
        for d in dirs:
            fullpath = os.path.join(root, d)
            if os.path.splitext(fullpath)[1].lower() == '.ufo':
                ufo_dirs.append(fullpath[l:])

    state['txt_files'] = txt_files
    state['ufo_dirs'] = ufo_dirs

    # if lincense_file not defined then choose OFL.txt or LICENSE.txt from the root of repo
    if not state['license_file']:
        for fn in ['OFL.txt', 'LICENSE.txt']: # order means priority
            if os.path.exists(os.path.join(dir_in, fn)):
                state['license_file'] = fn
                break

    if os.path.exists(state['license_file']):
        state['license_file_found'] = True

    return state

def project_state_save(login, project_id, state):
    # don't publish this property to user
    if state.get('source', None):
        del state['source']
    yml = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.bakery.yaml' % locals())
    f = open(yml, 'w')
    f.write(yaml.safe_dump(state))
    f.close()

@job
def project_git_sync(login, project_id, clone):
    project_dir = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.in/' % locals())
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)

    project_out = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.out/src/' % locals())
    if not os.path.exists(project_out):
        os.makedirs(project_out)

    log = open(os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.process.log' % locals()), 'a')

    if not os.path.exists(os.path.join(project_dir, '.git')):
        # no .git folder in project folder
        run('git clone --depth=100 --quiet --branch=master %s .' % clone, cwd = project_dir, log=log)

    # child = prun('git rev-parse --short HEAD', cwd=project_dir)
    # hashno = child.stdout.readline().strip()
    # make current out folder

    log.close()

@job
def process_project(login, project_id, conn):
    # login — user login
    # project_id - database project_id
    # conn - redis connection
    log = RedisFd(os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.process.log' % locals()),
        'a', conn, "build_%s" % project_id)

    state = project_state_get(login, project_id)
    _in = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.in/' % locals())
    _out = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.out/src/' % locals())
    for ufo, name in state['out_ufo'].items():
        if state['rename']:
            ufo_folder = name+'.ufo'
        else:
            ufo_folder = ufo.split('/')[-1]
        run("cp -R '%s' '%s'" % (os.path.join(_in, ufo), os.path.join(_out, ufo_folder)), log=log)
        if state['rename']:
            finame = os.path.join(_out, ufo_folder, 'fontinfo.plist')
            finfo = plistlib.readPlist(finame)
            finfo['familyName'] = name
            plistlib.writePlist(finfo, finame)

    # set of other commands
    if state['autoprocess']:
        # project should be processes only when setup is done
        generate_fonts(login, project_id, log)
        ttfautohint_process(login, project_id, log)
        # subset
        subset_process(login, project_id, log)
        generate_metadata(login, project_id, log)
        lint_process(login, project_id, log)

    log.close()

def status(login, project_id):
    if not check_yaml(login, project_id):
        return 0

def read_license(login, project_id):
    state = project_state_get(login, project_id, full=True)
    licensef = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.in/' % locals(), state['license_file'])
    if os.path.exists(licensef):
        try:
            return unicode(open(licensef, 'r').read(), "utf8")
        except IOError:
            return "Error reading license file"
    else:
        return None

def read_metadata(login, project_id):
    metadata = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.out/' % locals(), 'METADATA.json')
    metadata_new = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.out/' % locals(), 'METADATA.json.new')

    if os.path.exists(metadata):
        metadata_file = unicode(open(metadata, 'r').read(), "utf8")
    else:
        metadata_file = ''

    if os.path.exists(metadata_new):
        metadata_new_file = unicode(open(metadata_new, 'r').read(), "utf8")
    else:
        metadata_new_file = ''

    return (metadata_file, metadata_new_file)

def save_metadata(login, project_id, metadata, del_new=True):
    mf = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.out/' % locals(), 'METADATA.json')
    mf_new = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.out/' % locals(), 'METADATA.json.new')

    f = open(mf, 'w')
    json.dump(json.loads(metadata), f, indent=2, ensure_ascii=True) # same params as in generatemetadata.py
    f.close()

    if del_new:
        if os.path.exists(mf_new):
            os.remove(mf_new)

def read_description(login, project_id):
    description_file = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.out/' % locals(), 'DESCRIPTION.en_us.html')

    if os.path.exists(description_file):
        description = unicode(open(description_file, 'r').read(), "utf8")
    else:
        description = ''

    return description

def save_description(login, project_id, description):
    mf = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.out/' % locals(), 'DESCRIPTION.en_us.html')

    f = open(mf, 'w')
    f.write(description)
    f.close()

def read_log(login, project_id):
    log_file = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.process.log' % locals())

    if os.path.exists(log_file):
        return unicode(open(log_file, 'r').read(), "utf8")
    else:
        return ''

def read_yaml(login, project_id):
    yaml_file = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.bakery.yaml' % locals())

    if os.path.exists(yaml_file):
        return unicode(open(yaml_file, 'r').read(), "utf8")
    else:
        return ''

def read_tree(login, project_id):
    return rwalk(os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.in/' % locals()))

def generate_fonts(login, project_id, log):
    state = project_state_get(login, project_id)
    _in = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.in/' % locals())
    _out = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.out/src/' % locals())

    scripts_folder = os.path.join(ROOT, 'scripts')

    for name in state['out_ufo'].values():
        cmd_short = "python ufo2ttf.py '%(out)s.ufo' '%(out)s.ttf' '%(out)s.otf'" % {
            'out': os.path.join(_out, name),
        }
        run(cmd_short, cwd = scripts_folder, log=log)

def generate_metadata(login, project_id, log):
    _out = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.out/' % locals())
    cmd = "%(wd)s/venv/bin/python %(wd)s/scripts/genmetadata.py '%(out)s'"
    run(cmd % {'wd': ROOT, 'out': _out}, cwd=_out, log=log)

def lint_process(login, project_id, log):
    _out = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.out/' % locals())
    # java -jar dist/lint.jar "$(dirname $metadata)"
    cmd = "java -jar %(wd)s/scripts/lint.jar '%(out)s'"
    run(cmd % {'wd': ROOT, 'out': _out}, cwd=_out, log=log)

def ttfautohint_process(login, project_id, log):
    # $ ttfautohint -l 7 -r 28 -G 0 -x 13 -w "" -W -c original_font.ttf final_font.ttf
    state = project_state_get(login, project_id)
    _out = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.out/' % locals())
    if state['ttfautohintuse']:
        for name in state['out_ufo'].values():
            cmd = "ttfautohint '%(src)s.ttf' '%(out)s.ttf'" % {
                'out': os.path.join(_out, name),
                'src': os.path.join(_out, 'src', name),
            }
            run(cmd % {'wd': ROOT, 'out': _out}, cwd=_out, log=log)
    else:
        run("cp src/*.ttf .", cwd=_out, log=log)

def subset_process(login, project_id, log):
    state = project_state_get(login, project_id)
    _out = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.out/' % locals())
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

def project_tests(login, project_id):
    state = project_state_get(login, project_id)
    _out = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.out/src/' % locals())
    result = {}
    for name in state['out_ufo'].values():
        result[name] = checker.runner.run_set(os.path.join(_out, name+'.ufo'))
    return result

