import sys
import types
from mock import MagicMock
import unicodedata

sys.modules["unicodedata2"] = sys.modules["unicodedata"]
for notreal in [
    "cmarkgfm",
    "cmarkgfm.cmark",
    "toml",
    "rich",
    "pyyaml",
    "yaml",
    "glyphsLib",
    "glyphsLib.glyphdata",
    "defcon",
    "vharfbuzz",
    "uharfbuzz",
]:
    sys.modules[notreal] = MagicMock()

import glyphsets

import argparse
from fontbakery.commands.check_profile import get_module, log_levels
from fontbakery.reporters.serialize import SerializeReporter
from fontbakery.checkrunner import (
    get_module_profile,
    CheckRunner,
    START,
    ENDCHECK,
    distribute_generator,
)
import fontbakery
import pkgutil
from importlib import import_module
import re


class ProgressReporter(SerializeReporter):
    def __init__(self, callback, loglevels):
        super().__init__(loglevels)
        self.count = 0
        self.callback = callback

    def receive(self, event):
        super().receive(event)
        status, message, identity = event
        section, check, iterargs = identity
        key = self._get_key(identity)
        done = self.count - self._counter["(not finished)"]
        if status == START:
            self.count = len(message)
        elif status == ENDCHECK:
            self._items[key]["key"] = check.id
            self._items[key]["doc"] = check.__doc__
            self.callback({"progress": 100 * done / float(self.count)} | self._counter)
            if message >= self.loglevels:
                self.callback(self._items[key])


def run_fontbakery(
    paths,
    callback,
    profilename="universal",
    loglevels="INFO",
    checks=None,
    exclude_checks=None,
    full_lists=False,
):
    loglevels = log_levels[loglevels]
    profile = get_module_profile(get_module("fontbakery.profiles." + profilename))
    argument_parser = argparse.ArgumentParser()
    # Hack
    argument_parser.add_argument(
        "--list-checks",
        default=False,
        action="store_true",
        help="List the checks available in the selected profile.",
    )
    values_keys = profile.setup_argparse(argument_parser)
    args = argument_parser.parse_args(paths)
    values = {}
    for key in values_keys:
        if hasattr(args, key):
            values[key] = getattr(args, key)
    runner = CheckRunner(
        profile,
        values=values,
        config={
            "custom_order": None,
            "explicit_checks": checks,
            "exclude_checks": exclude_checks,
            "full_lists": full_lists,
        },
    )
    prog = ProgressReporter(callback, loglevels)
    prog.runner = runner
    reporters = [prog.receive]
    status_generator = runner.run()
    distribute_generator(status_generator, reporters)


def dump_all_the_checks():
    checks = {}
    profiles_modules = [
        x.name
        for x in pkgutil.walk_packages(fontbakery.__path__, "fontbakery.")
        if x.name.startswith("fontbakery.profiles")
    ]
    for profile_name in profiles_modules:
        try:
            imported = import_module(profile_name, package=None)
        except BaseException:
            continue
        profile = get_module_profile(imported)
        if not profile:
            continue
        profile_name = profile_name[20:]
        for section in profile._sections.values():
            for check in section._checks:
                if check.id not in checks:
                    checks[check.id] = {
                        "sections": set(),
                        "profiles": set(),
                    }
                checks[check.id]["sections"].add(section.name)
                checks[check.id]["profiles"].add(profile_name)
                for attr in ["proposal", "rationale", "severity", "description"]:
                    if getattr(check, attr):
                        md = getattr(check, attr)
                        if attr == "rationale":
                            md = re.sub(r"(?m)^\s+", "", md)
                            checks[check.id][attr] = md
                        else:
                            checks[check.id][attr] = md

    for ck in checks.values():
        ck["sections"] = list(ck["sections"])
        ck["profiles"] = list(ck["profiles"])
    return checks
