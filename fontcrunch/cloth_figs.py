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
import pcorn

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

def clothoid_map(figname):
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
            seg = pcorn.Segment([-10, 0], [10, 0], -th0, -th1)
            curve = pcorn.Curve([seg])
            print 'gsave'
            print 306 + scale * th0, 396 + scale * th1, 'translate'
            if figname == 'clothmap':
                print 'circle fill'
                bzs = draw_cornu.pcorn_segment_to_bzs(curve, 0, curve.arclen - 1e-6, 0, 1e-6)
                for k in range(len(bzs)):
                    draw_cornu.plot_bz(bzs[k], (0, 0), 1, k == 0)
                print 'stroke'
            print 'grestore'


if __name__ == '__main__':
    clothoid_map('clothmap')
