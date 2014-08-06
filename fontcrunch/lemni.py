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

print '%!PS-Adobe-3.0 EPSF'
n = 1000
scale = 200
print '.75 setlinewidth'
print 306, 396 - scale * .5, 'moveto', 0, scale, 'rlineto stroke'
print 306 - scale, 396, 'moveto', 2 * scale, 0, 'rlineto stroke'
print '1.5 setlinewidth'
cmd = 'moveto'
for j in range(n):
    th = (2 * pi * j) / n
    if (cos(2 * th) >= 0):
	r = sqrt(cos(2 * th))
	x = r * cos(th)
	y = r * sin(th)
	print 306 + scale * x, 396 + scale * y, cmd
	cmd = 'lineto'
print 'closepath stroke showpage'
