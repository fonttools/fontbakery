#!/usr/bin/env python
import sys

from functools import partial
from fontbakery.specifications.fontval import specification
from fontbakery.commands.check_specification import (
    runner_factory as super_runner_factory, main as super_main)

# runner_factory is used by the fontbakery dashboard.
# It is here in order to have a single place from which
# the spec is configured for the CLI and the worker.
def runner_factory(fonts):
    values = {}
    values['fonts'] = fonts
    return super_runner_factory(specification, values=values)

main = partial(super_main, specification)


if __name__ == '__main__':
    sys.exit(main())
