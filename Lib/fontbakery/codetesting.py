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
from functools import cached_property
from typing import Iterable, Optional

import defcon

from fontbakery.checkrunner import CheckRunner
from fontbakery.fonts_profile import (
    profile_factory,
    load_all_checks,
    setup_context,
    checks_by_id,
)
from fontbakery.status import PASS, DEBUG, INFO, ERROR, SKIP
from fontbakery.configuration import Configuration
from fontbakery.message import Message
from fontbakery.profile import Profile
from fontbakery.profile import Section
from fontbakery.testable import FILE_TYPES, CheckRunContext, Font, GlyphsFile, Ufo
from fontbakery.result import Subresult


PATH_TEST_DATA = "data/test/"
PATH_TEST_DATA_GLYPHS_FILES = f"{PATH_TEST_DATA}glyphs_files/"


def make_mock(basecls, name):
    # We want a new CheckRunContext/Font/etc with some user-supplied attributes.
    # But the attributes we want to feed in are generally properties, and
    # we can't calls setattr to override them because there is no setattr
    # for read-only properties.
    # So our mock class doesn't have *any* properties, just the mock values
    # we want to override. When we're asked for any other properties, we look
    # up the implementation from CheckRunContext and run that.
    cls = type(name, tuple(), {})

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __dir__(self):
        return dir(basecls) + list(self.__dict__.keys())

    def __getattr__(self, name):
        prop = getattr(basecls, name)
        if isinstance(prop, cached_property):
            return prop.func(self)
        if isinstance(prop, property):
            return prop.fget(self)
        return prop

    cls.__init__ = __init__
    cls.__getattr__ = __getattr__
    cls.__dir__ = __dir__
    cls.mocked = True
    return cls


MockContext = make_mock(CheckRunContext, "MockContext")
MockFont = make_mock(Font, "MockFont")
MockGlyphsFile = make_mock(GlyphsFile, "MockGlyphsFile")
MockUfo = make_mock(Ufo, "MockUfo")


class CheckTester:
    """
    This class offers a bit of automation to aid in the implementation of
    code-tests to validate the proper behaviour of FontBakery checks.
    """

    def __init__(self, check_id, profile=None):
        load_all_checks()
        # Generally we don't need a profile unless we're testing
        # overrides and configuration settings.
        if isinstance(profile, Profile):
            self.profile = profile
        elif profile:
            self.profile = profile_factory(profile)
        else:
            # We create a fake profile containing just this check
            self.profile = Profile(
                name="TestProfile",
                iterargs={val.singular: val.plural for val in FILE_TYPES},
                sections=[
                    Section(
                        name="Test",
                        checks=[checks_by_id[check_id]],
                    )
                ],
            )
        self.check_id = check_id

    def __call__(
        self, values, condition_overrides=None, config=None
    ) -> Iterable[Subresult]:
        from fontTools.ttLib import TTFont
        from glyphsLib import GSFont

        if condition_overrides:
            raise DeprecationWarning("Don't use condition_overrides, use a mock object")
        if isinstance(values, MockContext):
            context = values
        elif isinstance(values, str):
            context = setup_context([values])
        elif hasattr(values, "mocked"):
            context = CheckRunContext([values])
        elif isinstance(values, list) and all(hasattr(v, "mocked") for v in values):
            context = CheckRunContext(values)
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
                    context.testables.append(
                        MockFont(ttFont=value, file=value.reader.file.name)
                    )
                elif isinstance(value, GSFont):
                    context.testables.append(MockGlyphsFile(gsfont=value))
                elif isinstance(value, defcon.Font):
                    context.testables.append(MockUfo(ufo_font=value))
        for testable in context.testables:
            testable.context = context

        runner = CheckRunner(
            self.profile,
            context,
            Configuration(explicit_checks=[self.check_id], full_lists=True),
        )
        runner.catch_errors = False
        if config:
            for key, value in config.items():
                context.config[key] = value
        order = runner.order
        if not order:
            raise Exception(
                f"{self.check_id} check arguments could not be fulfilled for"
                " any files (may indicate bad condition)"
            )
        result = runner._run_check(order[0])
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

    # We'll ignore INFO and DEBUG messages:
    check_results = [r for r in check_results if r.status not in [INFO, DEBUG]]

    if not check_results:
        subresult = Subresult(PASS, Message("ok", "All looks good!"))
    else:
        subresult = check_results[-1]

    if ignore_error and subresult.status == ERROR:
        print(ignore_error)
    else:
        assert subresult.status == PASS


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
