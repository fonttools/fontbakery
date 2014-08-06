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
# Figures for finite element model of elastica

import sys
from math import *

def prolog():
    print '%!PS-Adobe-3.0 EPSF'
    print '%%EndComments'
    print '%%EndProlog'
    print '%%Page: 1 1'
    print '/cshow {dup stringwidth exch -.5 mul exch rmoveto show} bind def'
    print '/circle { ss 0 moveto currentpoint exch ss sub exch ss 0 360 arc } bind def'

def eps_trailer():
    print '%%EOF'

def arrow(x0, y0, len, th, headlen = 5, headwid = 6):
    print 'gsave', x0, y0, 'translate', th, 'rotate'
    print 0, 0, 'moveto', len - .5 * headlen, 0, 'lineto stroke'
    print len, 0, 'moveto', -headlen, -.5 * headwid, 'rlineto', 0, headwid, 'rlineto fill'
    print 'grestore'

def strutfig():
    prolog()
    print '/Times-Roman 12 selectfont'
    print 3, 'setlinewidth'
    print 100, 100, 'moveto', 200, 0, 'rlineto stroke'
    print .75, 'setlinewidth'
    arrow(100, 100, 50, 180)
    arrow(300, 100, 50, 0)
    print 75, 105, 'moveto (T) cshow'
    print 325, 105, 'moveto (T) cshow'
    print 'showpage'
    eps_trailer()

def pivotfig():
    prolog()
    th = 20
    moment = 25
    print 3, 'setlinewidth'
    print 'gsave', 300, 100, 'translate', -.5 * th, 'rotate'
    print 0, 0, 'moveto', -150, 0, 'rlineto stroke'
    print .75, 'setlinewidth'
    print 0, 0, 'moveto', 50, 0, 'rlineto stroke'
    print 40, 0, 'moveto', 0, 0, 40, 0, th, 'arc stroke'
    arrow(-150, 0, moment, 270)
    print 'grestore'
    print 'gsave', 300, 100, 'translate', .5 * th, 'rotate'
    print 0, 0, 'moveto', 150, 0, 'rlineto stroke'
    print '/ss', 4, 'def circle fill'
    print .75, 'setlinewidth'
    arrow(150, 0, moment, 270)
    print 'grestore'
    print .75, 'setlinewidth'
    arrow(300, 100, 2 * moment * cos(.5 * th * pi / 180), 90)
    print '/Symbol 12 selectfont'
    print 345, 96, 'moveto (Dq) show'
    print '/Times-Roman 12 selectfont'
    print 155, 109, 'moveto (M) show'
    print 455, 112, 'moveto (M) show'
    print 303, 125, 'moveto (2M) show 1 0 rmoveto (cos) show'
    print '/Symbol 12 selectfont 1 0 rmoveto (\(Dq/2\)) show'
    print 'showpage'
    eps_trailer()

def chainfig():
    prolog()
    th0 = 25
    th1 = 30
    th2 = 35
    m = 1.5
    thrad = 35
    print 3, 'setlinewidth'
    print 'gsave', 300, 100, 'translate', -1 * th1, 'rotate'

    print 'gsave', -150, 0, 'translate', -1 * th0, 'rotate'
    print 0, 0, 'moveto', -100, 0, 'rlineto stroke'
    print .75, 'setlinewidth'
    print 0, 0, 'moveto', 50, 0, 'rlineto stroke'
    print thrad, 0, 'moveto', 0, 0, thrad, 0, th0, 'arc stroke'
    print '/ss', 4, 'def circle fill'
    print 'grestore'
    print 0, 0, 'moveto', -150, 0, 'rlineto stroke'
    print .75, 'setlinewidth'
    #print 0, 0, 'moveto', 50, 0, 'rlineto stroke'
    arrow(0, 0, 50, 0)
    arrow(0, 0, m * th0, 270)
    print thrad, 0, 'moveto', 0, 0, thrad, 0, th1, 'arc stroke'
    print 'grestore'
    print 'gsave', 300, 100, 'translate', 0, 'rotate'
    print 0, 0, 'moveto', 150, 0, 'rlineto stroke'
    print '/ss', 4, 'def circle fill'
    print .75, 'setlinewidth'
    arrow(0, 0, 50, 180)
    arrow(0, 0, m * th1 * 2 * cos(.5 * th1 * pi/180), 90 - .5 * th1)
    arrow(0, 0, m * th2, 270)
    print 150, 0, 'translate'
    print 0, 0, 'moveto', 50, 0, 'rlineto stroke'
    print thrad, 0, 'moveto', 0, 0, thrad, 0, th2, 'arc stroke'
    print 'grestore'
    print 'gsave', 450, 100, 'translate', 1 * th2, 'rotate'
    print 0, 0, 'moveto', 100, 0, 'rlineto stroke'
    print '/ss', 4, 'def circle fill'
    print 'grestore'

    print '/Symbol 12 selectfont'
    print 162 + thrad, 142, 'moveto (Dq) show'
    print '/Times-Roman 9 selectfont 0 -2 rmoveto (0) show'
    print '/Symbol 12 selectfont'
    print 302 + thrad, 85, 'moveto (Dq) show'
    print '/Times-Roman 9 selectfont 0 -2 rmoveto (1) show'
    print '/Symbol 12 selectfont'
    print 452 + thrad, 108, 'moveto (Dq) show'
    print '/Times-Roman 9 selectfont 0 -2 rmoveto (2) show'

    print '/Times-Roman 12 selectfont'
    print 233, 96, 'moveto (T) show'
    print '/Times-Roman 9 selectfont 0 -2 rmoveto (1) show'
    print '/Times-Roman 12 selectfont'
    print 345, 70, 'moveto (T) show'
    print '/Times-Roman 9 selectfont 0 -2 rmoveto (0) show'

    print '/Times-Roman 12 selectfont'
    print 286 - 10 * m, 92 - 23 * m, 'moveto (M) show'
    print '/Times-Roman 9 selectfont 0 -2 rmoveto (0) show'
    print '/Times-Roman 12 selectfont'
    print 296 + 14 * m, 102 + 58 * m, 'moveto (2M) show'
    print '/Times-Roman 9 selectfont 0 -2 rmoveto (1) show'
    print '/Times-Roman 12 selectfont 1 2 rmoveto (cos\() show'
    print '/Symbol 12 selectfont 1 0 rmoveto (Dq) show'
    print '/Times-Roman 9 selectfont 0 -2 rmoveto (1) show'
    print '/Times-Roman 12 selectfont 0 2 rmoveto (/2\)) show'
    print '/Times-Roman 12 selectfont'
    print 296, 92 - 36 * m, 'moveto (M) show'
    print '/Times-Roman 9 selectfont 0 -2 rmoveto (2) show'

    print '/Times-Roman 12 selectfont'
    print 240, 140, 'moveto (0) show'
    print 375, 105, 'moveto (1) show'
    print 495, 140, 'moveto (2) show'

    print 'showpage'
    eps_trailer()

if __name__ == '__main__':
    figname = sys.argv[1]
    if len(figname) > 4 and figname[-4:] == '.pdf': figname = figname[:-4]
    if figname == 'strutfig':
        strutfig()
    elif figname == 'pivotfig':
        pivotfig()
    elif figname == 'chainfig':
        chainfig()

