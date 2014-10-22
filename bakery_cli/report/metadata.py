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

METADATA_JSON = 'METADATA.json'


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


def generate(config):
    matadata_json = op.join(config['path'], METADATA_JSON)
    if not op.exists(matadata_json):
        return

    try:
        data = yaml.load(open(op.join(config['path'], 'METADATA.yaml')))
    except IOError:
        data = {}

    tests_summary = {}
    tests_summary_filepath = op.join(config['path'], 'summary.tests.json')
    if op.exists(tests_summary_filepath):
        tests_summary = json.load(open(tests_summary_filepath))

    summary = {
        'success': len(data.get(METADATA_JSON, {}).get('success', [])),
        'error': len(data.get(METADATA_JSON, {}).get('error', [])),
        'failure': len(data.get(METADATA_JSON, {}).get('failure', [])),
        'fixed': len(data.get(METADATA_JSON, {}).get('fixed', []))
    }
    tests_summary.update({METADATA_JSON: summary})
    json.dump(tests_summary, open(tests_summary_filepath, 'w'))

    new_data = []
    for k in data:
        d = {'name': k}
        d.update(data[k])
        new_data.append(d)
    report_app = report_utils.BuildInfo(config)

    report_app.metadata_page.dump_file(new_data, 'tests.json')
