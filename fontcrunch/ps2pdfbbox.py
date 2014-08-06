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
# A little utility to make pdf files sized to the marking bbox

import os, sys

fni = sys.argv[1]
fno = sys.argv[2]
os.system('gs -dQUIET -dNOPAUSE -dBATCH -sDEVICE=bbox 2>/tmp/foobbox.ps ' + fni)
fi = file(fni)
fo = file('/tmp/foo2.ps', 'w')
fo.write(fi.readline())
for line in file('/tmp/foobbox.ps').readlines():
    fo.write(line)
for line in fi.xreadlines():
    fo.write(line)
fo.close()
os.system('ps2pdf -dEPSCrop /tmp/foo2.ps ' + fno)

