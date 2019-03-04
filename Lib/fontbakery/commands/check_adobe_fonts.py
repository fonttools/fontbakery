#!/usr/bin/env python
import sys

from functools import partial
from fontbakery.specifications.adobe_fonts import specification
from fontbakery.commands.check_specification import (
    runner_factory as super_runner_factory, main as super_main)

# The values dict will probably get one or more specific blacklists
# for the google font project. It would be good if it was not necessary
# to copy paste this kind of configuration, thus a central init for
# the google/fonts repository is good.
ADOBE_FONTS_SPECIFICS = {}


# runner_factory is used by the fontbakery dashboard.
# It is here in order to have a single place from which
# the spec is configured for the CLI and the worker.
def runner_factory(fonts):
    values = {}
    values.update(ADOBE_FONTS_SPECIFICS)
    values['fonts'] = fonts
    return super_runner_factory(specification, values=values)


main = partial(super_main, specification, values=ADOBE_FONTS_SPECIFICS)


if __name__ == '__main__':
    sys.exit(main())
