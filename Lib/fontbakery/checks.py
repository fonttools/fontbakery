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
from __future__ import print_function
import os
import sys
import tempfile
import logging
import requests
import urllib
import csv
import re
import defusedxml.lxml
from fontTools import ttLib
from unidecode import unidecode
import plistlib
from fontbakery.pifont import PiFont
from fontbakery.utils import (
                             get_name_string,
                             check_bit_entry,
                             ttfauto_fpgm_xheight_rounding,
                             glyphs_surface_area,
                             save_FamilyProto_Message,
                             assertExists
                             )

# =======================================================================
# The following functions implement each of the individual checks per-se.
# =======================================================================

def check_regression_v_number_increased(fb, new_font, old_font, f):
  fb.new_check("117", "Version number has increased since previous release?")
  new_v_number = new_font['head'].fontRevision
  old_v_number = old_font['head'].fontRevision
  if new_v_number < old_v_number:
    fb.error(("Version number %s is less than or equal to"
              " old version %s") % (new_v_number, old_v_number))
  else:
    fb.ok(("Version number %s is greater than"
           " old version %s") % (new_v_number, old_v_number))


def check_regression_glyphs_structure(fb, new_font, old_font, f):
  fb.new_check("118", "Glyphs are similiar to old version")
  bad_glyphs = []
  new_glyphs = glyphs_surface_area(new_font)
  old_glyphs = glyphs_surface_area(old_font)

  shared_glyphs = set(new_glyphs) & set(old_glyphs)

  for glyph in shared_glyphs:
    if abs(int(new_glyphs[glyph]) - int(old_glyphs[glyph])) > 8000:
      bad_glyphs.append(glyph)

  if bad_glyphs:
    fb.error("Following glyphs differ greatly from previous version: [%s]" % (
      ', '.join(bad_glyphs)
    ))
  else:
    fb.ok("Yes, the glyphs are similar "
          "in comparison to the previous version.")


def check_regression_ttfauto_xheight_increase(fb, new_font, old_font, f):
  fb.new_check("119", "TTFAutohint x-height increase value is"
                      " same as previouse release?")
  new_inc_xheight = None
  old_inc_xheight = None

  if 'fpgm' in new_font:
    new_fpgm_tbl = new_font['fpgm'].program.getAssembly()
    new_inc_xheight = ttfauto_fpgm_xheight_rounding(fb,
                                                    new_fpgm_tbl,
                                                    "this fontfile")
  if 'fpgm' in old_font:
    old_fpgm_tbl = old_font['fpgm'].program.getAssembly()
    old_inc_xheight = ttfauto_fpgm_xheight_rounding(fb,
                                                    old_fpgm_tbl,
                                                    "previous release")
  if new_inc_xheight != old_inc_xheight:
    fb.error("TTFAutohint --increase-x-height is %s. "
             "It should match the previous version's value %s" %
             (new_inc_xheight, old_inc_xheight)
             )
  else:
    fb.ok("TTFAutohint --increase-x-height is the same as the previous "
          "release, %s" % (new_inc_xheight))


###############################
# Upstream Font Source checks #
###############################

def check_all_fonts_have_matching_glyphnames(fb, folder, directory):
  fb.new_check(120, "Each font in family has matching glyph names?")
  glyphs = None
  failed = False
  for f in directory.get_fonts():
    try:
      font = PiFont(os.path.join(folder, f))
      if glyphs is None:
        glyphs = font.get_glyphs()
      elif glyphs != font.get_glyphs():
        failed = True
        fb.error(("Font '{}' has different glyphs in"
                  " comparison to onther fonts"
                  " in this family.").format(f))
        break
    except:
      failed = True
      fb.error("Failed to load font file: '{}'".format(f))

  if failed is False:
    fb.ok("All fonts in family have matching glyph names.")


def check_glyphs_have_same_num_of_contours(fb, folder, directory):
  fb.new_check("121", "Glyphs have same number of contours across family ?")
  glyphs = {}
  failed = False
  for f in directory.get_fonts():
    font = PiFont(os.path.join(folder, f))
    for glyphcode, glyphname in font.get_glyphs():
      contours = font.get_contours_count(glyphname)
      if glyphcode in glyphs and glyphs[glyphcode] != contours:
        failed = True
        fb.error(("Number of contours of glyph '{}'"
                  " does not match."
                  " Expected {} contours, but actual is"
                  " {} contours").format(glyphname,
                                         glyphs[glyphcode],
                                         contours))
      glyphs[glyphcode] = contours
  if failed is False:
    fb.ok("Glyphs have same number of contours across family.")


def check_glyphs_have_same_num_of_points(fb, folder, directory):
  fb.new_check("122", "Glyphs have same number of points across family ?")
  glyphs = {}
  failed = False
  for f in directory.get_fonts():
    font = PiFont(os.path.join(folder, f))
    for g, glyphname in font.get_glyphs():
      points = font.get_points_count(glyphname)
      if g in glyphs and glyphs[g] != points:
        failed = True
        fb.error(("Number of points of glyph '{}' does not match."
                  " Expected {} points, but actual is"
                  " {} points").format(glyphname,
                                       glyphs[g],
                                       points))
      glyphs[g] = points
  if failed is False:
    fb.ok("Glyphs have same number of points across family.")


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
