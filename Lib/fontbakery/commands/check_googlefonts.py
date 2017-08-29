#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from functools import partial
from fontbakery.specifications.googlefonts import specification
from fontbakery.commands.check_spec import (
                                             runner_factory as super_runner_factory
                                           , main as super_main
                                           )

# The values dict will probably get one or more specific blacklists
# for the google font project. It would be good if it was not necessary
# to copy paste this kind of configuration, thus a central init for
# the google/fonts repository is be good.
GOOGLEFONTS_SPECIFICS = {}

runner_factory = partial(super_runner_factory, specification, values=GOOGLEFONTS_SPECIFICS)
main = partial(super_main, specification, values=GOOGLEFONTS_SPECIFICS)

