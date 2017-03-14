#!/usr/bin/env python2
# Copyright 2016 The Fontbakery Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from fontTools import ttLib

class TargetFont(object):
  def __init__(self, ttfont=None, desc={}):
    self.ttfont = ttfont
    self.set_description(desc)

  def set_description(self, desc):
    '''NOTE:
       The JSON description format is a dictionary with the following fields:
        -> filename
        -> familyName
        -> weightName
        -> isItalic
        -> version
        -> vendorID'''
    self.fullpath = desc.get("filename")
    self.familyName = desc.get("familyName")
    self.weightName = desc.get("weightName")
    self.isItalic = desc.get("isItalic")
    self.version = desc.get("version")
    self.vendorID = desc.get("vendorID")

  def get_ttfont(self):
    if self.ttfont is None:
      self.ttfont = ttLib.TTFont(self.fullpath)
    return self.ttfont
