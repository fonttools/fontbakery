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
import pcorn

# One step of 4th-order Runge-Kutta numerical integration - update y in place
def rk4(y, dydx, x, h, derivs):
    hh = h * .5
    h6 = h * (1./6)
    xh = x + hh
    yt = []
    for i in range(len(y)):
	yt.append(y[i] + hh * dydx[i])
    dyt = derivs(xh, yt)
    for i in range(len(y)):
	yt[i] = y[i] + hh * dyt[i]
    dym = derivs(xh, yt)
    for i in range(len(y)):
	yt[i] = y[i] + h * dym[i]
	dym[i] += dyt[i]
    dyt = derivs(x + h, yt)
    for i in range(len(y)):
	y[i] += h6 * (dydx[i] + dyt[i] + 2 * dym[i])

def run_elastica_half(sp, k0, lam1, lam2):
    def mec_derivs(x, ys):
	th, k = ys[2], ys[3]
	dx, dy = cos(th), sin(th)
	return [dx, dy, k, lam1 * dx + lam2 * dy, k * k]
    ys = [0, 0, 0, k0, 0]
    xyk = [(ys[0], ys[1], ys[3])]
    n = max(1, int(sp * 10)) # note: * 50 improves mec_euler_compare accuracy
    h = float(sp) / n
    s = 0
    for i in range(n):
	dydx = mec_derivs(s, ys)
	rk4(ys, dydx, s, h, mec_derivs)
	xyk.append((ys[0], ys[1], ys[3]))
    return xyk, ys[2], ys[4]

def run_elastica(sm, sp, k0, lam1, lam2):
    xykm, thm, costm = run_elastica_half(-sm, k0, -lam1, lam2)
    xykp, thp, costp = run_elastica_half(sp, k0, lam1, lam2)
    xyk = []
    for i in range(1, len(xykm)):
	x, y, k = xykm[i]
	xyk.append((-x, y, k))
    xyk.reverse()
    xyk.extend(xykp)
    cost = costm + costp
    return xyk, cost

def compute_elastica(sm, sp, k0, lam):
    def mec_derivs(x, ys):
	th, k = ys[2], ys[3]
	dx, dy = cos(th), sin(th)
	return [dx, dy, k, -lam * dy, k * k]
    ys = [0, 0, 0, k0, 0]
    dt = .01
    np = int(sp / dt)
    k = k0
    x, y = 0, 0
    th = 0
    p = [(0, 0, 0)]
    for i in range(np):
	dkds = -lam * sin(th)
	km = k + .5 * dt * dkds
	thm = th + .5 * dt * km
	x += dt * cos(th)
	y += dt * sin(th)

	k += dt * dkds
	th += dt * km
	p.append((x, y, k))

    nm = int(-sm / dt)
    k = k0
    x, y = 0, 0
    th = 0
    m = []
    for i in range(nm):
	dkds = -lam * sin(th)
	km = k - .5 * dt * dkds
	thm = th - .5 * dt * km
	x -= dt * cos(th)
	y -= dt * sin(th)

	k -= dt * dkds
	th -= dt * km
	m.append((x, y, k))
    m.reverse()
    m.extend(p)
    return m

def plot(xys, x0, y0, sx, sy):
    cmd = 'moveto'
    for i in range(len(xys)):
	xy = xys[i]
	print x0 + xy[0] * sx, y0 + xy[1] * sy, cmd
	cmd = 'lineto'
    print 'stroke'

def eps_prologue(x0, y0, x1, y1, draw_box = False):
    print '%!PS-Adobe-3.0 EPSF'
    print '%%BoundingBox:', x0, y0, x1, y1
    print '%%EndComments'
    print '%%EndProlog'
    print '%%Page: 1 1'
    if draw_box:
        print x0, y0, 'moveto', x0, y1, 'lineto', x1, y1, 'lineto', x1, y0, 'lineto closepath stroke'

def eps_trailer():
    print '%%EOF'

