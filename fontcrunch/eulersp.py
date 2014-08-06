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
#
# Recreation of Fig. 17 from Euler's Additamentum

import sys
import common
from math import *
import draw_cornu
import pcorn
import cornu
import elastfe
import elastica

def fig17():
    t_m = .28
    t_B = .85
    Ax = 280
    Bx = 400
    Ay = 300
    Py = Ay - 60
    r = 12

    th_a = -t_B * t_B
    By = Ay
    My = Ay
    Mx = Ax + t_m * (Bx - Ax) / t_B

    y, x = cornu.eval_cornu(t_B)
    ax = Bx - (Bx - Ax) * (x * cos(th_a) - y * sin(th_a)) / t_B
    ay = By - (Bx - Ax) * (y * cos(th_a) + x * sin(th_a)) / t_B
    chth = atan2(By - ay, Bx - ax)
    if 0:
	print 'gsave 1 0 0 setrgbcolor'
	print Bx, By, 'moveto'
	print 10 * cos(chth), 10 * sin(chth), 'rlineto stroke'
	print ax, ay, 'moveto'
	print 10 * cos(th_a), 10 * sin(th_a), 'rlineto stroke'
	print 'grestore'

    draw_cornu.plot_prolog(120, 210, 470, 420)
    print '/cshow {dup stringwidth exch -.5 mul exch rmoveto show} bind def'
    print Ax, Ay, 'm'
    print Bx, By, 'l stroke'
    seg = pcorn.Segment([ax, ay], [Bx, By], -th_a + chth, -chth)
    curve = pcorn.Curve([seg])
    bzs = draw_cornu.pcorn_segment_to_bzs(curve, 0, (Bx - Ax - 1e-5), 0, 1e-6)
    for k in range(len(bzs)):
	draw_cornu.plot_bz(bzs[k], (0, 0), 1, k == 0)
    print 'stroke'
    print 'gsave'
    print '.4 setlinewidth'
    print ax, ay, 'translate'
    print (Bx - Ax) / (250. * t_B), 'dup scale'
    print th_a * 180 / pi, 'rotate'
    print -306, -396, 'translate'
    draw_cornu.test_draw_cornu(200, False, True)
    print 'grestore'

    print '/Times-Roman 12 selectfont'
    print Ax, Ay + 3, 'm (A) cshow'
    print Mx, My - 11, 'm (M) cshow'
    print Bx, By - 11, 'm (B) cshow'

    # the weight
    print Ax, Ay, 'moveto'
    print Ax, Py + r, 'lineto stroke'
    print Ax, Py - 4, 'm (P) cshow'
    print Ax + r, Py, 'moveto', Ax, Py, r, '0 360 arc stroke'

    print '/Times-Italic 12 selectfont'
    print ax - 4, ay - 6, 'm (a) cshow'
    y, x = cornu.eval_cornu(t_m)
    mx = ax + (Bx - Ax) * (x * cos(th_a) - y * sin(th_a)) / t_B
    my = ay + (Bx - Ax) * (y * cos(th_a) + x * sin(th_a)) / t_B
    print 'gsave'
    print mx, my, 'translate'
    th_m = th_a + t_m * t_m
    print th_m * 180 / pi, 'rotate'
    print '0 -2 moveto 0 2 lineto stroke grestore'
    print mx + 8, my + 2, 'm (m) cshow'

    print 'showpage'

def euler_elastic():
    t_m = .5
    t_B = 1.2
    Ax = 200
    Bx = 500
    Ay = 300
    Py = Ay - 60
    r = 12

    th_a = -t_B * t_B
    By = Ay
    My = Ay
    Mx = Ax + t_m * (Bx - Ax) / t_B

    y, x = cornu.eval_cornu(t_B)
    ax = Bx - (Bx - Ax) * (x * cos(th_a) - y * sin(th_a)) / t_B
    ay = By - (Bx - Ax) * (y * cos(th_a) + x * sin(th_a)) / t_B
    chth = atan2(By - ay, Bx - ax)

    draw_cornu.plot_prolog(190, 195, 530, 530)
    print '/cshow {dup stringwidth exch -.5 mul exch rmoveto show} bind def'
    print Ax, Ay, 'm'
    print Bx, By, 'l stroke'
    seg = pcorn.Segment([ax, ay], [Bx, By], -th_a + chth, -chth)
    curve = pcorn.Curve([seg])
    bzs = draw_cornu.pcorn_segment_to_bzs(curve, 0, (Bx - Ax - 1e-5), 0, 1e-6)
    for k in range(len(bzs)):
	draw_cornu.plot_bz(bzs[k], (0, 0), 1, k == 0)
    print 'stroke'

    print 'gsave [2] 0 setdash'
    print ax, ay, 'm', Ax, Ay, 'l stroke'
    y, x = cornu.eval_cornu(t_m)
    mx = ax + (Bx - Ax) * (x * cos(th_a) - y * sin(th_a)) / t_B
    my = ay + (Bx - Ax) * (y * cos(th_a) + x * sin(th_a)) / t_B
    print Mx, My, 'm', mx, my, 'l stroke'
    print 'grestore'

    print '/Symbol 12 selectfont'
    print mx + 4, my - 4, 'm (k) show'
    print '/Times-Roman 12 selectfont'
    print '( = cs) show'


    # the weight
    elastfe.arrow(Ax, Ay, Ay - Py, 270)
    print Ax + 4, Py + 12, 'm (F) show'

    # hatching (the wall)
    print 'gsave'
    print Bx, By - 100, 'm', Bx, By + 140, 'l stroke'
    print 'gsave', Bx, By - 100, 'moveto', Bx + 20, By - 100, 'lineto'
    print Bx + 20, By + 140, 'lineto', Bx, By + 140, 'lineto clip newpath'
    for y in range(By - 100, By + 160, 12):
	print Bx, y, 'moveto', 20, -20, 'rlineto stroke'
    print 'grestore'

    print Mx, My, 'm', 0, -6, 'rlineto stroke'
    print 'gsave [1 3] 0 setdash'
    print Ax, My - 4, 'm', Mx, My - 4, 'l stroke'
    print 'grestore'

    print (ax + mx) * .5 + 2, (ay + my) * .5 - 6, 'm (s) show'

    print (Ax + Mx) * .5, Ay - 12, 'm (s) cshow'
    elastica.moment_arrow(Mx, My, 10, -60, 240)
    print Mx, My - 22, 'm (M = Fs) cshow'

    print 'showpage'

