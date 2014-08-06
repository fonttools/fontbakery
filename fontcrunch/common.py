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
# Common drawing utilities. Most of this stuff exists in ad hoc form in the
# individual drawing programs, but it should get migrated here in the interest
# of cleanup.

linescale = 1
flags = {}

import sys

def setlinewidth(width = 1):
    print width * linescale, 'setlinewidth'

def parse_cmdline():
    figname = None
    global flags
    flagname = None
    args = []
    for arg in sys.argv[1:]:
	if arg.startswith('-') and flagname is None:
	    flagname = arg[1:]
	else:
	    if flagname:
		flags[flagname] = arg
		flagname = None
	    elif figname is None:
		figname = arg
	    else:
		args.append(arg)
    if figname and figname.endswith('.pdf'):
	figname = figname[:-4]
    #print '%', figname, args, flags
    if 'linescale' in flags:
	global linescale
	linescale = float(flags['linescale'])
    return figname, args, flags