def moment_arrow(x0, y0, r, th0, th1):
    wid = 2
    len = min(3, r * (th1 - th0) * .005)
    print x0 + r * cos(th0 * pi / 180), y0 + r * sin(th0 * pi / 180), 'moveto'
    print x0, y0, r, th0, th1, 'arc'
    print 'stroke'
    print 'gsave'
    print x0 + r * cos(th0 * pi / 180), y0 + r * sin(th0 * pi / 180), 'translate'
    print th0 - 90, 'rotate'
    print -len, -wid, 'moveto 0 0 lineto', -len, wid, 'lineto stroke'
    print 'grestore'
    print 'gsave'
    print x0 + r * cos(th1 * pi / 180), y0 + r * sin(th1 * pi / 180), 'translate'
    print th1 + 90, 'rotate'
    print -len, -wid, 'moveto 0 0 lineto', -len, wid, 'lineto stroke'
    print 'grestore'

def draw_moment():
    import elastfe
    print '%!PS-Adobe-3.0 EPSF'
    s = 3.12676
    xyk, cost = run_elastica(-s, s, 1, 0, -.4)
    print '% k = ', xyk[0][2]
    x0, y0 = 300, 500
    sx = -100
    sy = -100
    f = 50
    plot(xyk, x0, y0, sx, sy)
    print 'gsave 2 setlinewidth'
    xl = x0 + xyk[-1][0] * sx
    yl = y0 + xyk[-1][1] * sy
    elastfe.arrow(xl - f, yl, f, 0)
    xr = x0 + xyk[0][0] * sx
    yr = y0 + xyk[0][1] * sy
    elastfe.arrow(xr + f, yr, f, 180)
    print 'grestore'
    print '/Times-Bold 12 selectfont'
    print xl - 30, yl + 4, 'moveto (F) show'
    print xr + 25, yl + 4, 'moveto (F) show'
    print '.75 setlinewidth'
    print x0, yl, 'moveto', 0, 300, 'rlineto stroke'
    print xl, yl, 'moveto', xr, yr, 'lineto stroke'
    print '/Times-Italic 12 selectfont'
    if 0:
	print x0 + 4, yl + 290, 'moveto (y) show'
	print xr - 10, yl - 8, 'moveto (x) show'
    xs = x0 + xyk[26][0] * sx
    ys = y0 + xyk[26][1] * sy
    print 'gsave [2] 0 setdash'
    print xs, yl, 'moveto', xs, ys, 'lineto stroke'
    print 'grestore'
    print xs - 8, (yl + ys) * .5, 'moveto (y) show'
    moment_arrow(xs, ys, 10, -70, 200)
    print xs + 12, ys + 2, 'moveto'
    #print '/Times-Bold 12 selectfont (M) show'
    print '/Times-Roman 12 selectfont (M = F) show'
    #print '/Times-Bold 12 selectfont (F) show'
    print '/Times-Italic 12 selectfont (y) show'
    print 'showpage'

