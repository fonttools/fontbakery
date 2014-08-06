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
import math
import elastica
import draw_cornu

def plot_odd(bzs, x0, y0, scale):
    frist = True
    for i in range(len(bzs) - 1, -1, -1):
        bzr = bzs[i][:]
        bzr.reverse()
        draw_cornu.plot_bz(bzr, (x0, y0), -scale, frist)
        frist = False
    for i in range(len(bzs)):
        draw_cornu.plot_bz(bzs[i], (x0, y0), scale, False)
    print 'stroke'

def draw_threecurves():
    draw_cornu.plot_prolog(306 - 160, 396 - 160, 306 + 220, 396 + 220, False)
    print '/Times-Roman 12 selectfont'

    # rectangular elastica
    xyk, cost = elastica.run_elastica(-5, 6, 0, 1, 0)
    x0, y0 = 8.5 * 36, 11 * 36
    sx = 100 * math.sqrt(.5)
    sy = sx
    elastica.plot(xyk, x0, y0, sx, sy)
    print x0, y0 + 1.98 * sy, 'moveto (rectangular elastica) show'
    print x0, y0 + 1.98 * sy - 14, 'moveto'
    print '/Symbol 12 selectfont (k) show'
    print '/Times-Roman 12 selectfont ( = x) show'

    # Euler spiral
    imax = 180
    ds2 = .1
    thresh = 1e-6
    s0 = 0
    scale = 100
    bzs = []
    for i in range(1, imax):
        s = math.sqrt(i * ds2)
        bz, score = draw_cornu.cornu_to_cubic(s0, s)
        if score > (s - s0) * thresh or i == imax - 1:
            # plot_bz(bz, (x0, y0), scale, s0 == 0)
            bzs.append(bz)
            s0 = s
    plot_odd(bzs, x0, y0, scale)
    print x0 - .2 * scale, y0 + 0.65 * scale, 'moveto (Euler spiral) show'
    print x0 - .2 * scale, y0 + 0.65 * scale - 14, 'moveto'
    print '/Symbol 12 selectfont (k) show'
    print '/Times-Roman 12 selectfont ( = s) show'

    # cubic parabola
    xmax = 1.5
    ymax = xmax ** 3 / 3.0
    bz = [(0, 0), (xmax / 3.0, 0), (xmax / 1.5, 0), (xmax, ymax)]
    plot_odd([bz], x0, y0, scale)
    print 'stroke'
    print x0 + 1.45 * scale, y0 + 0.9 * scale, 'moveto (cubic parabola) show'
    print x0 + 1.45 * scale, y0 + 0.9 * scale - 14, 'moveto'
    print "(y'' = x) show"

    print 'showpage'

if __name__ == '__main__':
    draw_threecurves()
