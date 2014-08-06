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
# offset curve of piecewise cornu curves

from math import *

import pcorn
from clothoid import mod_2pi

def seg_offset(seg, d):
    th0 = seg.th(0)
    th1 = seg.th(seg.arclen)
    z0 = [seg.z0[0] + d * sin(th0), seg.z0[1] - d * cos(th0)]
    z1 = [seg.z1[0] + d * sin(th1), seg.z1[1] - d * cos(th1)]
    chth = atan2(z1[1] - z0[1], z1[0] - z0[0])
    return [pcorn.Segment(z0, z1, mod_2pi(chth - th0), mod_2pi(th1 - chth))]


def offset(curve, d):
    segs = []
    for seg in curve.segs:
        segs.extend(seg_offset(seg, d))
    return pcorn.Curve(segs)
