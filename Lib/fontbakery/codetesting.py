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
import types
from typing import Iterable, Optional

import defcon

from fontbakery.checkrunner import CheckRunner
from fontbakery.fonts_profile import profile_factory
from fontbakery.status import PASS, DEBUG, ERROR, SKIP
from fontbakery.configuration import Configuration
from fontbakery.message import Message
from fontbakery.profile import Profile
from fontbakery.fonts_profile import setup_context
from fontbakery.testable import CheckRunContext, Font
from fontbakery.result import Subresult


PATH_TEST_DATA = "data/test/"
PATH_TEST_DATA_GLYPHS_FILES = f"{PATH_TEST_DATA}glyphs_files/"


class FakeFont(Font):
    def __init__(self, ttFont):
        self._ttFont = ttFont
    
    @property
    def ttFont(self):
        return self._ttFont
    
    @property
    def file(self):
        return self._ttFont.reader.file.name

class CheckTester:
    """
    This class offers a bit of automation to aid in the implementation of
    code-tests to validade the proper behaviour of FontBakery checks.
    """

    def __init__(self, module_or_profile, check_id):
        if isinstance(module_or_profile, Profile):
            self.profile = module_or_profile
        else:
            self.profile = profile_factory(module_or_profile)
        self.check_id = check_id
        self.check_identity = None
        self.check_section = None
        self.check = None
        self.check_iterargs = None
        self.runner = None
        self._args = None

    def __call__(self, values, condition_overrides=None) -> Iterable[Subresult]:
        from fontTools.ttLib import TTFont
        from glyphsLib import GSFont

        if isinstance(values, str):
            context = setup_context([values])
        elif isinstance(values, list) and all(isinstance(v, str) for v in values):
            context = CheckRunContext([])
            # Assert that they're fonts
            context.testables.extend(Font(v) for v in values)
        else:
            if isinstance(values, (TTFont, GSFont, defcon.Font)):
                values = [values]
            context = CheckRunContext([])
            for value in values:
                if isinstance(value, TTFont):
                    context.testables.append(FakeFont(value))
                elif isinstance(value, GSFont):
                    context.testables.append(FakeGSFont(value))
                elif isinstance(value, defcon.Font):
                    context.testables.append(FakeUFO(value))

        self.runner = CheckRunner(
            self.profile,
            context,
            Configuration(explicit_checks=[self.check_id], full_lists=True),
        )
        if condition_overrides:
            for condition, value in condition_overrides.items():
                setattr(self.runner.context, condition, value)
        result = self.runner._run_check(self.runner.order[0])
        return result.results


def portable_path(p):
    import os

    return os.path.join(*p.split("/"))


def TEST_FILE(f):
    return portable_path(f"{PATH_TEST_DATA}{f}")


def GLYPHSAPP_TEST_FILE(f):
    import glyphsLib

    the_file = portable_path(f"{PATH_TEST_DATA_GLYPHS_FILES}{f}")
    return glyphsLib.load(open(the_file, encoding="utf-8"))


def assert_PASS(check_results, reason="with a good font...", ignore_error=None):
    print(f"Test PASS {reason}")
    subresult = check_results[-1]
    if ignore_error and subresult.status == ERROR:
        print(ignore_error)
        return None
    else:
        assert subresult.status == PASS
        return str(subresult.message)


def assert_SKIP(check_results, reason=""):
    print(f"Test SKIP {reason}")
    subresult = list(check_results)[-1]
    assert subresult.status == SKIP
    return str(subresult.message)


def assert_results_contain(
    check_results, expected_status, expected_msgcode, reason=None, ignore_error=None
) -> Optional[str]:
    """
    This helper function is useful when we want to make sure that
    a certain log message is emited by a check but it can be in any
    order among other log messages.
    """
    if not isinstance(expected_msgcode, str):
        raise Exception("The expected message code must be a string")

    if not reason:
        reason = f"[{expected_msgcode}]"

    print(f"Test {expected_status} {reason}")
    check_results = list(check_results)

    for subresult in check_results:
        if ignore_error and subresult.status == ERROR:
            print(ignore_error)
            return None

    for subresult in check_results:
        if subresult.status not in [PASS, DEBUG] and not isinstance(
            subresult.message, Message
        ):
            raise Exception(
                f"Bare Python strings are no longer supported in result values.\n"
                f"Please use the Message class to wrap strings and to give them"
                f" a keyword useful for identifying them (in bug reports as well as"
                f" in the implementation of reliable unit tests).\n"
                f"(Bare string: {subresult.message!r})"
            )

        if subresult.status == expected_status and (
            subresult.message.code == expected_msgcode  # pylint: disable=R1714
            or subresult.message.message == expected_msgcode  # deprecated
        ):
            return subresult.message.message

    # if no match was found
    raise Exception(
        f"Expected to find {expected_status}, [code: {expected_msgcode}]\n"
        f"But did not find it in:\n"
        f"{check_results}"
    )


class MockContext:
    # We want a new CheckRunContext with some user-supplied attributes.
    # But the attributes we want to feed in are generally properties, and
    # we can't calls setattr to override them because there is no setattr
    # for read-only properties.
    # So our mock class doesn't have *any* properties, just the mock values
    # we want to override. When we're asked for any other properties, we look
    # up the implementation from CheckRunContext and run that.
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __getattr__(self, name):
        prop = getattr(CheckRunContext, name)
        return prop.fget(self)
