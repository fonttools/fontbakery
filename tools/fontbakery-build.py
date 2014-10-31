#!/usr/bin/env python
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
import argparse
import os
import os.path as op
import sys
import yaml

try:
    import git
    from git import Repo
    GITPYTHON_INSTALLED = True
except ImportError:
    GITPYTHON_INSTALLED = False

from bakery_cli.bakery import Bakery, BAKERY_CONFIGURATION_DEFAULTS
from bakery_cli.utils import UpstreamDirectory


def create_bakery_config(bakery_config_dir, data):
    if not op.exists(bakery_config_dir):
        os.makedirs(bakery_config_dir)

    bakeryyaml = op.abspath(op.join(bakery_config_dir, 'bakery.yaml'))

    data = {k: data[k] for k in data if data[k]}

    l = open(bakeryyaml, 'w')
    l.write(yaml.safe_dump(data))
    l.close()


def find_bakery_config(sourcedir):
    for bakeryfile in ['bakery.yaml', 'bakery.yml']:
        try:
            bakeryyaml = open(op.join(sourcedir, bakeryfile), 'r')
            return yaml.safe_load(bakeryyaml)
        except IOError:
            pass
    return None


def run_bakery(sourcedir):
    sourcedir = op.realpath(sourcedir)
    try:
        config = find_bakery_config(sourcedir)
        if not config:
            config = yaml.safe_load(open(BAKERY_CONFIGURATION_DEFAULTS))

        builddir = 'build'
        if GITPYTHON_INSTALLED:
            try:
                repo = Repo(sourcedir)
                builddir = repo.git.rev_parse('HEAD', short=True)
            except git.exc.InvalidGitRepositoryError:
                pass
        builddir = os.environ.get('TRAVIS_COMMIT', builddir)

        build_project_dir = op.join(sourcedir, 'builds', builddir)

        if 'process_files' not in config:
            directory = UpstreamDirectory(sourcedir)
            # normalize process_files path
            config['process_files'] = directory.get_fonts()

        create_bakery_config(build_project_dir, config)

        b = Bakery('', sourcedir, 'builds', builddir)
        config = op.join(build_project_dir, 'bakery.yaml')
        b.load_config(config)
        b.run()
    except:
        if os.environ.get('DEBUG'):
            raise
        sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('projectpath', nargs='+',
                        help="Directory to run bakery build process on")
    args = parser.parse_args()

    for p in args.projectpath:
        run_bakery(p)
