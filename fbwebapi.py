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

from fontbakery.commands.check_profile import get_module, log_levels
from fontbakery.fonts_profile import profile_factory, setup_context
from fontbakery.reporters.serialize import SerializeReporter
from fontbakery.checkrunner import (
    CheckRunner,
)
from importlib import import_module


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
    profile = profile_factory(import_module("fontbakery.profiles." + profilename))
    context = setup_context(paths)
    runner = CheckRunner(
        profile,
        context,
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
