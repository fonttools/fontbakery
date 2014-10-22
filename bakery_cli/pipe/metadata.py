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
from bakery_cli.scripts import genmetadata


class Metadata(object):

    def __init__(self, bakery):
        self.project_root = bakery.project_root
        self.builddir = bakery.build_dir
        self.bakery = bakery

    def execute(self, pipedata, prefix=""):
        task = self.bakery.logging_task('Generate METADATA.json (fontbakery-build-metadata.py)')
        if self.bakery.forcerun:
            return

        self.bakery.logging_cmd('fontbakery-build-metadata.py %s' % self.builddir)
        try:
            # reassign ansiprint to our own method
            genmetadata.ansiprint = self.ansiprint
            genmetadata.run(self.builddir)
            self.bakery.logging_task_done(task)
        except Exception as  e:
            self.bakery.logging_err(e.message)
            self.bakery.logging_task_done(task, failed=True)
            raise

    def ansiprint(self, message, color):
        self.bakery.logging_raw(u'{}\n'.format(message.encode('unicode_escape', 'ignore')))
