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

from fontTools.ttLib import TTFont
from bakery_cli.scripts.vmet import metricview, metricfix
from bakery_cli.scripts import SpecCharsForASCIIFixer, CreateDSIGFixer, \
    ResetFSTypeFlagFixer, AddSPUAByGlyphIDToCmap, NbspAndSpaceSameWidth, \
    GaspFixer
from bakery_cli.scripts import opentype
from bakery_cli.scripts import gasp
from bakery_cli.utils import shutil
from bakery_cli.utils import UpstreamDirectory


def replace_licenseurl(testcase):
    font = TTFont(testcase.operator.path)

    for nameRecord in font['name'].names:
        if nameRecord.nameID == 14:
            if nameRecord.isUnicode():
                nameRecord.string = testcase.placeholderUrlText.encode('utf-16-be')
            else:
                nameRecord.string = testcase.placeholderUrlText
    font.save(testcase.operator.path + '.fix')
    replace_origfont(testcase)


def replace_license_with_short(testcase):
    font = TTFont(testcase.operator.path)

    for nameRecord in font['name'].names:
        if nameRecord.nameID == 13:
            if nameRecord.isUnicode():
                nameRecord.string = testcase.placeholderText.encode('utf-16-be')
            else:
                nameRecord.string = testcase.placeholderText

    testcase.operator.debug('SETTING UP: {}'.format(testcase.placeholderText))
    font.save(testcase.operator.path + '.fix')
    replace_origfont(testcase)


def remove_description_with_substr(testcase):
    ttf = TTFont(testcase.operator.path)
    records = []
    for record in ttf['name'].names:
        passed = True
        for namerecord in testcase.namerecords:
            if (record.nameID == namerecord.nameID
                    and record.platformID == namerecord.platformID
                    and record.platEncID == namerecord.platEncID
                    and record.langID == namerecord.langID):
                passed = False
                break
        if passed:
            records.append(record)
    ttf['name'].names = records
    ttf.save(testcase.operator.path + '.fix')
    replace_origfont(testcase)


def replace_origfont(testcase):
    targetpath = testcase.operator.path
    command = "$ mv {0}.fix {0}".format(targetpath)
    if hasattr(testcase, 'operator'):
        testcase.operator.debug(command)
    fixed_font_path = '{}.fix'.format(targetpath)
    if op.exists(fixed_font_path):
        shutil.move(fixed_font_path, targetpath)


def dsig_signature(testcase):
    """ Create "DSIG" table with default signaturerecord """
    targetpath = testcase.operator.path

    SCRIPTPATH = 'fontbakery-fix-dsig.py'

    command = "$ {0} {1}".format(SCRIPTPATH, targetpath)
    if hasattr(testcase, 'operator'):
        testcase.operator.debug(command)

    CreateDSIGFixer(targetpath).apply()

    replace_origfont(testcase)


def gaspfix(testcase):
    """ Set in "gasp" table value of key "65535" to "15" """
    targetpath = testcase.operator.path

    SCRIPTPATH = 'fontbakery-fix-gasp.py'

    command = "$ {0} --set={1} {2}".format(SCRIPTPATH, 15, targetpath)
    if hasattr(testcase, 'operator'):
        testcase.operator.debug(command)

    if GaspFixer(targetpath).apply(15):
        replace_origfont(testcase)


def fix_opentype_specific_fields(testcase):
    """ Fix Opentype-specific fields in "name" table """
    targetpath = testcase.operator.path
    SCRIPTPATH = 'fontbakery-fix-opentype-names.py'

    command = "$ {0} {1}".format(SCRIPTPATH, targetpath)
    if hasattr(testcase, 'operator'):
        testcase.operator.debug(command)

    opentype.fix(targetpath)

    replace_origfont(testcase)


def fix_nbsp(testcase):
    """ Fix width for space and nbsp """
    targetpath = testcase.operator.path

    SCRIPTPATH = 'fontbakery-fix-nbsp.py'

    command = "$ {0} {1}".format(SCRIPTPATH, targetpath)
    if hasattr(testcase, 'operator'):
        testcase.operator.debug(command)
    if NbspAndSpaceSameWidth(targetpath).apply():
        replace_origfont(testcase)


def fix_metrics(testcase):
    """ Fix vmet table with actual min and max values """
    targetpath = os.path.dirname(testcase.operator.path)
    SCRIPTPATH = 'fontbakery-fix-vertical-metrics.py'

    directory = UpstreamDirectory(targetpath)

    paths = []
    for f in directory.BIN:
        path = op.join(targetpath, f)
        paths.append(path)

    command = "$ {0} --autofix {1}"
    command = command.format(SCRIPTPATH, ' '.join(paths))
    if hasattr(testcase, 'operator'):
        testcase.operator.debug(command)

    metricfix(paths)

    for path in paths:
        try:
            shutil.move(path + '.fix', path, log=testcase.operator.logger)
        except IOError:
            pass

    command = "$ {0} {1}".format(SCRIPTPATH, ' '.join(paths))
    if hasattr(testcase, 'operator'):
        testcase.operator.debug(command)
        testcase.operator.debug(metricview(paths))


def fix_name_ascii(testcase):
    """ Replacing non ascii names in copyright """
    targetpath = testcase.operator.path

    SCRIPTPATH = 'fontbakery-fix-ascii-fontmetadata.py'
    command = "$ {0} {1}".format(SCRIPTPATH, targetpath)
    if hasattr(testcase, 'operator'):
        testcase.operator.debug(command)

    if SpecCharsForASCIIFixer(targetpath).apply():
        replace_origfont(testcase)


def fix_fstype_to_zero(testcase):
    """ Fix fsType to zero """
    targetpath = testcase.operator.path

    SCRIPTPATH = 'fontbakery-fix-fstype.py'
    command = "$ {0} --autofix {1}".format(SCRIPTPATH, targetpath)
    if hasattr(testcase, 'operator'):
        testcase.operator.debug(command)

    if ResetFSTypeFlagFixer(targetpath).apply():
        replace_origfont(testcase)


def fix_encode_glyphs(testcase):
    targetpath = testcase.operator.path
    SCRIPTPATH = 'fontbakery-fix-glyph-private-encoding.py'
    command = "$ {0} --autofix {1}".format(SCRIPTPATH, targetpath)
    if hasattr(testcase, 'operator'):
        testcase.operator.debug(command)

    fixer = AddSPUAByGlyphIDToCmap(targetpath)
    if fixer.apply():
        replace_origfont(testcase)


def rename(testcase):
    targetpath = testcase.operator.path

    new_targetpath = op.join(op.dirname(targetpath),
                             testcase.expectedfilename)
    shutil.move(targetpath, new_targetpath, log=testcase.operator.logger)

    testcase.operator.path = new_targetpath
