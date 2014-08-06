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
# Some code to convert arbitrary curves to high quality cubics.

# Some conventions: points are (x, y) pairs. Cubic Bezier segments are
# lists of four points.

import sys
import common

from math import *

import pcorn

def pt_wsum(points, wts):
    x, y = 0, 0
    for i in range(len(points)):
        x += points[i][0] * wts[i]
        y += points[i][1] * wts[i]
    return x, y

# Very basic spline primitives
def bz_eval(bz, t):
    degree = len(bz) - 1
    mt = 1 - t
    if degree == 3:
        return pt_wsum(bz, [mt * mt * mt, 3 * mt * mt * t, 3 * mt * t * t, t * t * t])
    elif degree == 2:
        return pt_wsum(bz, [mt * mt, 2 * mt * t, t * t])
    elif degree == 1:
        return pt_wsum(bz, [mt, t])

def bz_deriv(bz):
    degree = len(bz) - 1
    return [(degree * (bz[i + 1][0] - bz[i][0]), degree * (bz[i + 1][1] - bz[i][1])) for i in range(degree)]

def bz_arclength(bz, n = 10):
    # We're just going to integrate |z'| over the parameter [0..1].
    # The integration algorithm here is eqn 4.1.14 from NRC2, and is
    # chosen for simplicity. Likely adaptive and/or higher-order
    # algorithms would be better, but this should be good enough.
    # Convergence should be quartic in n.
    wtarr = (3./8, 7./6, 23./24)
    dt = 1./n
    s = 0
    dbz = bz_deriv(bz)
    for i in range(0, n + 1):
        if i < 3:
            wt = wtarr[i]
        elif i > n - 3:
            wt = wtarr[n - i]
        else:
            wt = 1.
        dx, dy = bz_eval(dbz, i * dt)
        ds = hypot(dx, dy)
        s += wt * ds
    return s * dt

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

def bz_arclength_rk4(bz, n = 10):
    dbz = bz_deriv(bz)
    def arclength_deriv(x, ys):
        dx, dy = bz_eval(dbz, x)
        return [hypot(dx, dy)]
    dt = 1./n
    t = 0
    ys = [0]
    for i in range(n):
        dydx = arclength_deriv(t, ys)
        rk4(ys, dydx, t, dt, arclength_deriv)
        t += dt
    return ys[0]

# z0 and z1 are start and end points, resp.
# th0 and th1 are the initial and final tangents, measured in the
# direction of the curve.
# aab is a/(a + b), where a and b are the lengths of the bezier "arms"
def fit_cubic_arclen(z0, z1, arclen, th0, th1, aab):
    chord = hypot(z1[0] - z0[0], z1[1] - z0[1])
    cth0, sth0 = cos(th0), sin(th0)
    cth1, sth1 = -cos(th1), -sin(th1)
    armlen = .66667 * chord
    darmlen = 1e-6 * armlen
    for i in range(10):
        a = armlen * aab
        b = armlen - a
        bz = [z0, (z0[0] + cth0 * a, z0[1] + sth0 * a),
              (z1[0] + cth1 * b, z1[1] + sth1 * b), z1]
        actual_s = bz_arclength_rk4(bz)
        if (abs(arclen - actual_s) < 1e-12):
            break
        a = (armlen + darmlen) * aab
        b = (armlen + darmlen) - a
        bz = [z0, (z0[0] + cth0 * a, z0[1] + sth0 * a),
              (z1[0] + cth1 * b, z1[1] + sth1 * b), z1]
        actual_s2 = bz_arclength_rk4(bz)
        ds = (actual_s2 - actual_s) / darmlen
        #print '% armlen = ', armlen
        if ds == 0:
            break
        armlen += (arclen - actual_s) / ds
    a = armlen * aab
    b = armlen - a
    bz = [z0, (z0[0] + cth0 * a, z0[1] + sth0 * a),
          (z1[0] + cth1 * b, z1[1] + sth1 * b), z1]
    return bz