def draw_moment_bernoul():
    import elastfe
    print '%!PS-Adobe-3.0 EPSF'
    s = 2.63
    xyk, cost = run_elastica(0, s, 1, 0, -.5)
    xyk = [(-y, -x, k) for x, y, k in xyk]
    print '% k = ', xyk[0][2]
    x0, y0 = 300, 500
    sx = -100
    sy = -100
    f = 30
    plot(xyk, x0, y0, sx, sy)
    print 'gsave 2 setlinewidth'
    xl = x0 + xyk[-1][0] * sx
    yl = y0 + xyk[-1][1] * sy
    elastfe.arrow(xl, yl + f, f, 270)
    xr = x0 + xyk[0][0] * sx
    yr = y0 + xyk[0][1] * sy
    #elastfe.arrow(xr + f, yr, f, 180)
    print 'grestore'
    print '/Times-Bold 12 selectfont'
    print xl + 4, yl + 25, 'moveto (F) show'
    print '.75 setlinewidth'
    print xl, yl, 'moveto', xl, y0, 'lineto stroke'
    print x0 - 20, y0, 'moveto', xl + 20, y0, 'lineto stroke'
    #hatching
    print 'gsave', x0 - 20, y0, 'moveto', xl + 20, y0, 'lineto'
    print xl + 20, y0 - 15, 'lineto', x0 - 20, y0 - 15, 'lineto clip'
    for x in range(x0 - 20, int(xl + 50), 8):
	print x, y0, 'moveto', -20, -20, 'rlineto stroke'
    print 'grestore'
    x1 = x0 + xyk[2][0] * sx
    y1 = y0 + xyk[2][1] * sy
    print x1, y1, 'moveto', x0 + 10, y1, 'lineto', x0 + 10, y0, 'lineto stroke'
    print '/Times-Italic 12 selectfont'
    xs = x0 + xyk[10][0] * sx
    ys = y0 + xyk[10][1] * sy
    print 'gsave [2] 0 setdash'
    print xl, ys, 'moveto', xs, ys, 'lineto stroke'
    print 'grestore'
    print (xl + xs) * .5 , ys + 4, 'moveto (x) show'
    moment_arrow(xs, ys, 10, 20, 250)
    print xs - 20, ys + 16, 'moveto'
    #print '/Times-Bold 12 selectfont (M) show'
    print '/Times-Roman 12 selectfont (M = F) show'
    #print '/Times-Bold 12 selectfont (F) show'
    print '/Times-Italic 12 selectfont (x) show'
    print 'showpage'

def draw_rectel():
    import elastfe
    print '%!PS-Adobe-3.0 EPSF'
    s = 2.63
    xyk, cost = run_elastica(-3 * s, s, 1, 0, -.5)
    print '% k = ', xyk[0][2]
    x0, y0 = 300, 500
    sx = -50
    sy = -50
    f = 50
    plot(xyk, x0, y0, sx, sy)
    print 'gsave 2 setlinewidth'
    xl = x0 + xyk[-1][0] * sx
    yl = y0 + xyk[-1][1] * sy
    elastfe.arrow(xl - f, yl, f, 0)
    xr = x0 + xyk[0][0] * sx
    yr = y0 + xyk[0][1] * sy
    elastfe.arrow(xr + f, yr, f, 180)
    print 'grestore'
    print '/Times-Bold 12 selectfont'
    print xl - 30, yl + 4, 'moveto (F) show'
    print xr + 25, yl + 4, 'moveto (F) show'
    print '.75 setlinewidth'
    print 'showpage'



def run_elastica_half_th(sp, k0, lam1, lam2, n = 10):
    def mec_derivs(x, ys):
	th, k = ys[2], ys[3]
	dx, dy = cos(th), sin(th)
	return [dx, dy, k, lam1 * dx + lam2 * dy, k * k]
    ys = [0, 0, 0, k0, 0]
    xytk = [ys[:4]]
    h = float(sp) / n
    s = 0
    for i in range(n):
	dydx = mec_derivs(s, ys)
	rk4(ys, dydx, s, h, mec_derivs)
	xytk.append(ys[:4])
    return xytk

def draw_chain():
    print '%!PS-Adobe-3.0 EPSF'
    print '100 400 translate'
    print '-70 rotate'
    print '/ss 2 def'
    print '/circle { ss 0 moveto currentpoint exch ss sub exch ss 0 360 arc } bind def'
    xytks = run_elastica_half_th(4, 1, 0, -.5, 10)
    x0, y0 = 0, 0
    sc = 100
    th0 = -90
    plot(xytks, x0, y0, sc, sc)
    for i in range(len(xytks)):
	xy = xytks[i]
	print 'gsave', x0 + sc * xy[0], y0 + sc * xy[1], 'translate circle fill'
	print 180 * xy[2] / pi, 'rotate'
	if i > 0 and i < len(xytks) - 1:
	    if (xy[3] > 0):
		moment_arrow(0, 0, 12, th0 - 60 * xy[3], th0 + 60 * xy[3])
	    else:
		moment_arrow(0, 0, 12, -th0 + 60 * xy[3], -th0 - 60 * xy[3])
	print 'grestore'
    print 'showpage'

