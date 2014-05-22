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
import subprocess
import sys

from bakery.app import app


ENV = os.environ.copy()
ENV.update({'PYTHONPATH': os.pathsep.join(sys.path)})
PYPATH = 'python'


def fix_nbsp(font_path):
    SCRIPTPATH = os.path.join(app.config['ROOT'], 'scripts', 'fix-ttf-nbsp.py')
    subprocess.Popen("{0} {1} {2}".format(PYPATH, SCRIPTPATH, font_path), shell=True, env=ENV).communicate()
    subprocess.Popen("rm {0}".format(font_path), shell=True).communicate()
    subprocess.Popen("mv {0}-nbsp {0}".format(font_path), shell=True).communicate()


def fix_metrics(font_path):
    SCRIPTPATH = os.path.join(app.config['ROOT'], 'scripts', 'fix-ttf-vmet.py')
    subprocess.Popen("{0} {1} --autofix {2}".format(PYPATH, SCRIPTPATH, font_path), shell=True, env=ENV).communicate()
    subprocess.Popen("rm {0}".format(font_path), shell=True).communicate()
    subprocess.Popen("mv {0}.fix {0}".format(font_path), shell=True).communicate()


def fix_name_ascii(font_path):
    SCRIPTPATH = os.path.join(app.config['ROOT'], 'scripts', 'fix-ttf-ascii-name.py')
    subprocess.Popen("{0} {1} --autofix {2}".format(PYPATH, SCRIPTPATH, font_path), shell=True, env=ENV).communicate()


def fix_fstype_to_zero(font_path):
    pass
