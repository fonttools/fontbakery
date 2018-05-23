#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import sys
from functools import partial

import fontbakery.specifications.opentype
from fontbakery.commands.check_specification import (
    main as super_main, get_module_specification)

main = partial(super_main,
               get_module_specification(fontbakery.specifications.opentype))

if __name__ == '__main__':
  sys.exit(main())
