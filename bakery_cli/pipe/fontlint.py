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
import os
import os.path as op
import yaml
import traceback

from bakery_lint import run_set
from bakery_lint.base import BakeryTestCase


OUT_YAML = 'METADATA.yaml'


class FontLint(object):

    def __init__(self, bakery):
        self.project_root = bakery.project_root
        self.builddir = bakery.build_dir
        self.bakery = bakery

    def read_lint_testsresult(self):
        try:
            _out_yaml = op.join(self.builddir, OUT_YAML)
            return yaml.safe_load(open(_out_yaml))
        except (IOError, OSError):
            return {}

    def write_lint_results(self, testsresult):
        _out_yaml = op.join(self.builddir, OUT_YAML)
        l = open(_out_yaml, 'w')
        l.write(yaml.safe_dump(testsresult))
        l.close()

    def run(self, ttf_path, pipedata):
        if 'downstream' in pipedata and not pipedata['downstream']:
            return

        self.bakery.logging_raw('### Test %s\n' % ttf_path)

        self.bakery.logging_cmd('fontbakery-check.py result {}'.format(ttf_path))

        try:
            data = run_set(op.join(self.builddir, ttf_path), 'result')
            l = open(os.path.join(self.builddir, '{}.yaml'.format(ttf_path[:-4])), 'w')
            l.write(yaml.safe_dump(data))
            l.close()
        except Exception as ex:
            traceback.print_exc(ex)
            self.bakery.logging_raw('Could not store tests result: {}'.format(ex))
            raise

    def execute(self, pipedata, prefix=""):
        _out_yaml = op.join(self.builddir, OUT_YAML)

        if op.exists(_out_yaml):
            return yaml.safe_load(open(_out_yaml, 'r'))

        task = self.bakery.logging_task('Run tests for baked files')
        if self.bakery.forcerun:
            return

        try:
            result = {}
            for font in pipedata['bin_files']:
                self.run(font, pipedata)

            # self.bakery.logging_raw('### Test METADATA.json\n')
            # result['METADATA.json'] = self.run_metadata_tests()
            self.bakery.logging_task_done(task)
        except:
            self.bakery.logging_task_done(task, failed=True)

        if not result:
            return

        self.write_lint_results(result)


# register yaml serializer for tests result objects.
def repr_testcase(dumper, data):

    def method_doc(doc):
        if doc is None:
            return "None"
        else:
            try:
                doc = ' '.join(doc.split())
                return doc.decode('utf-8', 'ignore')
            except Exception as ex:
                return '%s' % ex

    try:
        err_msg = getattr(data, '_err_msg', '').decode('utf-8', 'ignore')
    except Exception as ex:
        err_msg = '%s' % ex

    testMethod = getattr(data, data._testMethodName)
    _ = {
        'methodDoc': method_doc(data._testMethodDoc),
        'tool': data.tool,
        'name': data.name,
        'methodName': data._testMethodName,
        'targets': data.targets,
        'tags': getattr(testMethod, 'tags', ['note']),
        'err_msg': err_msg,
        'autofix': getattr(testMethod, 'autofix', False)
    }
    return dumper.represent_mapping(u'tag:yaml.org,2002:map', _)

yaml.SafeDumper.add_multi_representer(BakeryTestCase, repr_testcase)
