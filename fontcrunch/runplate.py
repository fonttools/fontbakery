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

import bigmat
import polyfigs

def read_plate(f):
    paths = []
    l = f.readline()
    if l.strip() != '(plate':
        return None
    subpath = []
    for l in f.xreadlines():
        if l == '':
            return None
        l = l.strip()
        if l == ')':
            break
        if len(l) >= 2 and l[0] == '(' and l[-1] == ')':
            list = l[1:-1].split()
            if list == ['z']:
                paths.append(subpath)
                subpath = []
            elif list[0] in 'voc[]':
                subpath.append((float(list[1]), float(list[2]), list[0]))
    if len(subpath):
        subpath[0] = (subpath[0][0], subpath[0][1], '{')
        subpath[-1] = (subpath[-1][0], subpath[-1][1], '}')
        paths.append(subpath)
    return paths

def scale_subpath(subpath, scale):
    result = []
    for el in subpath:
	if len(el) == 3:
	    x, y, cmd = el
	    result.append((x * scale, y * scale, cmd))
	else:
	    result.append(el)
    return result

def run_multi(fn, show_nodes):
    bigmat.prologue()
    print '1 -1 scale 0 -720 translate'
    for l in file(fn).xreadlines():
	if l.startswith('#'):
	    continue
	s = l.split()
	fn = s[0]
	x = float(s[1])
	y = float(s[2])
	print >> sys.stderr, fn
	if (len(s) > 3):
	    scale = float(s[3])
	else:
	    scale = 1
	paths= read_plate(file(fn))
	for subpath in paths:
	    subpath = scale_subpath(subpath, scale)
	    print 'gsave', x, y, 'translate', 0.6, 'dup scale'
	    bigmat.run_path(subpath, False, 10, None, None, None, None, show_nodes)
	    print 'grestore'
    print 'showpage'

def run_one(fn, show_nodes, show_iter, xo, yo, xscale, yscale):
    paths = read_plate(file(fn))
    if paths == None:
        print >> sys.stderr, "Can't handle plate", fn
    else:
        print '%!PS-Adobe-3.0 EPSF'
        print '1 -1 scale 0 -720 translate'
        bigmat.prologue()
        for subpath in paths:
            bigmat.run_path(subpath, show_iter, 10, xo, yo, xscale, yscale, show_nodes)
	print 'showpage'

if __name__ == '__main__':
    show_iter = False
    show_nodes = False
    xo, yo, xscale, yscale = None, None, None, None
    multi = False
    fn = None
    for arg in sys.argv[1:]:
        if arg == '-n':
            show_nodes = True
        elif arg == '-i':
            show_iter = True
        elif arg == '-k':
            xo, yo, xscale, yscale = 100, 550, .375, -3000
	elif arg == '-m':
	    multi = True
        elif len(arg) > 2 and arg[0:2] == '-k':
            xo, yo, xscale, yscale = [float(s) for s in arg[2:].split(',')]
        else:
            fn = arg
    if multi:
	run_multi(fn, show_nodes)
    else:
	run_one(fn, show_nodes, show_iter, xo, yo, xscale, yscale)
