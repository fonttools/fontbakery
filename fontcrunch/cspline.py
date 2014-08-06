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

# fit arc to pts (0, 0), (x, y), and (1, 0), return th tangent to
# arc at (x, y)
def fit_arc(x, y):
    th = atan2(y - 2 * x * y, y * y + x - x * x)
    return th

# find thetas tangent to path using local cspline logic
def local_ths(path, closed):
    if closed:
        result = []
    else:
        result = [0]
    for i in range(1 - closed, len(path) - 1 + closed):
        x0, y0 = path[(i + len(path) - 1) % len(path)]
        x1, y1 = path[i]
        x2, y2 = path[(i + 1) % len(path)]
        dx = x2 - x0
        dy = y2 - y0
        ir2 = dx * dx + dy * dy
        x = ((x1 - x0) * dx + (y1 - y0) * dy) / ir2
        y = ((y1 - y0) * dx - (x1 - x0) * dy) / ir2
        th = fit_arc(x, y) + atan2(dy, dx)
        result.append(th)
    if not closed:
        result.append(0)
    boundary_ths(path, result, closed)
    return result

# set the endpoint thetas so endpoint curves are circular arcs
def boundary_ths(path, ths, closed):
    if not closed:
        first_th = 2 * atan2(path[1][1] - path[0][1], path[1][0] - path[0][0]) - ths[1]
        ths[0] = first_th
        last_th = 2 * atan2(path[-1][1] - path[-2][1], path[-1][0] - path[-2][0]) - ths[-2]
        ths[-1] = last_th

def draw_tan(x, y, th):
    dx = .2 * cos(th)
    dy = .2 * sin(th)
    print_pt(x - dx, y - dy, 'moveto')
    print_pt(x + dx, y + dy, 'lineto')
    print 'stroke'

def csinterp(t0, t1, u):
    if u == 0: return (0, 0)
    elif u == 1: return (1, 0)
    c = cos(u * pi * 0.5)
    s = sin(u * pi * 0.5)

    #sigmoid interpolant:
    tau = t0 * c * c + t1 * s * s

    #linear interpolant:
    #tau = t0 * (1 - u) + t1 * u + 1e-9

    f = sin(u * tau) / sin(tau)
    ph = (1 - u) * tau
    return (f * cos(ph), f * sin(ph))

def mod_2pi(th):
    u = th / (2 * pi)
    return 2 * pi * (u - floor(u + 0.5))

def print_pt(x, y, cmd):
    print 306 + 100 * x, 396 + 100 * y, cmd

def draw_cspline(path, ths):
    cmd = 'moveto'
    for i in range(len(path) - 1):
        x0, y0 = path[i]
        x1, y1 = path[i + 1]
        th = atan2(y1 - y0, x1 - x0)
        th0 = mod_2pi(ths[i] - th)
        th1 = mod_2pi(th - ths[i + 1])
        scale = hypot(y1 - y0, x1 - x0)
        rot = th
        cs = scale * cos(rot)
        ss = scale * sin(rot)
        for j in range(0, 100):
            t = j * .01
            c, s = csinterp(th0, th1, t)
            x = c * cs - s * ss
            y = s * cs + c * ss
            print_pt(x0 + x, y0 + y, cmd)
            cmd = 'lineto'
    print 'stroke'

print '%!PS-Adobe-3.0 EPSF'

print '-100 0 translate'
#path = [(-0.997535, 0.434403), (0.0156765, -0.0252084), (0.32168, 0.972144), (0.319054, 0.342386), (-0.0216322, -0.0717378)]
#path = [(-1, 0), (-.5, .05), (0, 0.1), (1, 1), (2, 0.1), (2.5, 0.05), (3,0)]
#path = [(-2, 0), (-1.5, 0), (-1, 0), (-.5, 0), (0, 0), (0.5, .5), (1, 0), (1.5, 0), (2, 0), (2.5, 0), (3, 0)]
closed = 0
if 0:
    cmd = 'moveto'
    for i in range(len(path)):
        x, y = path[i]
        print_pt(x, y, cmd)
        cmd = 'lineto'
    print 'stroke'


#ths[2] += .7

print '0 0 0 setrgbcolor'
print '2 setlinewidth'

print '/ss 3 def'
print '/ci { moveto ss 0 rmoveto currentpoint exch ss sub exch ss 0 360 arc fill } bind def'

def draw_cspline_fig(path):
    #print '1 1 translate'
    #print '0 0 .5 setrgbcolor'
    ths = local_ths(path, closed)
    print '1 setlinewidth'
    draw_cspline(path, ths)

    #print '3 3 translate'
    print '.5 setlinewidth'
    #print '1 0 0 setrgbcolor'
    for i in range(len(path)):
        x, y = path[i]
        print_pt(x, y, 'ci')
        #draw_tan(x, y, ths[i])

path = [(-1, .5), (0, 0), (.9, .9), (-.9, 2.6), (0, 3.5), (.9, 3)]
draw_cspline_fig(path)
path = [(1.2, .5), (2.2, 0), (3.1, .9), (2.2, 1.75), (1.3, 2.6), (2.2, 3.5), (3.1, 3)]
draw_cspline_fig(path)

print 'showpage'