def draw_bernoulli91(Eix = 45):
    print '%!PS-Adobe-3.0 EPSF'
    xytk = run_elastica_half_th(2.63, 1, 0, -.5, 100)
    scale = 100
    fontsize = 21
    D = (200, 300)
    print '2.5 setlinewidth'
    cmd = 'moveto'
    for i in range(len(xytk)):
	xy = xytk[i]
	print D[0] + xy[1] * scale, D[1] + xy[0] * scale, cmd
	if i == Eix: E = (D[0] + xy[1] * scale, D[1] + xy[0] * scale)
	cmd = 'lineto'
    print 'stroke'
    A = (D[0] + xytk[-1][1] * scale, D[1] + xytk[-1][0] * scale)
    AC = A[0] - D[0]
    # The evolute
    cmd = 'moveto'
    for i in range(len(xytk)):
	xy = xytk[i]
	r = 1 / xy[3]
	x = xy[1] + r * cos(xy[2])
	y = xy[0] - r * sin(xy[2])
	print D[0] + x * scale, D[1] + y * scale, cmd
	if i == 0: G = (D[0] + x * scale, D[1] + y * scale)
	if i == Eix: L = (D[0] + x * scale, D[1] + y * scale)
	cmd = 'lineto'
	if y < -2:
	    M = (D[0] + x * scale, D[1] + y * scale)
	    break
    print 'stroke'
    print '1.5 setlinewidth'
    print 'gsave [4] 0 setdash'
    print L[0], L[1], 'moveto', E[0], E[1], 'lineto'
    print A[0], E[1], 'lineto stroke'
    print '[6] 0 setdash'
    print D[0], D[1], 'moveto', D[0], A[1], 'lineto stroke'
    print 'grestore'

    # axes and other guide lines
    N = (A[0], D[1] - 2 * scale)
    B = (A[0], A[1] + AC)
    print N[0], N[1], 'moveto', B[0], B[1], 'lineto stroke'
    print D[0], D[1], 'moveto', A[0], D[1], 'lineto stroke' # DH
    print L[0], L[1], 'moveto', A[0], L[1], 'lineto stroke' # LI
    print A[0], A[1], 'moveto', D[0], A[1], 'lineto stroke' # AC
    print B[0], B[1], 'moveto', A[0], A[1], AC, 90, 180, 'arc stroke'
    Q = (.5 * (G[0] + A[0]), D[1] + .5 * (A[0] - G[0]))
    print A[0], D[1], 'moveto'
    print Q[0], D[1], Q[1] - D[1], 0, 180, 'arc stroke'
    print G[0], G[1], 'moveto', Q[0], Q[1], 'lineto'
    print A[0], D[1], 'lineto stroke'

    # labels
    print '/Times-Roman', fontsize, 'selectfont'
    print A[0] + 3, A[1], 'moveto (A) show'
    print B[0] - .9 * fontsize, B[1] - .8 * fontsize, 'moveto (B) show'
    print D[0] - .9 * fontsize, A[1] - fontsize / 3, 'moveto (C) show'
    print D[0] - .9 * fontsize, D[1] - fontsize / 3, 'moveto (D) show'
    print E[0] - .6 * fontsize, E[1] + 1, 'moveto (E) show'
    print A[0] + 3, E[1] - 2, 'moveto (F) show'
    print G[0] - .9 * fontsize, G[1] + 2, 'moveto (G) show'
    print A[0] + 3, G[1], 'moveto (H) show'
    print A[0] + 3, L[1] - fontsize / 3, 'moveto (I) show'
    print L[0] - .7 * fontsize, L[1] - fontsize / 3, 'moveto (L) show'
    print M[0] - 1.2 * fontsize, M[1] + 12, 'moveto (M) show'
    print N[0] + 3, N[1], 'moveto (N) show'
    print Q[0] - .4 * fontsize, Q[1] + 5, 'moveto (Q) show'
    print 'showpage'

