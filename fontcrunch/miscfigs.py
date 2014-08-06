# coding: utf-8
# Copyright 2013 The Font Bakery Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# See AUTHORS.txt for the list of Authors and LICENSE.txt for the License.
import sys
import math

import tocubic
import fromcubic

def lerp(z0, z1, t):
    return (z0[0] + t * (z1[0] - z0[0]), z0[1] + t * (z1[1] - z0[1]))

def lerpbz(bz0, bz1, t):
    return [lerp(bz0[i], bz1[i], t) for i in range(len(bz0))]

def bzscale(bz, xscale, yscale):
    return [(x * xscale, y * yscale) for x, y in bz]

def bztranslate(bz, xoff, yoff):
    return [(x + xoff, y + yoff) for x, y in bz]

# Subdivide a cubic Bezier segment into two, using de Casteljau
def decasteljau(bez, t):
    z0, z1, z2, z3 = bez
    z01 = lerp(z0, z1, t)
    z12 = lerp(z1, z2, t)
    z23 = lerp(z2, z3, t)
    z012 = lerp(z01, z12, t)
    z123 = lerp(z12, z23, t)
    z0123 = lerp(z012, z123, t)
    return [z0, z01, z012, z0123], [z0123, z123, z23, z3]

def bezinterp():
    tocubic.plot_prolog()
    print '/ss 1.5 def'
    print '/circle { ss 0 moveto currentpoint exch ss sub exch ss 0 360 arc } bind def'
    C1 = 0.55228
    bz = [(0, 0), (0, 100 * C1), (100 - 100 * C1, 100), (100, 100)]

    bz00, bz01 = decasteljau(bzscale(bz, 0.5, 1), .4)
    bz00 = bztranslate(bz00, 200, 0)
    bz01 = bztranslate(bz01, 200, 0)
    fromcubic.plot_bzs([[bz00, bz01]], (0, 0), 1, True)

    bz10, bz11 = decasteljau(bzscale(bz, 2.0, 1), .6)
    bz10 = bztranslate(bz10, 350, 0)
    bz11 = bztranslate(bz11, 350, 0)
    fromcubic.plot_bzs([[bz10, bz11]], (0, 0), 1, True)

    for t in (.333,):
	bz20 = bztranslate(lerpbz(bz00, bz10, t), 0, 0)
	bz21 = bztranslate(lerpbz(bz01, bz11, t), 0, 0)
	fromcubic.plot_bzs([[bz20, bz21]], (0, 0), 1, True)

    print 'gsave 0.75 setlinewidth [2 3] 0 setdash'
    for bz0, bz1, imax in ((bz00, bz10, 3), (bz01, bz11, 4)):
	for i in range(imax):
	    print bz0[i][0], bz0[i][1], 'moveto'
	    print bz1[i][0], bz1[i][1], 'lineto stroke'
    print 'grestore'

    print 'showpage'

def quantcircle(n):
    tocubic.plot_prolog()
    r = 100.0 / n
    arc = []
    lastx = 0
    for y in range(n, 0, -1):
	x = math.floor(math.sqrt((n + .5) * (n + .5) - y * y))
	if x != lastx: arc.append((x, y))
	arc.append((x, y - 1))
	lastx = x
    half = arc[:]
    arc.reverse()
    half += [(x, -y) for x, y in arc[1:]]
    print '%', half
    circle = half[:]
    half.reverse()
    circle += [(-x, y) for x, y in half]
    print '%', circle
    cmd = 'm'
    for x, y in circle:
	print 306 + r * x, 396 + r * y, cmd
	cmd = 'l'
    print 'z stroke'
    print 'showpage'

def warpedcircle(n):
    print '(plate'
    for i in range(8):
	r = 100 * (1 - math.sqrt(.5) * (-1) ** i / n)
	x = 306 + r * math.cos(i * math.pi / 4)
	y = 396 + r * math.sin(i * math.pi / 4)
	print '  (c %f %f)' % (x, y)
    print '  (z)'
    print ')'

if __name__ == '__main__':
    if sys.argv[1] == 'bezinterp.pdf':
	bezinterp()
    elif sys.argv[1] in ('quantcircle.pdf', 'warpedcircle.plate'):
	n = 40
	if len(sys.argv) > 2:
	    n = int(sys.argv[2])
	if sys.argv[1] == 'quantcircle.pdf':
	    quantcircle(n)
	else:
	    warpedcircle(n)
