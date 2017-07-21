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
import os
import re
from fontbakery.pifont import PiFont
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


def check_copyright_notice_is_consistent_across_family(fb, folder):
  fb.new_check("128", "Copyright notice is consistent"
                      " across all fonts in this family ?")

  COPYRIGHT_REGEX = re.compile(r'Copyright.*?20\d{2}.*', re.U | re.I)

  def grep_copyright_notice(contents):
    match = COPYRIGHT_REGEX.search(contents)
    if match:
      return match.group(0).strip(',\r\n')
    return

  def lookup_copyright_notice(ufo_folder):
    # current_path = ufo_folder
    try:
      contents = open(os.path.join(ufo_folder,
                                   'fontinfo.plist')).read()
      copyright = grep_copyright_notice(contents)
      if copyright:
        return copyright
    except (IOError, OSError):
      pass

    # TODO: FIX-ME!
    # I'm not sure what's going on here:
    # "?" was originaly "self.operator.path" in the old codebase:
#    while os.path.realpath(?) != current_path:
#      # look for all text files inside folder
#      # read contents from them and compare with copyright notice pattern
#      files = glob.glob(os.path.join(current_path, '*.txt'))
#      files += glob.glob(os.path.join(current_path, '*.ttx'))
#      for filename in files:
#        with open(os.path.join(current_path, filename)) as fp:
#          match = COPYRIGHT_REGEX.search(fp.read())
#          if not match:
#            continue
#          return match.group(0).strip(',\r\n')
#      current_path = os.path.join(current_path, '..')  # go up
#      current_path = os.path.realpath(current_path)
    return

  ufo_dirs = []
  for item in os.walk(folder):
    root = item[0]
    dirs = item[1]
    # files = item[2]
    for d in dirs:
        fullpath = os.path.join(root, d)
        if os.path.splitext(fullpath)[1].lower() == '.ufo':
            ufo_dirs.append(fullpath)
  if len(ufo_dirs) == 0:
    fb.skip("No UFO font file found.")
  else:
    failed = False
    copyright = None
    for ufo_folder in ufo_dirs:
      current_notice = lookup_copyright_notice(ufo_folder)
      if current_notice is None:
        continue
      if copyright is not None and current_notice != copyright:
        failed = True
        fb.error('"{}" != "{}"'.format(current_notice,
                                       copyright))
        break
      copyright = current_notice
    if failed is False:
      fb.ok("Copyright notice is consistent across all fonts in this family.")