def find_antisym_elastica(target, a, plot_iters = False):
    l = 0
    r = .4
    for j in range(20):
	sc = 0.5 * (l + r)
	xyk, th, cost = run_elastica_half(5, 0, sc * cos(a), sc * sin(a))
	chth = atan2(xyk[-1][1], xyk[-1][0])
	chord = hypot(xyk[-1][1], xyk[-1][0])
	th1 = th - chth
	if th1 > target: r = sc
	else: l = sc
	if plot_iters:
	    print 'gsave', i * 5, j * 50, 'translate'
	    print '0 0 moveto (%.4g %.4g) show' % (cost, cost * chord)
	    print 'gsave .5 .5 1 setrgbcolor 20 10 moveto', 50 * sc * cos(a), 50 * sc * sin(a), 'rlineto stroke grestore'
	    plot(xyk, 20, 10, 4, 4)
	    print 'grestore'
    return chord, chth, cost, sc

def run_simec():
    print '%!PS-Adobe-3.0 EPSF'
    print '/Times-Roman 12 selectfont'
    simec = []
    mec = []
    target = pi / 2
    simin = 580
    if target == 1: simin = 420
    step = 1
    for i in range(0, 1000, step):
	ia = i
	if (i < 20): ia = 20 + .65 * (ia - 20)
	a = (ia - 100) * .001480256614
	chord, chth, cost, sc = find_antisym_elastica(target, a)
	x = (chord - 2.8) * 400
	if target == 1:
	    x = (chord - 4.4) * 2500
	simec.append((x, cost))
	mec.append((x, cost * chord))
	print '% th', i, a - chth
	if i in (0, 20, 100, 280, simin, 830, 999):
	    print 'gsave', x, 130, 'translate'
	    print -180 * chth / pi, 'rotate'
	    xyk, cost = run_elastica(-5, 5, 0, sc * cos(a), sc * sin(a))
	    plot(xyk, 0, 0, 4, 4)
	    print 'gsave'
	    print '[2] 0 setdash 0.75 setlinewidth'
	    s = 12
	    if i == 580: s = 10
	    elif i == 830: s = 13
	    xyk, cost = run_elastica(-s, s, 0, sc * cos(a), sc * sin(a))
	    plot(xyk, 0, 0, 4, 4)
	    print 'grestore .5 setlinewidth'
	    print 180 * a / pi, 'rotate'
	    print 0, -70 * sc, 'moveto', 0, 70 * sc, 'lineto stroke'
	    print 'grestore'

    plot(mec, 0, 200 - 200 * min([xy[1] for xy in mec]), 1, 200)
    plot(simec, 0, 200 - 600 * min([xy[1] for xy in simec]), 1, 600)

    # axes
    print mec[0][0], 170, 'moveto', mec[-1][0], 170, 'lineto stroke'
    print 480, 158, 'moveto (chord length) show'
    for i in range(6):
	print mec[0][0] + (i / 5.) * (mec[-1][0] - mec[0][0]), 170, 'moveto'
	print '0 -5 rlineto stroke'
    print mec[0][0], 170, 'moveto', 0, 300, 'rlineto stroke'
    for i in range(1, 6):
	print mec[0][0], 170 + (i / 5.) * 300, 'moveto', 5, 0, 'rlineto stroke'

    print '[2] 0 setdash'
    if len(mec) == 1000 / step:
	print mec[100 / step][0], 150, 'moveto 0 50 rlineto stroke'
	print simec[simin / step][0], 150, 'moveto 0 50 rlineto stroke'

    print mec[0][0] + 8, 466, 'moveto (energy (relative units)) show'
    print '120 232 moveto (MEC energy) show'
    print '200 336 moveto (SIMEC energy) show'
    print 'showpage'