def mod_2pi(th):
    u = th / (2 * pi)
    return 2 * pi * (u - floor(u + 0.5))

def measure_bz(bz, arclen, th_fn, n = 1000):
    dt = 1./n
    dbz = bz_deriv(bz)
    s = 0
    score = 0
    for i in range(n):
        dx, dy = bz_eval(dbz, (i + .5) * dt)
        ds = dt * hypot(dx, dy)
        s += ds
        score += ds * (mod_2pi(atan2(dy, dx) - th_fn(s)) ** 2)
    return score

def measure_bz_rk4(bz, arclen, th_fn, n = 10):
    dbz = bz_deriv(bz)
    def measure_derivs(x, ys):
        dx, dy = bz_eval(dbz, x)
        ds = hypot(dx, dy)
        s = ys[0]
        dscore = ds * (mod_2pi(atan2(dy, dx) - th_fn(s)) ** 2)
        return [ds, dscore]
    dt = 1./n
    t = 0
    ys = [0, 0]
    for i in range(n):
        dydx = measure_derivs(t, ys)
        rk4(ys, dydx, t, dt, measure_derivs)
        t += dt
    return ys[1]

# th_fn() is a function that takes an arclength from the start point, and
# returns an angle - thus th_fn(0) and th_fn(arclen) are the initial and
# final tangents.
# z0, z1, and arclen are as fit_cubic_arclen
def fit_cubic(z0, z1, arclen, th_fn, fast = 1):
    chord = hypot(z1[0] - z0[0], z1[1] - z0[1])
    if (arclen < 1.000001 * chord):
        return [z0, z1], 0
    th0 = th_fn(0)
    th1 = th_fn(arclen)
    imax = 4
    jmax = 10
    aabmin = 0
    aabmax = 1.
    if fast:
        imax = 1
        jmax = 0
    for i in range(imax):
        for j in range(jmax + 1):
            if jmax == 0:
                aab = 0.5 * (aabmin + aabmax)
            else:
                aab = aabmin + (aabmax - aabmin) * j / jmax
            bz = fit_cubic_arclen(z0, z1, arclen, th0, th1, aab)
            score = measure_bz_rk4(bz, arclen, th_fn)
            print '% aab =', aab, 'score =', score
            sys.stdout.flush()
            if j == 0 or score < best_score:
                best_score = score
                best_aab = aab
                best_bz = bz
        daab = .06 * (aabmax - aabmin)
        aabmin = max(0, best_aab - daab)
        aabmax = min(1, best_aab + daab)
        print '%--- best_aab =', best_aab
    return best_bz, best_score

def plot_prolog(x0, y0, x1, y1, draw_box = False):
    print '%!PS-Adobe-3.0 EPSF'
    print '%%BoundingBox:', x0, y0, x1, y1
    print '%%EndComments'
    print '%%EndProlog'
    print '%%Page: 1 1'
    if draw_box:
        print x0, y0, 'moveto', x0, y1, 'lineto', x1, y1, 'lineto', x1, y0, 'lineto closepath stroke'
    print '/m { moveto } bind def'
    print '/l { lineto } bind def'
    print '/c { curveto } bind def'
    print '/z { closepath } bind def'

def plot_bz(bz, z0, scale, do_moveto = True):
    x0, y0 = z0
    if do_moveto:
        print bz[0][0] * scale + x0, bz[0][1] * scale + y0, 'm'
    if len(bz) == 4:
        x1, y1 = bz[1][0] * scale + x0, bz[1][1] * scale + y0
        x2, y2 = bz[2][0] * scale + x0, bz[2][1] * scale + y0
        x3, y3 = bz[3][0] * scale + x0, bz[3][1] * scale + y0
        print x1, y1, x2, y2, x3, y3, 'c'
    elif len(bz) == 2:
        print bz[1][0] * scale + x0, bz[1][1] * scale + y0, 'l'

