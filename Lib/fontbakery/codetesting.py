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

from fontbakery.checkrunner import CheckRunner
from fontbakery.configuration import Configuration
from fontbakery.profile import Profile, get_module_profile


class CheckTester:
    """
    This class offers a bit of automation to aid in the implementation of
    code-tests to validade the proper behaviour of FontBakery checks.

    !!!CAUTION: this uses a lot of "private" methods and properties
    of CheckRunner, in order to make unit testing different cases simpler.

    This is not intended to run in production. However, if that is desired
    we may or may not find inspiration here on how to implement a proper
    public CheckRunner API.

    Not built for performance either!

    The idea is that we can let this class take care of computing
    the dependencies of a check for us. And we can also optionaly "fake"
    some of them in order to create useful testing scenarios for the checks.

    An initial run can be with unaltered arguments, as CheckRunner would
    produce them by itself. And subsequent calls can reuse some of them.
    """
    def __init__(self, module_or_profile, check_id):
        self.profile = module_or_profile \
                       if isinstance(module_or_profile, Profile) \
                       else get_module_profile(module_or_profile)
        self.check_id = check_id
        self.check_identity = None
        self.check_section = None
        self.check = None
        self.check_iterargs = None
        self._args = None

    def _get_args(self, condition_overrides=None):
        if condition_overrides is not None:
            for name_key, value in condition_overrides.items():
                if isinstance(name_key, str):
                    # this is a simplified form of a cache key:
                    # write the conditions directly to the iterargs of the check identity
                    used_iterargs = self.runner._filter_condition_used_iterargs(name_key, self.check_iterargs)
                    key = (name_key, used_iterargs)
                else:
                    # Full control for the caller, who has to inspect how
                    # the desired key needs to be set up.
                    key = name_key
                #                                      error, value
                self.runner._cache['conditions'][key] = None, value
        args = self.runner._get_args(self.check, self.check_iterargs)
        # args that are derived iterables are generators that must be
        # converted to lists, otherwise we end up with exhausted
        # generators after their first consumption.
        for k in args:
            if self.profile.get_type(k, None) == 'derived_iterables':
                args[k] = list(args[k])
        return args

    def __getitem__(self, key):
        if key in self._args:
            return self._args[key]

        used_iterargs = self.runner._filter_condition_used_iterargs(key, self.check_iterargs)
        key = (key, used_iterargs)
        if key in self.runner._cache['conditions']:
            return self.runner._cache['conditions'][key][1]

    def __call__(self, values, condition_overrides={}):
        from fontTools.ttLib import TTFont
        if isinstance(values, str):
            values = {'font': values,
                      'fonts': [values]}
        elif isinstance(values, TTFont):
            values = {'font': values.reader.file.name,
                      'fonts': [values.reader.file.name],
                      'ttFont': values,
                      'ttFonts': [values]}
        elif isinstance(values, list):
            if isinstance(values[0], str):
                values = {'fonts': values}
            elif isinstance(values[0], TTFont):
                values = {'fonts': [v.reader.file.name for v in values],
                          'ttFonts': values}

        self.runner = CheckRunner(self.profile, values, Configuration(explicit_checks=[self.check_id]))
        for check_identity in self.runner.order:
            _, check, _ = check_identity
            if check.id != self.check_id:
                continue
            self.check_identity = check_identity
            self.check_section, self.check, self.check_iterargs = check_identity
            break
        if self.check_identity is None:
            raise KeyError(f'Check with id "{self.check_id}" not found.')

        self._args = self._get_args(condition_overrides)
        return list(self.runner._exec_check(self.check, self._args))


def portable_path(p):
    import os
    return os.path.join(*p.split('/'))


def TEST_FILE(f):
    return portable_path("data/test/" + f)


def assert_PASS(check_results, reason="with a good font...", ignore_error=None):
    from fontbakery.checkrunner import PASS, ERROR
    print(f"Test PASS {reason}")
    status, message = list(check_results)[-1]
    if ignore_error and status == ERROR:
        print(ignore_error)
        return None
    else:
        assert status == PASS
        return str(message)


def assert_SKIP(check_results, reason=""):
    from fontbakery.checkrunner import SKIP
    print(f"Test SKIP {reason}")
    status, message = list(check_results)[-1]
    assert status == SKIP
    return str(message)


def assert_results_contain(check_results,
                           expected_status,
                           expected_msgcode=None,
                           reason=None,
                           ignore_error=None):
    """
    This helper function is useful when we want to make sure that
    a certain log message is emited by a check but it can be in any
    order among other log messages.
    """
    from fontbakery.message import Message
    from fontbakery.checkrunner import PASS, DEBUG, ERROR
    if not reason:
        reason = f"[{expected_msgcode}]"
    if not expected_msgcode:
      raise Exception("Test must expect a message code")

    print(f"Test {expected_status} {reason}")
    check_results = list(check_results)

    for status, _ in check_results:
        if ignore_error and status == ERROR:
            print(ignore_error)
            return None

    for status, msg in check_results:
        if status not in [PASS, DEBUG] and not isinstance(msg, Message):
            raise Exception(f"Bare Python strings no longer supported in result values.\n"
                f"Please use the Message class to wrap strings and to give them"
                f" a keyword useful for identifying them (on bug reports as well as"
                f" in the implementation of reliable code-tests).\n"
                f"(Bare string: '{msg}')")

        if (status == expected_status and
            expected_msgcode == None or
            (isinstance(msg, Message) and msg.code == expected_msgcode)):
            if isinstance(msg, Message):
                return msg.message
            else:
                return msg # It is probably a plain python string

    #if not found:
    raise Exception(f"Expected to find {expected_status}, [code: {expected_msgcode}]\n"
                    f"But did not find it in:\n"
                    f"{check_results}")
