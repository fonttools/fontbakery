#!/usr/bin/env python
import sys

from functools import partial
from fontbakery.profiles.typenetwork import profile, BLOCKLISTS
from fontbakery.commands.check_profile import main as super_main


main = partial(super_main, profile, values=BLOCKLISTS)


if __name__ == '__main__':
    sys.exit(main())