def test_bz_arclength():
    bz = [(0, 0), (.5, 0), (1, 0.5), (1, 1)]
    ans = bz_arclength_rk4(bz, 2048)
    last = 1
    lastrk = 1
    for i in range(3, 11):
        n = 1 << i
        err = bz_arclength(bz, n) - ans
        err_rk = bz_arclength_rk4(bz, n) - ans
        print n, err, last / err, err_rk, lastrk / err_rk
        last = err
        lastrk = err_rk

def test_fit_cubic_arclen():
    th = pi / 4
    arclen = th / sin(th)
    bz = fit_cubic_arclen((0, 0), (1, 0), arclen, th, th, .5)
    print '%', bz
    plot_bz(bz, (100, 400), 500)
    print 'stroke'
    print 'showpage'

# -- cornu fitting

import cornu

def cornu_to_cubic(t0, t1):
    def th_fn(s):
        return (s + t0) ** 2
    y0, x0 = cornu.eval_cornu(t0)
    y1, x1 = cornu.eval_cornu(t1)
    bz, score = fit_cubic((x0, y0), (x1, y1), t1 - t0, th_fn, 0)
    return bz, score

def test_draw_cornu(imax = 500, draw_axes = True, draw_poles = True, draw_pts = False):
    plot_prolog(306 - 255, 396 - 234, 306 + 255, 396 + 234, False)
    if 'rot' in common.flags:
	print '306 396 translate', common.flags['rot'], 'rotate'
	print '-306 -396 translate'
    common.setlinewidth()
    print 'gsave'
    common.setlinewidth(.5)
    print '/Times-Roman 10 selectfont'
    print '/cshow {dup stringwidth exch -.5 mul exch rmoveto show} bind def'
    print '/rshow {dup stringwidth exch neg exch rmoveto show} bind def'
    if draw_axes:
	print 306, 396 - 230, 'moveto', 0, 460, 'rlineto stroke'
	print 306 - 250, 396, 'moveto', 500, 0, 'rlineto stroke'
	for i in range(-10, 11):
	    if i == 0:
		print 306 + 25 * i - 2, 396 - 10, 'moveto (%g)' % (.1 * i), 'rshow'
	    else:
		print 306 + 25 * i, 396, 'moveto', 0, 4, 'rlineto stroke'
		print 306 + 25 * i, 396 - 10, 'moveto (%g)' % (.1 * i), 'cshow'
	for i in range(-9, 10):
	    if i != 0:
		print 306, 396 + 25 * i, 'moveto', 4, 0, 'rlineto stroke'
		print 306 - 2, 396 + 25 * i - 3, 'moveto (%g)' % (.1 * i), 'rshow'
    if draw_poles:
	print '/piratetreasure { gsave -4 0 rmoveto 8 0 rlineto stroke grestore 0 -4 rmoveto 0 8 rlineto stroke } bind def'
	limit = sqrt(pi/8)
	print 306 + 250 * limit, 396 + 250 * limit, 'moveto piratetreasure'
	print 306 - 250 * limit, 396 - 250 * limit, 'moveto piratetreasure'
    print 'grestore'
    thresh = 1e-9
    print '/ss 1.5 def'
    print '/circle { ss 0 moveto currentpoint exch ss sub exch ss 0 360 arc } bind def'
    s0 = 0
    x0, y0, scale = 8.5 * 36, 11 * 36, 250
    bzs = []
    for i in range(1, imax):
        s = sqrt(i * .1)
        bz, score = cornu_to_cubic(s0, s)
        if score > (s - s0) * thresh or i == imax - 1:
            # plot_bz(bz, (x0, y0), scale, s0 == 0)
            bzs.append(bz)
            s0 = s
    frist = True
    for i in range(len(bzs) - 1, -1, -1):
        bzr = bzs[i][:]
        bzr.reverse()
        plot_bz(bzr, (x0, y0), -scale, frist)
        frist = False
    for i in range(len(bzs)):
        plot_bz(bzs[i], (x0, y0), scale, False)
    print 'stroke'
    if draw_pts:
        for i in range(len(bzs)):
            bz = bzs[i]
            bx0, by0 = x0 + bz[0][0] * scale, y0 + bz[0][1] * scale
            bx1, by1 = x0 + bz[1][0] * scale, y0 + bz[1][1] * scale
            bx2, by2 = x0 + bz[2][0] * scale, y0 + bz[2][1] * scale
            bx3, by3 = x0 + bz[3][0] * scale, y0 + bz[3][1] * scale
            print 'gsave 0 0 1 setrgbcolor .5 setlinewidth'
            print bx0, by0, 'moveto', bx1, by1, 'lineto stroke'
            print bx2, by2, 'moveto', bx3, by3, 'lineto stroke'
            print 'grestore'
            print 'gsave', bx0, by0, 'translate circle fill grestore'
            print 'gsave', bx1, by1, 'translate .5 dup scale circle fill grestore'
            print 'gsave', bx2, by2, 'translate .5 dup scale circle fill grestore'
            print 'gsave', bx3, by3, 'translate circle fill grestore'

