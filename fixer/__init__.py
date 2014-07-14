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
    'test_nbsp_and_space_glyphs_width': fixes.fix_nbsp,
    'test_metrics_linegaps_are_zero': fixes.fix_metrics,
    'test_metrics_ascents_equal_max_bbox': fixes.fix_metrics,
    'test_metrics_descents_equal_min_bbox': fixes.fix_metrics,
    'test_non_ascii_chars_in_names': fixes.fix_name_ascii,
    'test_is_fsType_not_set': fixes.fix_fstype_to_zero,
    'test_font_weight_is_canonical': fixes.fix_ttf_stylenames
}


def fix_font(yaml_file, path, log=None, interactive=False):
    """ Applies available fixes to baked fonts.

        Looks through yaml_file to search available fixes and apply it
        upon the concrete baked font.

        Args:
            yaml: Font bakery checker tests results yaml file.
                This file will be modified when all fixes apply.
            path: Folder where baked fonts generated.
            interactive: Optional.
                If True then user will be asked to start applying fixes
                manually.
            log: Optional argument to make fixes process loggable.
                It is a class that must have defined `write` method. Eg:

                class stdlog:

                    @staticmethod
                    def write(msg, prefix=''):
                        pass
    """
    result = yaml.safe_load(open(yaml_file, 'r'))
    fonts = result.keys()
    for font in fonts:
        failure_list = []
        fixed_list = []
        apply_fixes = set()
        for test in result[font]['failure']:
            if test['methodName'] in available_fixes:
                apply_fixes.add(available_fixes[test['methodName']])
                fixed_list.append(test)
            else:
                failure_list.append(test)

        if apply_fixes:
            font_path = os.path.join(path, font)
            for fun in apply_fixes:
                if interactive:
                    answer = raw_input("Apply fix %s? [y/N]" % fun.__doc__)
                    if answer.lower() != 'y':
                        log.write('N\n')
                        continue
                fun(font_path, log)

        del result[font]['failure']
        result[font]['failure'] = failure_list
        result[font]['fixed'] = fixed_list

    l = open(yaml_file, 'w')
    l.write(yaml.safe_dump(result))
    l.close()
