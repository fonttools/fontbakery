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

def get_check(profile, checkid):
    def _checker(value):
        from fontTools.ttLib import TTFont
        from fontbakery.fonts_profile import execute_check_once
        if isinstance(value, str):
            return execute_check_once(profile, checkid, value)

        elif isinstance(value, TTFont):
            return execute_check_once(profile, checkid, value.reader.file.name,
                                      {'ttFont': value})
#
# TODO: I am not sure how to properly handle these cases:
#
#        elif isinstance(value, list):
#            if isinstance(value[0], str):
#                return execute_check_once(profile, checkid, value)
#
#            elif isinstance(value[0], TTFont):
#                return execute_check_once(profile, checkid, "",
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
