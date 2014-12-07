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
import codecs
import os.path as op
import yaml

from bakery_lint import run_set
from bakery_cli.utils import UpstreamDirectory


class UpstreamLint(object):

    def __init__(self, bakery):
        self.project_root = bakery.project_root
        self.builddir = bakery.build_dir
        self.bakery = bakery

    def execute(self, pipedata):
        task = self.bakery.logging_task('Run upstream tests')
        if self.bakery.forcerun:
            return

        result = {}
        upstreamdir = op.join(self.builddir, 'sources')

        self.bakery.logging_cmd('fontbakery-check.py upstream-repo sources')
        result['Project'] = run_set(upstreamdir, 'upstream-repo',
                                    log=self.bakery.logger)
        directory = UpstreamDirectory(upstreamdir)

        for font in directory.ALL_FONTS:
            if font[-4:] not in '.ttx':
                self.bakery.logging_cmd('fontbakery-check.py upstream {}'.format(font))
                result[font] = run_set(op.join(upstreamdir, font),
                                       'upstream', log=self.bakery.logger)

        _out_yaml = op.join(self.builddir, 'upstream.yaml')

        l = codecs.open(_out_yaml, mode='w', encoding="utf-8")
        l.write(yaml.safe_dump(result))
        l.close()
