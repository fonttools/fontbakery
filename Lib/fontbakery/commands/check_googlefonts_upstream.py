#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from functools import partial
from fontbakery.specifications.googlefonts_upstream import specification
from fontbakery.commands.check_spec import main as super_main
from fontbakery.argumentparser import FBArgumentParser
import glob
# The values dict will probably get one or more specific blacklists
# for the google font project. It would be good if it was not necessary
# to copy paste this kind of configuration, thus a central init for
# the google/fonts repository is be good.
GOOGLEFONTS_UPSTREAM_SPECIFICS = {}

parser = FBArgumentParser(specification)
parser.add_argument('font_dirs', nargs='+')

args = parser.parse_args()
main = partial(super_main, args=args, 
                           specification=specification,
                           items_label='font_dirs',
                           values=GOOGLEFONTS_UPSTREAM_SPECIFICS)