def draw_pendulum():
    print '%!PS-Adobe-3.0 EPSF'
    print '/Times-Roman 12 selectfont'
    print '/circ { /ss exch def ss 0 moveto currentpoint exch ss sub exch ss 0 360 arc } bind def'
    print '/cshow {dup stringwidth exch -.5 mul exch rmoveto show} bind def'
    x0, y0 = 300, 300
    plen = 250
    flen = 60
    weightrad = 12
    th = .5
    print 'gsave', x0, y0, 'translate',
    print 3, 'circ stroke'
    print 0, -3, 'moveto', 0, -40, 'rlineto stroke'
    print -30 * sin(th), -30 * cos(th), 'moveto', 0, 0, 30, 270 - th * 180/pi, 270, 'arc stroke'
    print 'gsave /Symbol 12 selectfont'
    print -45 * sin(.5 * th), -45 * cos(.5 * th), 'moveto (q) cshow grestore'
    print -th * 180 / pi, 'rotate'
    print 3, -26, 'moveto', -3, -4, 'rlineto', 3, -4, 'rlineto stroke'
    print 0, -3, 'moveto', 0, 3-plen, 'rlineto stroke'
    print 6, -plen / 2, 'moveto gsave', th*180/pi, 'rotate (r) show grestore'
    print 'gsave', 0, -plen, 'translate', weightrad, 'circ fill'
    print th * 180 / pi, 'rotate'
    print 0, weightrad, 'moveto', 0, flen, 'rlineto stroke'
    print -5, 6 + weightrad, 'moveto 5 -6 rlineto 5 6 rlineto stroke'
    print 0, weightrad + flen + 3, 'moveto (F = mg) cshow'
    print 'gsave', -th * 180/pi, 'rotate'
    print -weightrad, 0, 'moveto', -flen * sin(th), 0, 'rlineto stroke'
    print -weightrad - 6, -5, 'moveto 6 5 rlineto -6 5 rlineto stroke'
    print -weightrad - flen * sin(th), 0, 'translate'
    print th * 180/pi, 'rotate', -45, 5, 'moveto'
    print '(F) show'
    print '/Times-Roman 9 selectfont 0 -2 rmoveto (net) show 0 2 rmoveto'
    print '/Times-Roman 12 selectfont ( = mg sin ) show'
    print '/Symbol 12 selectfont (q) show'
    print 'grestore'
    print 'grestore'
    print '[4] 0 setdash'
    print 0, -plen, 'moveto', 0, 0, plen, 270, 270 + 2 * th * 180/pi, 'arc stroke'
    print 2 * th * 180/pi, 'rotate'
    print 0, -3, 'moveto', 0, 3-plen + weightrad, 'rlineto stroke'
    print 'gsave', 0, -plen, 'translate', weightrad, 'circ stroke'
    print 'grestore'

def draw_pendulum_example(lam = 0.5):
    print -160, 35, 'moveto'
    print '/Symbol 12 selectfont (l) show'
    print '/Times-Roman 12 selectfont ( = %g) show' % lam

    plen = 50

    # scale
    x0 = -80
    h = 4
    if lam < .25: h = 5
    print x0, -plen, 'moveto', 0, .5 * h * plen, 'rlineto stroke'
    for i in range(h + 1):
	print x0, plen * .5 * (i - 2), 'moveto -4 0 rlineto stroke'
	print x0 - 12, plen * .5 * (i - 2) - 4, 'moveto (%d) show' % i
    print x0 + 4, plen * .5 * (h - 2) - 15, 'moveto (1/) show'
    print '/Symbol 12 selectfont (l) show'
    print x0, plen * (-1 + .5/lam), 'moveto 10 0 rlineto stroke'
    print '[1 5] 0 setdash'
    print x0 + 10, plen * (-1 + .5/lam), 'moveto 150 0 rlineto stroke'
    print '[] 0 setdash'

    weightrad = 4
    print 'gsave'
    print 3, 'circ stroke'
    if lam > .25:
	th = acos(1 - .5/lam)
    else:
	th = 3.7
    print -th * 180 / pi, 'rotate'
    print 0, -3, 'moveto', 0, 3-plen, 'rlineto stroke'
    print 'gsave', 0, -plen, 'translate', weightrad, 'circ fill'
    print 'grestore'
    print '[4] 0 setdash'
    if lam > .25:
	print 0, -plen, 'moveto', 0, 0, plen, 270, 270 + 2 * th * 180/pi, 'arc stroke'
	print 2 * th * 180/pi, 'rotate'
	print 0, -3, 'moveto', 0, 3-plen + weightrad, 'rlineto stroke'
	print 0, -plen, 'translate', weightrad, 'circ stroke'
    else:
	print 0, -plen, 'moveto', 0, 0, plen, 270, 360 + 270, 'arc stroke'
	print '[] 0 setdash'
	print 0, -plen - 10, 'moveto', 0, 0, plen + 10, 260, 280, 'arc stroke'
	print 'gsave 260 rotate'
	print plen + 10 + 4, 4, 'moveto -4 -4 rlineto -4 4 rlineto stroke'
	print 'grestore'
    print 'grestore'

    s = 17
    if lam == .5: s = 13.2
    if lam > .9: s = 8
    xyk, cost = run_elastica(-s, s, 1, 0, -lam)
    sc = 10
    plot(xyk, 150, -.5 * sc * max([xy[1] for xy in xyk]), sc, sc)

