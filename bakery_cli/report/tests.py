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

import os.path as op
import yaml
import json

from bakery_cli.report import utils as report_utils
from bakery_cli.utils import UpstreamDirectory

TAB = 'Tests'
TEMPLATE_DIR = op.join(op.dirname(__file__), 'templates')

t = lambda templatefile: op.join(TEMPLATE_DIR, templatefile)


def sort(data):
    a = []
    for d in data:
        if 'required' in d['tags']:
            a.append(d)

    for d in data:
        if 'note' in d['tags'] and 'required' not in d['tags']:
            a.append(d)

    for d in data:
        if 'note' not in d['tags'] and 'required' not in d['tags']:
            a.append(d)

    return a


def generate(config, outfile='tests.html'):
    directory = UpstreamDirectory(config['path'])

    tests = {}

    data = {}
    for fp in directory.BIN:
        path = op.join(config['path'], '{}.yaml'.format(fp[:-4]))
        if op.exists(path):
            data[fp] = yaml.load(open(path))
            tests[fp] = {'success': len(data[fp].get('success', [])),
                         'error': len(data[fp].get('error', [])),
                         'failure': len(data[fp].get('failure', [])),
                         'fixed': len(data[fp].get('fixed', []))}

    if not data:
        return

    new_data = []
    for k in data:
        d = {'name': k}
        d.update(data[k])
        new_data.append(d)

    tests_summary = {}
    tests_summary_filepath = op.join(config['path'], 'summary.tests.json')
    if op.exists(tests_summary_filepath):
        tests_summary = json.load(open(tests_summary_filepath))
    tests_summary.update(tests)

    json.dump(tests_summary, open(tests_summary_filepath, 'w'))

    report_app = report_utils.BuildInfo(config)
    report_app.tests_page.dump_file(new_data, 'tests.json')

    # print(report_utils.render_template(outfile,
    #     tests=data, sort=sort, current_page=outfile, app_version=app_version,
    #     build_repo_url=report_utils.build_repo_url), file=destfile)
