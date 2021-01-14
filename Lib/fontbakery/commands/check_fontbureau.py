#!/usr/bin/env python
import sys

from functools import partial
from fontbakery.profiles.fontbureau import profile
from fontbakery.commands.check_profile import (
    runner_factory as super_runner_factory, main as super_main)

FONT_BUREAU_SPECIFICS = {}


# runner_factory is used by the fontbakery dashboard.
# It is here in order to have a single place from which
# the profile is configured for the CLI and the worker.
def runner_factory(fonts):
    values = {}
    values.update(FONT_BUREAU_SPECIFICS)
    values['fonts'] = fonts
    return super_runner_factory(profile, values=values)


main = partial(super_main, profile, values=FONT_BUREAU_SPECIFICS)


if __name__ == '__main__':
    sys.exit(main())
