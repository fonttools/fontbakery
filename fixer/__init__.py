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

import yaml
# import imp
import os
from . import fixes

# fixes_folder = "fixes"
# MainModule = "__init__"

# def load_fixes(path):
#     fixes = []
#     files = [f for f in os.listdir(path) if f.endswith('.py')]
#     for i in files:
#         item = imp.find_module()
#         fixes.append({"name": i, "info": info})
#     return fixes

# temporary list
available_fixes = {
    'checker.result_suite.fontforge_suite.fftest.test_nbsp_and_space_glyphs_width': fixes.fix_nbsp
}


def fix_font(yaml_file, path):
    """ yaml — font bakery checker tests results yaml file. This file
               will be modified when all fixes apply
        path — font output folder in specified format

    """
    result = yaml.safe_load(open(yaml_file, 'r'))
    fonts = result.keys()
    for font in fonts:
        failure_list = []
        fixed_list = []
        for test in result[font]['failure']:
            full_name = ".".join([test['name'], test['methodName']])
            if full_name in available_fixes:
                font_path = os.path.join(path, font)
                print(font_path)
                available_fixes[full_name](font_path)
                fixed_list.append(test)
            else:
                failure_list.append(test)
        del result[font]['failure']
        result[font]['failure'] = failure_list
        result[font]['fixed'] = fixed_list

    l = open(yaml_file, 'w')
    l.write(yaml.safe_dump(result))
    l.close()