def lerp(z0, z1, t):
    return (z0[0] + t * (z1[0] - z0[0]), z0[1] + t * (z1[1] - z0[1]))

# This figure isn't strictly related to Euler spirals, as I ended up using
# Beziers as the primitive.
def two_continue():
    z0 = 100, 200
    z1 = 200, 220
    z2 = 300, 300
    z3 = 400, z0[1]

    draw_cornu.plot_prolog(95, 155, 445, 255)

    t = 1.1
#    print z0[0], z0[1], 'moveto', z1[0], z1[1], z2[0], z2[1], z3[0], z3[1], 'curveto stroke'
#    print '1 0 0 setrgbcolor'

    z01 = lerp(z0, z1, t)
    z12 = lerp(z1, z2, t)
    z23 = lerp(z2, z3, t)
    z012 = lerp(z01, z12, t)
    z123 = lerp(z12, z23, t)
    z0123 = lerp(z012, z123, t)
    print z0[0], z0[1], 'moveto', z01[0], z01[1], z012[0], z012[1], z0123[0], z0123[1], 'curveto stroke'
    print z0[0], z0[1], 'moveto', z3[0], z3[1], 'lineto stroke'
    print z0[0], z0[1], 'moveto', z0123[0], z0123[1], 'lineto stroke'

    print '/Symbol 12 selectfont'
    print 150, 204, 'moveto (q) show'
    print '/Times-Roman 8 selectfont 0 -2 rmoveto (0) show'

    print '/Symbol 12 selectfont'
    print 375, 204, 'moveto (q) show'
    print '/Times-Roman 8 selectfont 0 -2 rmoveto (1) show'

    #print '/Symbol 12 selectfont'
    #print 417, 184, 'moveto (D) show'
    #print '/Times-Roman 12 selectfont (s) show'

    print '/Times-Roman 12 selectfont'
    print z0[0] - 3, z0[1] + 5, 'moveto (s) show'
    print '/Times-Roman 8 selectfont 0 -2 rmoveto (0) show'

    print '/Times-Roman 12 selectfont'
    print z3[0], z3[1] + 4, 'moveto (s) show'
    print '/Times-Roman 8 selectfont 0 -2 rmoveto (1) show'

    print '/Times-Roman 12 selectfont'
    print z0123[0] + 2, z0123[1], 'moveto (s) show'
    print '/Times-Roman 8 selectfont 0 -2 rmoveto (2) show'

    print '/Symbol 12 selectfont'
    print z3[0], z3[1] + 30, 'moveto (k, k\242, k\242\242) show'

    elastfe.arrow(z3[0] - 2, z3[1] + 27, 17, 240)

    print 'showpage'

# This figure isn't strictly related to Euler spirals, as I ended up using
# Beziers as the primitive.
def twoparam():
    z0 = 100, 200
    z1 = 200, 250
    z2 = 300, 300
    z3 = 400, z0[1]

    draw_cornu.plot_prolog(95, 155, 445, 255)
    common.setlinewidth(3)

    print z0[0], z0[1], 'moveto', z1[0], z1[1], z2[0], z2[1], z3[0], z3[1], 'curveto stroke'
    common.setlinewidth(2)
    print z0[0], z0[1], 'moveto', z1[0], z1[1], 'lineto stroke'
    z23 = lerp(z2, z3, .5)
    print z23[0], z23[1], 'moveto', z3[0], z3[1], 'lineto stroke'
    print z0[0], z0[1], 'moveto', z3[0], z3[1], 'lineto stroke'

    print '/Symbol 18 selectfont'
    print 140, 205, 'moveto (q) show'
    print '/Times-Roman 12 selectfont 0 -2 rmoveto (0) show'

    print '/Symbol 18 selectfont'
    print 365, 205, 'moveto (q) show'
    print '/Times-Roman 12 selectfont 0 -2 rmoveto (1) show'

    print 'showpage'

if __name__ == '__main__':
    figname, args, flags = common.parse_cmdline()
    if figname == 'watchspring':
	fig17()
    elif figname == 'euler_elastic':
	euler_elastic()
    elif figname == 'two_continue':
	two_continue()
    elif figname == 'twoparam':
	twoparam()
