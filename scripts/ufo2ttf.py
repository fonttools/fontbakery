#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
# hardcoded for OSX
# sys.path.append('/usr/local/lib/python2.7/site-packages/')
print(sys.argv[1], sys.argv[2])

import fontforge

font = fontforge.open(sys.argv[1])

font.layers["Fore"].is_quadratic = True
font.selection.all()
#   Add Extrema
font.addExtrema()
#   Simplify
font.simplify(1,('setstarttoextremum','removesingletonpoints'))
#   Correct Directions
font.correctDirection()

ttf = font.generate(sys.argv[2])
otf = font.generate(sys.argv[3])
