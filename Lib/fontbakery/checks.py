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
from fontbakery.utils import assertExists

###############################
# Upstream Font Source checks #
###############################

def check_font_folder_contains_a_COPYRIGHT_file(fb, folder):
  fb.new_check("123", "Does this font folder contain COPYRIGHT file ?")
  assertExists(fb, folder, "COPYRIGHT.txt",
               "Font folder lacks a copyright file at '{}'",
               "Font folder contains COPYRIGHT.txt")


def check_font_folder_contains_a_DESCRIPTION_file(fb, folder):
  fb.new_check("124", "Does this font folder contain a DESCRIPTION file ?")
  assertExists(fb, folder, "DESCRIPTION.en_us.html",
               "Font folder lacks a description file at '{}'",
               "Font folder should contain DESCRIPTION.en_us.html.")


def check_font_folder_contains_licensing_files(fb, folder):
  fb.new_check("125", "Does this font folder contain licensing files?")
  assertExists(fb, folder, ["LICENSE.txt", "OFL.txt"],
               "Font folder lacks licensing files at '{}'",
               "Font folder should contain licensing files.")


def check_font_folder_contains_a_FONTLOG_txt_file(fb, folder):
  fb.new_check("126", "Font folder should contain FONTLOG.txt")
  assertExists(fb, folder, "FONTLOG.txt",
               "Font folder lacks a fontlog file at '{}'",
               "Font folder should contain a 'FONTLOG.txt' file.")
