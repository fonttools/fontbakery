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
import importlib
import inspect


modules = []


for testfile in os.listdir(os.path.dirname(__file__)):
    if testfile.startswith('test_'):
        try:
            module_name, _ = os.path.splitext(testfile)
            module = 'checker.tests.downstream.%s' % module_name
            module = importlib.import_module(module)

            for name, obj in inspect.getmembers(module):
                if obj.__bases__[0].__name__ == 'BakeryTestCase':
                    importstring = 'from checker.tests.downstream.%s import %s' % (module_name, name)
                    if importstring not in modules:
                        modules.append(importstring)
                        exec importstring
                        print name
        except (ImportError, AttributeError, IndexError):
            pass
