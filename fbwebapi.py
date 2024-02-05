import sys
from mock import MagicMock
from importlib import import_module
import unicodedata
import json

sys.modules["unicodedata2"] = sys.modules["unicodedata"]
for notreal in [
    "cmarkgfm",
    "cmarkgfm.cmark",
    "toml",
    "rich",
    "rich.theme",
    "rich.segment",
    "rich.live",
    "rich.markdown",
    "rich.markup",
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
    CheckRunner,
)
import fontbakery
import pkgutil
from importlib import import_module
import re


class ProgressReporter(SerializeReporter):
    def __init__(self, callback, loglevels):
        super().__init__(loglevels=loglevels)
        self.count = 0
        self.callback = callback

    def start(self, order):
        super().start(order)
        self.count = len(order)

    def receive_result(self, checkresult):
        super().receive_result(checkresult)
        done = self.count - self._counter["(not finished)"]
        key = checkresult.identity.key
        self.callback({"progress": 100 * done / float(self.count)} | self._counter)
        data = checkresult.getData(self.runner)
        data["key"] = checkresult.identity.check.id
        for log in data["logs"]:
            if type(log["message"]["message"]).__name__ == "FailedConditionError":
                log["message"]["message"] = str(log["message"]["message"])
        data = json.loads(json.dumps(data))
        self.callback(data)


def run_fontbakery(
    paths,
    callback,
    profilename="universal",
    loglevels="INFO",
    checks=None,
    exclude_checks=None,
    full_lists=False,
):
    loglevels = [log_levels[loglevels]]
    profile = import_module("fontbakery.profiles." + profilename).profile
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
    reporters = [prog]
    runner.run(reporters)


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
            profile = imported.profile
        except BaseException:
            continue
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
