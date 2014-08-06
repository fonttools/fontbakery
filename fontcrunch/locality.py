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
def compute(s0, s1, a = 1):
    th_ch = s1 ** (a+2) + (-s0) ** (a + 2) / ((a+1) * (a+2) * (s1-s0))
    th0 = (-s0) ** (a+1) / (a + 1) - th_ch
    th1 = s1 ** (a+1) / (a + 1) - th_ch
    k0 = -(-s0) ** a * (s1-s0)
    k1 = s1 ** a * (s1 - s0)
    return th0, th1, k0, k1

# solve for k0/th0 = k1/th1
# use bisection because it's so easy
def solve(s0, a = 1):
    l = 0
    r = -s0 * .5
    for i in range(30):
	m = (l + r) * .5
	#m = i * -s0 * .05
	th0, th1, k0, k1 = compute(s0, m, a)
	err = k1 / th1 - k0 / th0
	#print err
	if err > 0:
	    l = m
	else:
	    r = m
    #print 'falloff =', k1 / k0
    return k1 / k0

def make_graph():
    for i in range(101):
	a = i * .05
	print a, -solve(-.01, a)

make_graph()
