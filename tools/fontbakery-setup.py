#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 The Font Bakery Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# See AUTHORS.txt for the list of Authors and LICENSE.txt for the License.

import os
from bakery_cli.bakery import BAKERY_CONFIGURATION_DEFAULTS, BAKERY_CONFIGURATION_NEW

BAKERY_DEFAULTS_EXISTS = os.path.exists(BAKERY_CONFIGURATION_DEFAULTS)
BAKERY_DEFAULTS_CONTENT = ''
FILENAME = BAKERY_CONFIGURATION_NEW if BAKERY_DEFAULTS_EXISTS else BAKERY_CONFIGURATION_DEFAULTS

process_files = []
extensions = ['.sfd', '.ufo', '.ttx', '.ttf']
for path, dirs, files in os.walk('.'):
    for f in files:
        for ext in extensions:
            if f.endswith(ext):
                process_files.append({'path': path, 'name': f, 'isfile': True})
    for d in dirs:
        for ext in extensions:
            if d.endswith(ext):
                process_files.append({'path': path, 'name': d, 'isfile': False})

if BAKERY_DEFAULTS_EXISTS:
    with open(BAKERY_CONFIGURATION_DEFAULTS, 'r') as f:
        BAKERY_DEFAULTS_CONTENT = f.read()

with open(FILENAME, 'w') as f:
    f.seek(0)
    f.write(BAKERY_DEFAULTS_CONTENT)
    process_files_str = ', '.join(['"{}"'.format(item.name) for item in process_files])
    f.write('[{}]'.format(process_files_str))
    f.truncate()
