#!/usr/bin/env python
import sys
from functools import partial

from fontbakery.commands.check_profile import main as super_main
from fontbakery.profiles.ufo_sources import profile



main = partial(super_main, profile)

if __name__ == '__main__':
    sys.exit(main())
