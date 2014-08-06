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
from math import *

import bigmat
import draw_cornu

def eps_prologue(x0, y0, x1, y1, draw_box = False):
    print '%!PS-Adobe-3.0 EPSF'
    print '%%BoundingBox:', x0, y0, x1, y1
    print '%%EndComments'
    print '%%EndProlog'
    print '%%Page: 1 1'
    if draw_box:
        print x0, y0, 'moveto', x0, y1, 'lineto', x1, y1, 'lineto', x1, y0, 'lineto closepath stroke'
    bigmat.prologue()
    print '/m { moveto } bind def'
    print '/l { lineto } bind def'
    print '/c { curveto } bind def'
    print '/z { closepath } bind def'

def eps_trailer():
    print '%%EOF'

def hobby_bz(th0, th1):
    cth0, sth0 = cos(th0), sin(th0)
    cth1, sth1 = cos(th1), sin(th1)
    a = sqrt(2)
    b = 1./16
    c = (3 - sqrt(5))/2
    alpha = a * (sth0 - b * sth1) * (sth1 - b * sth0) * (cth0 - cth1)
    rho = (2 + alpha) / (1 + (1 - c) * cth0 + c * cth1)
    sigma = (2 - alpha) / (1 + (1 - c) * cth1 + c * cth0)
    ch = 20
    x0, y0 = (-.5 * ch, 0)
    x1, y1 = x0 + ch * rho/3 * cth0, y0 + ch * rho/3 * sth0
    x3, y3 = (.5 * ch, 0)
    x2, y2 = x3 - ch * sigma/3 * cth1, y3 + ch * sigma/3 * sth1
    return [(x0, y0), (x1, y1), (x2, y2), (x3, y3)]

def do_hobby(figname):
    scale = 130
    eps_prologue(0, 90, 620, 700)
    print '0.5 setlinewidth'
    thlmin, thlmax = -2.2, 2.2
    thrmin, thrmax = -2.2, pi / 2 + .2
    print 306 + scale * thlmin, 396, 'moveto', 306 + scale * thlmax, 396, 'lineto stroke'
    print 306, 396 + scale * thrmin, 'moveto', 306, 396 + scale * thrmax, 'lineto stroke'

    print 'gsave [2] 0 setdash'
    print 306, 396 + scale * pi / 2, 'moveto'
    print 306 + scale * thlmax, 396 + scale * pi / 2, 'lineto stroke'
    print 306 + scale * thlmin, 396 - scale * pi / 2, 'moveto'
    print 306 + scale * thlmax, 396 - scale * pi / 2, 'lineto stroke'
    print 306 + scale * pi / 2, 396 + scale * thrmin, 'moveto'
    print 306 + scale * pi / 2, 396 + scale * thrmax, 'lineto stroke'
    print 'grestore'

    print 306 + 3, 396 + scale * thrmax - 10, 'moveto'
    print '/Symbol 12 selectfont (q) show'
    print 0, -2, 'rmoveto'
    print '/Times-Italic 9 selectfont (right) show'

    print 306 - 18, 396 + scale * pi / 2 - 4, 'moveto'
    print '/Symbol 12 selectfont (p/2) show'
    print 306 + scale * 2.2, 396 - scale * pi / 2 + 2, 'moveto'
    print '/Symbol 12 selectfont (-p/2) show'

    print 306 + scale * pi/2 + 2, 396 + scale * thrmax - 10, 'moveto'
    print '/Symbol 12 selectfont (p/2) show'

    print 306 + scale * 2.2, 396 + 6, 'moveto'
    print '/Symbol 12 selectfont (q) show'
    print 0, -2, 'rmoveto'
    print '/Times-Italic 9 selectfont (left) show'

    print '/ss 0.8 def'

    for i in range(-11, 12, 1):
        for j in range(-11, i + 1, 1):
            th0, th1 = i * .196, j * .196
            bz = hobby_bz(th0, th1)
            print 'gsave'
            print 306 + scale * th0, 396 + scale * th1, 'translate'
            if figname == 'hobby':
                print 'circle fill'
                draw_cornu.plot_bz(bz, (0, 0), 1, True)
                print 'stroke'
            elif figname == 'hobbyk':
                if True: #abs(i) < 10 and abs(j) < 10 and abs(i) + abs(j) < 10:
                    path = []
                    n = 32
                    for k in range(n + 1):
                        x, y = draw_cornu.bz_eval(bz, k * 1./n)
                        if k == 0:
                            cmd = '{'
                        elif k == n:
                            cmd = '}'
                        else:
                            cmd = 'o'
                        path.append((x, y, cmd))
                    bigmat.run_path(path, False, 10, 0, 0, .8, -50, False, False)
            print 'grestore'

if __name__ == '__main__':
    figname = sys.argv[1]
    if len(figname) > 4 and figname[-4:] == '.pdf': figname = figname[:-4]
    if figname in ('hobby', 'hobbyk'):
        do_hobby(figname)