def e675_spiral(imax = 200, draw_axes = True, draw_poles = True):
    scale = 125
    plot_prolog(306 - 6, 396 - 14, 306 + scale * 1.2 + 5, 396 + scale * .95, False)
    print 'gsave .5 setlinewidth'
    print '/Times-Roman 10 selectfont'
    print '/cshow {dup stringwidth exch -.5 mul exch rmoveto show} bind def'
    print '/rshow {dup stringwidth exch neg exch rmoveto show} bind def'
    if draw_axes:
	#print 306, 396, 'moveto', 0, 460, 'rlineto stroke'
	print 306, 396, 'moveto', scale * 1.2, 0, 'rlineto stroke'
	#for i in range(1, 11):
	#    print 306 + 25 * i, 396, 'moveto', 0, 4, 'rlineto stroke'
	#for i in range(1, 10):
	#    print 306, 396 + 25 * i, 'moveto', 4, 0, 'rlineto stroke'
    if draw_poles:
	print '/piratetreasure { gsave -4 0 rmoveto 8 0 rlineto stroke grestore 0 -4 rmoveto 0 8 rlineto stroke } bind def'
	limit = sqrt(pi/8)
	print 306 + scale * limit, 396 + scale * limit, 'moveto piratetreasure'
	print 306 - 2, 396 - 12, 'moveto (A) show'
	print 306 + scale * limit - 8, 396 + scale * limit + 2, 'moveto (O) show'
	print 306 + scale * limit - 2, 396 - 12, 'moveto (C) show'
	print 'gsave [2] 0 setdash'
	print 306 + scale * limit, 396, 'moveto', 0, scale * limit, 'rlineto stroke'
	print 'grestore'
	#print 306 - scale * limit, 396 - scale * limit, 'moveto piratetreasure'
	y, x = cornu.eval_cornu(1.0)
	print 306 + scale * x, 396 + scale * y, 'moveto'
	print 306 + scale * x, 396, 'lineto stroke'
	print 306 + scale * x + 4, 396 + scale * y - 6, 'moveto (M) show'
	print 306 + scale * x - 2, 396 - 12, 'moveto (P) show'
    print 'grestore'
    thresh = 1e-9
    print '/ss 1.5 def'
    print '/circle { ss 0 moveto currentpoint exch ss sub exch ss 0 360 arc } bind def'
    s0 = 0
    x0, y0 = 8.5 * 36, 11 * 36
    bzs = []
    for i in range(1, imax):
        s = sqrt(i * .1)
        bz, score = cornu_to_cubic(s0, s)
        if score > (s - s0) * thresh or i == imax - 1:
            # plot_bz(bz, (x0, y0), scale, s0 == 0)
            bzs.append(bz)
            s0 = s
    frist = True
    for i in range(len(bzs)):
        plot_bz(bzs[i], (x0, y0), scale, frist)
        frist = False
    print 'stroke'