def draw_pendulum_examples():
    print '%!PS-Adobe-3.0 EPSF'
    print '/Times-Roman 12 selectfont'
    print '/circ { /ss exch def ss 0 moveto currentpoint exch ss sub exch ss 0 360 arc } bind def'
    for i in range(4):
	print 'gsave 250', 150 + i * 130, 'translate'
	draw_pendulum_example([2, .5, .26, .2][i])
	print 'grestore'

def run_mec_vs_simec():
    print '%!PS-Adobe-3.0 EPSF'
    a = 0.71052317472
    chord, chth, cost, sc = find_antisym_elastica(pi / 2, a)
    xyk, cost = run_elastica(-5, 5, 0, sc * cos(a), sc * sin(a))
    plot(xyk, 200, 200, 4, 4)

def mec_euler_compare():
    print '%!PS-Adobe-3.0 EPSF'
    print '/Times-Roman 12 selectfont'
    target = pi / 2
    kscale = 200.0
    for i in (0, 1):
	a = i * 480 * .001480256614
	chord, chth, cost, sc = find_antisym_elastica(target, a)
	print 'gsave', 300, 300 + 100 * i, 'translate'
	print '120 -4 moveto (%s) show' % ('MEC', 'SI-MEC')[i]
	print -180 * chth / pi, 'rotate'
	xyk, cost = run_elastica(-5, 5, 0, sc * cos(a), sc * sin(a))
	scale = 100 / chord
	plot(xyk, 0, 0, scale, scale)

	# draw curvature tickmarks
	for i in range(len(xyk) - 1):
	    k0 = floor(kscale * xyk[i][2] / scale)
	    k1 = floor(kscale * xyk[i + 1][2] / scale)
	    if k0 != k1:
		# todo: linear interpolation to place tick more accurately
		x, y = xyk[i][:2]
		print 'gsave'
		print x * scale, y * scale, 'translate'
		print 180 * a / pi, 'rotate'
		print '0 -5 moveto 0 5 lineto stroke'
		print 'grestore'

	if 0:
	    print 180 * a / pi, 'rotate'
	    print 0, -70 * sc, 'moveto', 0, 70 * sc, 'lineto stroke'

	print 'grestore'

    # Euler spiral
    print 'gsave 300 500 translate'
    print '120 -4 moveto (%s) show' % 'Euler spiral'
    seg = pcorn.Segment((-100, 0), (100, 0), -target, target)
    xys = []
    for i in range(101):
	s = seg.arclen * i * .01
	xys.append(seg.xy(s))
    plot(xys, 0, 0, 1, 1)
    s_tick = seg.arclen * seg.arclen / (kscale * seg.k1)
    n_ticks = int(floor(0.5 * seg.arclen / s_tick))
    print >> sys.stderr, s_tick, n_ticks
    for i in range(-n_ticks, n_ticks + 1):
	s = i * s_tick + seg.arclen * 0.5
	print >> sys.stderr, s
	x, y = seg.xy(s)
	th = seg.th(s)
	print 'gsave', x, y, 'translate'
	print 180 * th / pi, 'rotate'
	print '0 -5 moveto 0 5 lineto stroke'
	print 'grestore'

    print 'grestore'

    print 'showpage'

