#!/usr/bin/env python
import sys

from functools import partial
from fontbakery.profiles.googlefonts import profile
from fontbakery.commands.check_profile import (
    runner_factory as super_runner_factory, main as super_main)

# The values dict will probably get one or more specific blacklists
# for the google font project. It would be good if it was not necessary
# to copy paste this kind of configuration, thus a central init for
# the google/fonts repository is good.
GOOGLEFONTS_SPECIFICS = {}

# runner_factory is used by the fontbakery dashboard.
# It is here in order to have a single place from which
# the profile is configured for the CLI and the worker.
def runner_factory(fonts):
    values = {}
    values.update(GOOGLEFONTS_SPECIFICS)
    values['fonts'] = fonts
    return super_runner_factory(profile, values=values)

main = partial(super_main, profile, values=GOOGLEFONTS_SPECIFICS)


if __name__ == '__main__':
    sys.exit(main())
