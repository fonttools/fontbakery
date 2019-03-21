#!/usr/bin/env python
import sys

from functools import partial
from fontbakery.profiles.fontval import profile
from fontbakery.commands.check_profile import (
    runner_factory as super_runner_factory, main as super_main)

# runner_factory is used by the fontbakery dashboard.
# It is here in order to have a single place from which
# the profile is configured for the CLI and the worker.
def runner_factory(fonts):
    values = {}
    values['fonts'] = fonts
    return super_runner_factory(profile, values=values)

main = partial(super_main, profile)


if __name__ == '__main__':
    sys.exit(main())