# -- fitting of piecewise cornu curves

def pcorn_segment_to_bzs_optim_inner(curve, s0, s1, thresh, nmax = None):
    result = []
    if s0 == s1: return [], 0
    while s0 < s1:
        def th_fn_inner(s):
            if s > s1: s = s1
            return curve.th(s0 + s, s == 0)
        z0 = curve.xy(s0)
        z1 = curve.xy(s1)
        bz, score = fit_cubic(z0, z1, s1 - s0, th_fn_inner, 0)
        if score < thresh or nmax != None and len(result) == nmax - 1:
            result.append(bz)
            break
        r = s1
        l = s0 + .001 * (s1 - s0)
        for i in range(10):
            smid = 0.5 * (l + r)
            zmid = curve.xy(smid)
            bz, score = fit_cubic(z0, zmid, smid - s0, th_fn_inner, 0)
            if score > thresh:
                r = smid
            else:
                l = smid
        print '% s0=', s0, 'smid=', smid, 'actual score =', score
        result.append(bz)
        s0 = smid
    print '% last actual score=', score
    return result, score

def pcorn_segment_to_bzs_optim(curve, s0, s1, thresh, optim):
    result, score = pcorn_segment_to_bzs_optim_inner(curve, s0, s1, thresh)
    bresult, bscore = result, score
    if len(result) > 1 and optim > 2:
        nmax = len(result)
        gamma = 1./6
        l = score
        r = thresh
        for i in range(5):
            tmid = (0.5 * (l ** gamma + r ** gamma)) ** (1/gamma)
            result, score = pcorn_segment_to_bzs_optim_inner(curve, s0, s1, tmid, nmax)
            if score < tmid:
                l = max(l, score)
                r = tmid
            else:
                l = tmid
                r = min(r, score)
            if max(score, tmid) < bscore:
                bresult, bscore = result, max(score, tmid)
    return result

def pcorn_segment_to_bzs(curve, s0, s1, optim = 0, thresh = 1e-3):
    if optim >= 2:
        return pcorn_segment_to_bzs_optim(curve, s0, s1, thresh, optim)
    z0 = curve.xy(s0)
    z1 = curve.xy(s1)
    fast = (optim == 0)
    def th_fn(s):
        return curve.th(s0 + s, s == 0)
    bz, score = fit_cubic(z0, z1, s1 - s0, th_fn, fast)
    if score < thresh:
        return [bz]
    else:
        smid = 0.5 * (s0 + s1)
        result = pcorn_segment_to_bzs(curve, s0, smid, optim, thresh)
        result.extend(pcorn_segment_to_bzs(curve, smid, s1, optim, thresh))
        return result

def pcorn_curve_to_bzs(curve, optim = 3, thresh = 1e-3):
    result = []
    extrema = curve.find_extrema()
    extrema.extend(curve.find_breaks())
    extrema.sort()
    print '%', extrema
    for i in range(len(extrema)):
        s0 = extrema[i]
        if i == len(extrema) - 1:
            s1 = extrema[0] + curve.arclen
        else:
            s1 = extrema[i + 1]
        result.extend(pcorn_segment_to_bzs(curve, s0, s1, optim, thresh))
    return result

import struct

