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
import cornu

x0 = 200
y0 = 396
sscale = 100
s0 = -.4
s1 = .6
smax = 1
fscale = 10.0

print """%!PS-Adobe-3.0 EPSF
% diffraction diagram coded in raw PostScript

/x0 200 def
/y0 396 def

/x1 400 def

/sscale 100 def

/smax 1 def"""
print "/s0", s0, "def"
print "/s1", s1, "def"
print "/fscale", fscale, "def"

print """
1.5 setlinewidth
x0 y0 smax neg sscale mul add moveto x0 y0 s0 sscale mul add lineto stroke
x0 y0 smax sscale mul add moveto x0 y0 s1 sscale mul add lineto stroke

x1 y0 smax neg sscale mul add moveto 0 smax sscale mul 2 mul rlineto stroke

0.75 setlinewidth

1 1 4 {
    gsave
    .2 mul s1 s0 sub mul s0 add sscale mul y0 add x0 exch translate
    0 0 22 -85 dup neg arc stroke
    grestore
} for

%1 1 4 {
%    gsave
%    .2 mul s1 s0 sub mul s0 add sscale mul y0 add x0 exch translate
%    0 0 100 -60 dup neg arc stroke
%    grestore
%} for

gsave
x0 y0 translate
0 0 x1 x0 sub -30 dup neg arc stroke
grestore

/wavelength sscale fscale div 0.5 mul def
gsave
x0 y0 translate
0 0 x1 x0 sub wavelength sub -30 dup neg arc stroke
grestore

x1 32 sub y0 80 sub moveto
/Symbol 12 selectfont (l) show

gsave
x0 y0 translate
-27 rotate
x1 x0 sub wavelength sub 0 moveto -8 0 rlineto stroke
x1 x0 sub wavelength sub 0 moveto -4 -2 rmoveto 4 2 rlineto -4 2 rlineto stroke
x1 x0 sub 0 moveto 8 0 rlineto stroke
x1 x0 sub 0 moveto 4 -2 rmoveto -4 2 rlineto 4 2 rlineto stroke
grestore

0.75 setlinewidth
x0 20 sub y0 moveto x1 y0 lineto stroke

/Times-Italic 12 selectfont
x0 12 sub y0 s0 sscale mul add moveto (s) show
/Times-Roman 8 selectfont
0 -1 rmoveto (0) show
/Times-Italic 12 selectfont
x0 12 sub y0 s1 sscale mul add moveto (s) show
/Times-Roman 8 selectfont
0 -1 rmoveto (1) show
/Times-Italic 12 selectfont
x0 4 add y0 smax sscale mul add 12 sub moveto (s) show

x0 x1 add .5 mul 4 sub y0 4 add moveto (x) show

/Symbol 12 selectfont
x1 y0 80 add moveto -17 0 rlineto stroke
x1 -12 add y0 85 add moveto (f) show"""

cmd = 'moveto'
print '1 setlinewidth'
for i in range(501):
    s = smax * ((i * .004) - 1)
    fs0, fc0 = cornu.eval_cornu((s - s0) * fscale)
    fs1, fc1 = cornu.eval_cornu((s - s1) * fscale)
    dx = fc1 - fc0
    dy = fs1 - fs0
    I = dx * dx + dy * dy
    print 410 + 10 * I, y0 + s * sscale, cmd
    cmd = 'lineto'
print 'stroke'

print "showpage"
