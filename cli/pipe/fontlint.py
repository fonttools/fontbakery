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
import os.path as op
import yaml

from checker import run_set
from checker.base import BakeryTestCase


class FontLint(object):

    def __init__(self, bakery):
        self.project_root = bakery.project_root
        self.builddir = bakery.build_dir
        self.bakery = bakery

    def read_lint_testsresult(self):
        try:
            _out_yaml = op.join(self.builddir, '.tests.yaml')
            return yaml.safe_load(open(_out_yaml))
        except (IOError, OSError):
            return {}

    def write_lint_results(self, testsresult):
        _out_yaml = op.join(self.builddir, '.tests.yaml')
        l = open(_out_yaml, 'w')
        l.write(yaml.safe_dump(testsresult))
        l.close()

    def run_metadata_tests(self):
        path = op.join(self.builddir, 'METADATA.json')
        return run_set(path, 'metadata', log=self.bakery.log)

    def execute(self, pipedata, prefix=""):
        _out_yaml = op.join(self.builddir, '.tests.yaml')

        if op.exists(_out_yaml):
            return yaml.safe_load(open(_out_yaml, 'r'))

        task = self.bakery.logging_task('Run tests for baked files')
        if self.bakery.forcerun:
            return

        try:
            result = {}
            for font in pipedata['bin_files']:
                self.bakery.logging_raw('### Test %s\n' % font)
                result[font] = run_set(op.join(self.builddir, font), 'result',
                                       log=self.bakery.log)

            self.bakery.logging_raw('### Test METADATA.json\n')
            result['METADATA.json'] = self.run_metadata_tests()
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
            except Exception, ex:
                return '%s' % ex

    try:
        err_msg = getattr(data, '_err_msg', '').decode('utf-8', 'ignore')
    except Exception, ex:
        err_msg = '%s' % ex

    _ = {
        'methodDoc': method_doc(data._testMethodDoc),
        'tool': data.tool,
        'name': data.name,
        'methodName': data._testMethodName,
        'targets': data.targets,
        'tags': getattr(data, data._testMethodName).tags,
        'err_msg': err_msg
    }
    return dumper.represent_mapping(u'tag:yaml.org,2002:map', _)

yaml.SafeDumper.add_multi_representer(BakeryTestCase, repr_testcase)
