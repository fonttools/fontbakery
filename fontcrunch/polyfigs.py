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

def eps_prologue(x0, y0, x1, y1, draw_box = False):
    print '%!PS-Adobe-3.0 EPSF'
    print '%%BoundingBox:', x0, y0, x1, y1
    print '%%EndComments'
    print '%%EndProlog'
    print '%%Page: 1 1'
    if draw_box:
        print x0, y0, 'moveto', x0, y1, 'lineto', x1, y1, 'lineto', x1, y0, 'lineto closepath stroke'
    bigmat.prologue()

def eps_trailer():
    print '%%EOF'

if __name__ == '__main__':
    figure = sys.argv[1]
    if len(figure) > 4 and figure[-4:] == '.pdf': figure = figure[:-4]
    xo, yo, xscale, yscale = 36, 550, .25, 2000
    pl_nodes = True
    if figure == 'u':
        cr = 15
        w = 60
        w2 = 45
        w3 = 40
        h = 275
        h2 = h
        path = [(100, 500 - cr, '['), (100, h, ']'), (250, 100, 'o'),
                (400, h, '['), (400, 500 - cr, ']'),
                (400 - cr, 500, '['), (400 - w3 + cr, 500, ']'),
                (400 - w3, 500 - cr, '['), (400 - w3, h2, ']'), (250, 100 + w2, 'o'),
                (100 + w, h2, '['), (100 + w, 500 - cr, ']'),
                (100 + w - cr, 500, '['), (100 + cr, 500, ']')]
        eps_prologue(34, 95, 508, 750)
    elif figure in ('ecc0', 'ecc1', 'ecc2', 'ecc3', 'ecc4', 'ecc5'):
        xo, yo, xscale, yscale = 100, 550, .375, 3000
        if figure == 'ecc0':
            ecc, ty, ty1 = 0.56199, 'c', 'c'
        elif figure == 'ecc1':
            ecc, ty, ty1 = 0.49076, 'o', 'o',
        elif figure == 'ecc2':
            ecc, ty, ty1 = 0.42637, 'o', 'c'
        elif figure == 'ecc3':
            ecc, ty, ty1 = 0.56199, 'o', 'o',
        elif figure == 'ecc4':
            ecc, ty, ty1 = 0.56199, 'o', 'c'
        elif figure == 'ecc5':
            ecc, ty, ty1 = 0.62030, 'c', 'o'
        path = [(300 - 200 * ecc, 300, ty), (300, 100, ty1),
                (300 + 200 * ecc, 300, ty), (300, 500, ty1)]
        eps_prologue(95, 95, 508, 620)
    elif figure in ('ell0'):
        xo, yo, xscale, yscale = 100, 550, .375, 3000
        ecc = 0.56199
        n = 48
        path = []
        for i in range(n):
            th = 2 * pi * i / n
            path.append((300 + 200 * ecc * cos(th), 300 + 200 * sin(th), 'o'))
        pl_nodes = False
        eps_prologue(95, 95, 508, 620)

    bigmat.run_path(path, False, 10, xo, yo, xscale, yscale, pl_nodes = pl_nodes)
    eps_trailer()
