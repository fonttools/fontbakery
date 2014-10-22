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
import zipfile


class Zip(object):

    def __init__(self, bakery):
        self.project_root = bakery.project_root
        self.builds_root = bakery.builds_dir
        self.bakery = bakery

    def execute(self, pipedata, prefix=""):
        task = self.bakery.logging_task('ZIP result for download')
        if self.bakery.forcerun:
            return

        try:
            name = op.basename(self.bakery.build_dir)

            self.bakery.logging_cmd('zip -r {0}.zip {0}'.format(name))

            zipf = zipfile.ZipFile(op.join(self.builds_root, name + '.zip'), 'w')
            for root, dirs, files in os.walk(op.join(self.builds_root, name)):
                root = root.replace(op.join(self.builds_root, name), '').lstrip('/')
                for file in files:
                    arcpath = op.join(name, root, file)
                    self.bakery.logging_raw('add %s\n' % arcpath)
                    zipf.write(op.join(self.builds_root, name, root, file), arcpath)
            zipf.close()
            self.bakery.logging_task_done(task)
        except:
            self.bakery.logging_task_done(task, failed=True)
            raise

        pipedata['zip'] = '%s.zip' % name
