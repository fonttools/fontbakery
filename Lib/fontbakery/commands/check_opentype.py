#!/usr/bin/env python
import sys
from functools import partial

import fontbakery.profiles.opentype
from fontbakery.commands.check_profile import (
    main as super_main, get_module_profile)

main = partial(super_main,
               get_module_profile(fontbakery.profiles.opentype))

if __name__ == '__main__':
  sys.exit(main())