def touching():
    print '%!PS-Adobe-3.0 EPSF'
    lam = 0.341911657135
    xyk, cost = run_elastica(-25, 25, 1, 0, -lam)
    plot(xyk, 300, 300, 50, 50)
    for i in range(7):
	if i == 0:
	    print '1 setlinewidth'
	else:
	    print '.5 setlinewidth'
	y = 300 + 50 * i
	print 300 - 250, y, 'moveto 500 0 rlineto stroke'
    for i in range(-5, 6):
	if i == 0:
	    print '1 setlinewidth'
	else:
	    print '.5 setlinewidth'
	x = 300 + 50 * i
	print x, 300, 'moveto 0 300 rlineto stroke'
    eps_trailer()

if __name__ == '__main__':
    figure = sys.argv[1]
    if figure in ('elastica-fam.pdf', 'elastica-fam-k.pdf'):
	print '%!PS-Adobe-3.0 EPSF'

	y = 700
	print 'gsave 0.5 setlinewidth'
	x0 = 300
	if figure == 'elastica-fam-k.pdf': x0 = 350
	print x0, y + 40, 'moveto', 0, -690, 'rlineto stroke'
	print 'grestore'
	for i in range(12):
	    if figure == 'elastica-fam.pdf':
		ya = [50, 55, 60, 65, 80, 80, 70, 60, 50, 30, 30, 25]
	    else:
		ya = [55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55, 55]
	    la = [.1, .2, .249, .25, .251, .28, .5 / 1.651868, .35, .4, .5, 1, 2]
	    lam = la[i]
	    print 72, y + 14, 'moveto /Symbol 12 selectfont (l) show'
	    #print '0 -2 rmoveto /Times-Roman 8 selectfont (1) show'
	    #print '0 2 rmoveto'
	    print '/Times-Roman 12 selectfont ( = ' + ('%.4g' % lam) + ') show'
	    xyk, cost = run_elastica(-25, 25, 1, 0, -lam)
	    if figure == 'elastica-fam.pdf':
		plot(xyk, 300, y, 10, 10)
	    else:
		print 'gsave .5 setlinewidth'
		print 100, y, 'moveto', len(xyk), 0, 'rlineto stroke'
		print 'grestore'
		cmd = 'moveto'
		s = 0
		for x, yy, k in xyk:
		    print 100 + s * 10, y + k * 10, cmd
		    cmd = 'lineto'
		    s += .1
		print 'stroke'
	    y -= ya[i]

	eps_trailer()

    elif figure == 'horn.pdf':
	if 0:
	    eps_prologue(150, 290, 450, 501)
	    xyk = compute_elastica(-2.63, 2.63, 1, .5)
	    plot(xyk, 300, 500, -100, -100)
	    print '1 0 0 setrgbcolor'
	xyk, cost = run_elastica(-2.63, 2.63, 1, 0, -.5)
	plot(xyk, 300, 500, -100, -100)
	eps_trailer()

    elif figure == 'moment.pdf':
	draw_moment()

    elif figure == 'moment_bernoul.pdf':
	draw_moment_bernoul()

    elif figure == 'rectel.pdf':
	draw_rectel()

    elif figure == 'chain.pdf':
	draw_chain()

    elif figure == 'bernoulli91.pdf':
	if len(sys.argv) > 2:
	    draw_bernoulli91(int(sys.argv[2]))
	else:
	    draw_bernoulli91()
    elif figure == 'simecplot.pdf':
	run_simec()

    elif figure == 'mecvssimec.pdf':
	run_mec_vs_simec()

    elif figure == 'pendulum.pdf':
	draw_pendulum()

    elif figure == 'pendex.pdf':
	draw_pendulum_examples()

    elif figure == 'mec_euler_compare.pdf':
	mec_euler_compare()

    elif figure == 'touching.pdf':
	touching()
