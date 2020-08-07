#!/usr/bin/env python3
# Copyright 2020 The Fontbakery Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from fontbakery.checkrunner import CheckRunner, Profile, get_module_profile


def execute_check_once(module_or_profile, check_id, values, condition_overrides=None):
    """ Run a check in the profile once and return a list of its result statuses.

        This is a helper function intended for code testing only. as such
        it is a bit crude. Don't use it as a general API. Don't consider it
        mature.
    """
    profile = module_or_profile if isinstance(module_or_profile, Profile) \
                                else get_module_profile(module_or_profile)
    runner = CheckRunner(profile, values, explicit_checks=[check_id])
    for check_identity in runner.order:
        _, check, iterargs = check_identity
        if check.id != check_id:
            continue

        if condition_overrides:
            for name, value in condition_overrides.items():
                # write the conditions directly to the iterargs of the check identity
                used_iterargs = runner._filter_condition_used_iterargs(name, iterargs)
                key = (name, used_iterargs)
                # error, value
                runner._cache['conditions'][key] = None, value
        # removes STARTCHECK and ENDCHECK
        return list(runner._run_check(check, iterargs))[1:-1]
    raise KeyError(f'Check with id "{check_id}" not found.')

# for code testing
def execute_check_once_fonts(module_or_profile, check_id, font, condition_overrides=None):
    """Run a check of profile once, with font (file path) as value and/or
    with condition_overrides.

    Example that doesn't use `font`:

    > from fontbakery.fonts_profile import execute_check_once
    > from fontbakery.profiles import gdef
    > from fontTools.ttLib.ttFont import TTFont
    > ttf = TTFont('/path/to/Family-Regular.ttf')
    > execute_check_once(gdef, 'com.google.fonts/check/gdef_spacing_marks', 'not a file', {'ttFont': ttf})
    [(<Status PASS>,
          'Font does not has spacing glyphs in the GDEF mark glyph class.')]
    """
    values = {'fonts': [font]}
    return execute_check_once(module_or_profile, check_id, values, condition_overrides)

def get_check(profile, checkid):
    def _checker(value):
        from fontTools.ttLib import TTFont
        if isinstance(value, str):
            return execute_check_once_fonts(profile, checkid, value)

        elif isinstance(value, TTFont):
            return execute_check_once_fonts(profile, checkid, value.reader.file.name,
                                      {'ttFont': value})
#
# TODO: I am not sure how to properly handle these cases:
#
#        elif isinstance(value, list):
#            if isinstance(value[0], str):
#                return execute_check_once_fonts(profile, checkid, value)
#
#            elif isinstance(value[0], TTFont):
#                return execute_check_once_fonts(profile, checkid, "",
#                                          {'ttFonts': value})
    return _checker


def portable_path(p):
    import os
    return os.path.join(*p.split('/'))


def TEST_FILE(f):
    return portable_path("data/test/" + f)


def assert_PASS(check_results, reason="with a good font..."):
    from fontbakery.checkrunner import PASS
    print(f"Test PASS {reason}")
    status, message = list(check_results)[-1]
    assert status == PASS
    return str(message)


def assert_SKIP(check_results, reason=""):
    from fontbakery.checkrunner import SKIP
    print(f"Test SKIP {reason}")
    status, message = list(check_results)[-1]
    assert status == SKIP
    return str(message)


def assert_results_contain(check_results, expected_status, expected_msgcode=None, reason=None):
    """
    This helper function is useful when we want to make sure that
    a certain log message is emited by a check but it can be in any
    order among other log messages.
    """
    from fontbakery.message import Message
    if not reason:
        reason = f"[{expected_msgcode}]"

    print(f"Test {expected_status} {reason}")
    check_results = list(check_results)
    for status, msg in check_results:
        if (status == expected_status and
            expected_msgcode == None or
            (isinstance(msg, Message) and msg.code == expected_msgcode)): # At some point we will make
                                                                          # message keywords mandatory!
            if isinstance(msg, Message):
                return msg.message
            else:
                return msg # It is probably a plain python string

    #if not found:
    raise Exception(f"Expected to find {expected_status}, [code: {expected_msgcode}]\n"
                    f"But did not find it in:\n"
                    f"{check_results}")
