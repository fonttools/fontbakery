#!/usr/bin/python
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
import glob
import shutil
import os

from bakery_cli.report import (tests, index, buildlog, checks, metadata,
                               bakery, description, review, utils)


if __name__ == '__main__':
    try:
        import jinja2
    except IndexError:
        print(('Bakery report script uses jinja2 template engine.'
               ' Please install jinja2 before using'))

    parser = argparse.ArgumentParser()
    parser.add_argument('path')

    args = parser.parse_args()

    if int(os.environ.get('TRAVIS_TEST_RESULT', 0)) == 0:
        config = {'path': args.path}
        report_app = utils.BuildInfo(config)
        # app.generate(config)
        tests.generate(config)
        index.generate(config)
        metadata.generate(config)
        description.generate(config)
        checks.generate(config)
        review.generate(config)
        bakery.generate(config)
        buildlog.generate(config)

        for item in ('METADATA.yaml', 'buildlog.txt', 'fontaine.txt',
                     'summary.tests.json', 'upstream.yaml'):
            path = os.path.join(config['path'], item)
            if os.path.exists(path):
                report_app.move_to_data(path)

        if os.path.exists(os.path.join(config['path'], 'FONTLOG.txt')):

            if not bool(glob.glob(os.path.join(config['path'], 'README*'))):
                src = os.path.join(config['path'], 'FONTLOG.txt')
                dst = os.path.join(config['path'], 'README.md')
                shutil.move(src, dst)

        contents = ''
        if os.path.exists(os.path.join(config['path'], 'README.md')):
            with open(os.path.join(config['path'], 'README.md')) as l:
                contents = l.read()

        reposlug = os.environ.get('TRAVIS_REPO_SLUG', 'dummy/repo')
        travis_http = 'https://travis-ci.org/{}'.format(reposlug)
        travis = '[![Build Status]({0}.svg?branch=master)]({0})'

        contents = travis.format(travis_http) + '\n\n' + contents
        with open(os.path.join(config['path'], 'README.md'), 'w') as l:
            l.write(contents)
        report_app.copy_to_data(os.path.join(config['path'], 'summary.tests.json'))
    else:
        config = {'path': args.path, 'failed': True}
        utils.BuildInfo(config)
        # app.generate(config)
        # index.generate(config)

