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
import json
import os
import os.path as op
import yaml

from bakery.app import app
from cli.system import stdoutlog, shutil
from scripts.vmet import metricview, metricfix
from scripts.ascii import fix_name_table
from scripts.fstype import reset_fstype
from scripts.stylenames import fix_style_names
from scripts.nbsp import checkAndFix


class AutoFix(object):

    def __init__(self, project_root, builddir, stdout_pipe=stdoutlog):
        self.project_root = project_root
        self.builddir = builddir
        self.stdout_pipe = stdout_pipe

    def execute(self, pipedata):
        self.stdout_pipe.write('Applying autofixes\n', prefix='### ')
        _out_yaml = op.join(self.builddir, '.tests.yaml')
        autofix(_out_yaml, self.builddir, log=self.stdout_pipe)


PYPATH = 'python'


def logging(log, command):
    if not log:
        return
    log.write(u'$ %s' % command.replace(app.config['ROOT'], '').strip('/'))


def fix_nbsp(font_path, log=None):
    """ Fix width for space and nbsp """
    SCRIPTPATH = os.path.join(app.config['ROOT'], 'scripts', 'nbsp.py')

    command = "{0} {1} {2}".format(PYPATH, SCRIPTPATH, font_path)
    logging(log, command)
    checkAndFix(font_path)

    command = "mv {0}.fix {0}".format(font_path)
    logging(log, command)
    shutil.move(font_path + '.fix', font_path, log=log)


def fix_metrics(path, log=None):
    """ Fix vmet table with actual min and max values """
    SCRIPTPATH = os.path.join(app.config['ROOT'], 'scripts', 'vmet.py')

    from checker.metadata import FamilyMetadata
    family_metadata = FamilyMetadata(json.load(open(path)))

    paths = []
    for f in family_metadata.fonts:
        path = op.join(op.dirname(path), f.filename)
        paths.append(path)

    command = "{0} {1} --autofix {2}"
    command = command.format(PYPATH, SCRIPTPATH, ' '.join(paths))
    logging(log, command)

    metricfix(paths)

    for font_path in paths:
        shutil.move(font_path + '.fix', font_path, log=log)

    command = "{0} {1} {2}".format(PYPATH, SCRIPTPATH, ' '.join(paths))
    logging(log, command)
    log.write(metricview(paths))


def fix_name_ascii(font_path, log=None):
    """ Replacing non ascii names in copyright """
    SCRIPTPATH = os.path.join(app.config['ROOT'], 'scripts', 'ascii.py')
    command = "{0} {1} {2}".format(PYPATH, SCRIPTPATH, font_path)
    logging(log, command)
    fix_name_table(font_path)
    shutil.move(font_path + '.fix', font_path, log=log)


def fix_fstype_to_zero(font_path, log=None):
    """ Fix fsType to zero """
    SCRIPTPATH = os.path.join(app.config['ROOT'], 'scripts', 'fstype.py')
    command = "{0} {1} --autofix {2}".format(PYPATH, SCRIPTPATH, font_path)
    logging(log, command)
    reset_fstype(font_path)
    shutil.move(font_path + '.fix', font_path, log=log)


def fix_ttf_stylenames(font_path, log=None):
    """ Fix style names """
    SCRIPTPATH = os.path.join(app.config['ROOT'], 'scripts', 'stylenames.py')

    command = "{0} {1} --autofix {2}".format(PYPATH, SCRIPTPATH, font_path)
    logging(log, command)
    fix_style_names(font_path)

    shutil.move(font_path + '.fix', font_path, log=log)


available_fixes = {
    'test_nbsp_and_space_glyphs_width': fix_nbsp,
    'test_metrics_linegaps_are_zero': fix_metrics,
    'test_metrics_ascents_equal_bbox': fix_metrics,
    'test_metrics_descents_equal_bbox': fix_metrics,
    'test_non_ascii_chars_in_names': fix_name_ascii,
    'test_is_fsType_not_set': fix_fstype_to_zero,
    'test_font_weight_is_canonical': fix_ttf_stylenames
}


def autofix(yaml_file, path, log=None, interactive=False):
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