def fit_cubic_arclen_forplot(z0, z1, arclen, th0, th1, aab):
    chord = hypot(z1[0] - z0[0], z1[1] - z0[1])
    cth0, sth0 = cos(th0), sin(th0)
    cth1, sth1 = -cos(th1), -sin(th1)
    armlen = .66667 * chord
    darmlen = 1e-6 * armlen
    for i in range(10):
        a = armlen * aab
        b = armlen - a
        bz = [z0, (z0[0] + cth0 * a, z0[1] + sth0 * a),
              (z1[0] + cth1 * b, z1[1] + sth1 * b), z1]
        actual_s = bz_arclength_rk4(bz)
        if (abs(arclen - actual_s) < 1e-12):
            break
        a = (armlen + darmlen) * aab
        b = (armlen + darmlen) - a
        bz = [z0, (z0[0] + cth0 * a, z0[1] + sth0 * a),
              (z1[0] + cth1 * b, z1[1] + sth1 * b), z1]
        actual_s2 = bz_arclength_rk4(bz)
        ds = (actual_s2 - actual_s) / darmlen
        #print '% armlen = ', armlen
        armlen += (arclen - actual_s) / ds
    a = armlen * aab
    b = armlen - a
    bz = [z0, (z0[0] + cth0 * a, z0[1] + sth0 * a),
          (z1[0] + cth1 * b, z1[1] + sth1 * b), z1]
    return bz, a, b

def plot_errors_2d(t0, t1, as_ppm):
    xs = 1024
    ys = 1024
    if as_ppm:
        print 'P6'
        print xs, ys
        print 255
    def th_fn(s):
        return (s + t0) ** 2
    y0, x0 = cornu.eval_cornu(t0)
    y1, x1 = cornu.eval_cornu(t1)
    z0 = (x0, y0)
    z1 = (x1, y1)
    chord = hypot(y1 - y0, x1 - x0)
    arclen = t1 - t0
    th0 = th_fn(0)
    th1 = th_fn(arclen)
    cth0, sth0 = cos(th0), sin(th0)
    cth1, sth1 = -cos(th1), -sin(th1)

    for y in range(ys):
        b = .8 * chord * (ys - y - 1) / ys
        for x in range(xs):
            a = .8 * chord * x / xs
            bz = [z0, (z0[0] + cth0 * a, z0[1] + sth0 * a),
              (z1[0] + cth1 * b, z1[1] + sth1 * b), z1]
            s_bz = bz_arclength(bz, 10)
            def th_fn_scaled(s):
                return (s * arclen / s_bz + t0) ** 2
            score = measure_bz_rk4(bz, arclen, th_fn_scaled, 10)
            if as_ppm:
                ls = -log(score)
                color_th = ls
                darkstep = 0
                if s_bz > arclen:
                    g0 = 128 - darkstep
                else:
                    g0 = 128 + darkstep
                sc = 127 - darkstep
                rr = g0 + sc * cos(color_th)
                gg = g0 + sc * cos(color_th + 2 * pi / 3)
                bb = g0 + sc * cos(color_th - 2 * pi / 3)
                sys.stdout.write(struct.pack('3B', rr, gg, bb))
            else:
                print a, b, score
        if not as_ppm:
            print

def plot_arclen(t0, t1):
    def th_fn(s):
        return (s + t0) ** 2
    y0, x0 = cornu.eval_cornu(t0)
    y1, x1 = cornu.eval_cornu(t1)
    z0 = (x0, y0)
    z1 = (x1, y1)
    chord = hypot(y1 - y0, x1 - x0)
    arclen = t1 - t0
    th0 = th_fn(0)
    th1 = th_fn(arclen)
    for i in range(101):
        aab = i * .01
        bz, a, b = fit_cubic_arclen_forplot(z0, z1, arclen, th0, th1, aab)
        print a, b

if __name__ == '__main__':
    figname, args, flags = common.parse_cmdline()
    #test_bz_arclength()
    if figname == 'cornu':
	test_draw_cornu()
    elif figname == 'espiral':
	test_draw_cornu(500, draw_axes = False)
    elif figname == 'e675_spiral':
	e675_spiral()
    #run_one_cornu_seg()
    #plot_errors_2d(.5, 1.0, False)
    #plot_arclen(.5, 1.0)
