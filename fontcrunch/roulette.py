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
from math import *

sc = 100

def hyperb_here(xo, x, y, th, lw, center):
    print 'gsave 306 396 translate', sc, 'dup scale', lw / sc, 'setlinewidth'
    print xo, 0, 'translate'
    print -th * 180 / pi, 'rotate'
    print -x, -y, 'translate'
    cmd = 'moveto'
    for i in range(-20, 21):
	x = i * .1
	y = sqrt(1 + x * x)
	print x, y, cmd
	cmd = 'lineto'
    print 'stroke'
    if center:
	print 1.0 / sc, 'setlinewidth'
	print '[.02 .04] 0 setdash'
	s = 2
	print -s, s, 'moveto', 0, 0, 'lineto', s, s, 'lineto stroke'
    print 'grestore'

def sturm_roulette():
    print '%!PS-Adobe-3.0 EPSF'
    print '/ss 2 def'
    print '/circle { ss 0 moveto currentpoint exch ss sub exch ss 0 360 arc } bind def'
    print 'gsave 0.75 setlinewidth'
    print 306 - 220, 396, 'moveto', 440, 0, 'rlineto stroke grestore'
    ds = 0.05
    x = 0
    rxy = []
    for i in range(200):
	xo = ds * i
	y = sqrt(1 + x * x)
	th = atan2(x, sqrt(1 + x * x))
	x1 = -x
	y1 = -y
	rx = xo + x1 * cos(th) + y1 * sin(th)
	ry =      y1 * cos(th) - x1 * sin(th)
	rxy.append((rx, ry))
	if i in [0, 8]:
	    if i == 0: lw = 1.5
	    else: lw = 1.0
	    hyperb_here(xo, x, y, th, lw, True)
	    print 'gsave', 306 + sc * rx, 396 + sc * ry, 'translate circle fill grestore'
	x += ds * cos(th)
    rxy.append((rxy[-1][0], 0)) # cheap hack
    cmd = 'moveto'
    for (x, y) in rxy[-1:0:-1]:
	print 306 - sc * x, 396 + sc * y, cmd
	cmd = 'lineto'
    for (x, y) in rxy:
	print 306 + sc * x, 396 + sc * y, cmd
	cmd = 'lineto'
    print 'stroke'
    print 'showpage'
    print '%', rxy


sturm_roulette()
