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
import logging
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
from bakery_cli.logger import logger
from bakery_cli.utils import UpstreamDirectory, ttfautohint_installed


def create_bakery_config(bakery_yml_file, data):
    if not op.exists(op.dirname(bakery_yml_file)):
        os.makedirs(op.dirname(bakery_yml_file))

    data = {k: data[k] for k in data if data[k]}

    l = open(bakery_yml_file, 'w')
    l.write(yaml.safe_dump(data))
    l.close()


def run_bakery(path, verbose=False):
    # fontbakery-build supports passing arguments of directory or
    # concrete bakery.y[a]ml files. In case of passing directory
    # it looks at existing bakery.yml or bakery.yaml and runs on
    # first matched filepath

    # There can also be cases when directory does not contain any
    # bakery.y[a]ml or passed bakery.yml file does not exist. Then
    # fontbakery-build loads default configuration.
    bakery_yml_file = None
    sourcedir = path

    if os.path.isdir(path):
        for filename in ['bakery.yml', 'bakery.yaml']:
            if os.path.exists(os.path.join(path, filename)):
                bakery_yml_file = os.path.join(path, filename)
                break
    else:
        bakery_yml_file = path
        sourcedir = os.path.dirname(path)

    try:
        if bakery_yml_file:
            config = yaml.safe_load(open(bakery_yml_file, 'r'))
        else:
            raise IOError
    except IOError:
        bakery_yml_file = os.path.join(sourcedir, 'bakery.yml')
        config = yaml.safe_load(open(BAKERY_CONFIGURATION_DEFAULTS))

    try:
        builddir = 'build'
        if GITPYTHON_INSTALLED:
            try:
                repo = Repo(sourcedir)
                builddir = repo.git.rev_parse('HEAD', short=True)
            except git.exc.InvalidGitRepositoryError:
                pass
        builddir = os.environ.get('TRAVIS_COMMIT', builddir)

        if 'process_files' not in config:
            directory = UpstreamDirectory(sourcedir)
            # normalize process_files path
            config['process_files'] = directory.get_fonts()

        create_bakery_config(bakery_yml_file, config)

        b = Bakery('', sourcedir, 'builds', builddir)
        b.addLoggingToFile()
        b.load_config(bakery_yml_file)
        b.run()

        if not ttfautohint_installed():
            msg = ('Command line tool `ttfautohint` is required. Install it with'
                   ' `apt-get install ttfautohint` or `brew install ttfautohint`')
            logger.error(msg)
    except:
        if verbose or config.get('verbose'):
            raise
        sys.exit(1)


if __name__ == '__main__':
    description = ('Builds projects specified by bakery.yml file(s).'
                   ' Output is in project/builds/commit/')
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('path', metavar='DIRECTORY OR BAKERY.YML', nargs='+',
                        help="Directory or path to bakery.y[a]ml to run"
                             " bakery build process on")
    parser.add_argument('--verbose', default=False, action='store_true')
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.INFO)

    for p in args.path:
        run_bakery(os.path.abspath(p), verbose=args.verbose)
