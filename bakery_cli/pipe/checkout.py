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


class Checkout(object):

    def __init__(self, bakery):
        self.project_root = bakery.project_root
        self.bakery = bakery

    def execute(self, pipedata, prefix=''):
        from git import Repo
        revision = pipedata.get('commit') or 'master'

        repo = Repo(self.project_root)
        headcommit = repo.git.rev_parse('HEAD', short=True)
        if revision != 'master':
            msg = 'Checkout commit %s\n' % headcommit
        else:
            msg = 'Checkout most recent commit (%s)' % headcommit

        task = self.bakery.logging_task(msg)

        if self.bakery.forcerun:
            return

        self.bakery.logging_cmd('git checkout %s' % revision)
        try:
            repo.git.checkout(revision)
        except:
            self.bakery.logging_task_done(task, failed=True)
            raise

        self.bakery.logging_task_done(task)
