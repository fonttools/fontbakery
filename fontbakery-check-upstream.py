#!/usr/bin/env python
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
import argparse
import defusedxml.lxml
import glob
import logging
import os
import re

# =====================================
# Helper logging class
#TODO: This code is copied from fontbakery-check-ttf.py
#TODO: Deduplicate it by placing it in a shared external file.


class FontBakeryCheckLogger():
  all_checks = []
  current_check = None

  def save_json_report(self, filename="fontbakery-check-results.json"):
    import json
    self.flush()
    json_data = json.dumps(self.all_checks,
                           sort_keys=True,
                           indent=4,
                           separators=(',', ': '))
    open(filename, 'w').write(json_data)
    logging.debug(("Saved check results in "
                   "JSON format to '{}'").format(filename))

  def flush(self):
    if self.current_check is not None:
      self.all_checks.append(self.current_check)

  def new_check(self, desc):
    self.flush()
    logging.debug("Check #{}: {}".format(len(self.all_checks) + 1, desc))
    self.current_check = {"description": desc,
                          "log_messages": [],
                          "result": "unknown"}

  def skip(self, msg):
    logging.info("SKIP: " + msg)
    self.current_check["log_messages"].append(msg)
    self.current_check["result"] = "SKIP"

  def ok(self, msg):
    logging.info("OK: " + msg)
    self.current_check["log_messages"].append(msg)
    if self.current_check["result"] != "FAIL":
      self.current_check["result"] = "OK"

  def warning(self, msg):
    logging.warning(msg)
    self.current_check["log_messages"].append("Warning: " + msg)
    if self.current_check["result"] == "unknown":
      self.current_check["result"] = "WARNING"

  def error(self, msg):
    logging.error(msg)
    self.current_check["log_messages"].append("ERROR: " + msg)
    self.current_check["result"] = "ERROR"

  def hotfix(self, msg):
    logging.info('HOTFIXED: ' + msg)
    self.current_check['log_messages'].append('HOTFIX: ' + msg)
    self.current_check['result'] = "HOTFIX"

fb = FontBakeryCheckLogger()

def upstream_checks():
    # set up some command line argument processing
    description = 'Runs checks or tests on specified upstream folder(s)'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('folders', nargs="+", help="Test folder(s), can be a list")
    parser.add_argument('--verbose', '-v', action='count',
                        help="Verbosity level", default=False)
    args = parser.parse_args()

    # set up a basic logging config
    logger = logging.getLogger()
    if args.verbose == 1:
        logger.setLevel(logging.INFO)
    elif args.verbose >= 2:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.ERROR)

    folders_to_check = []
    for f in args.folders:
        if os.path.isdir(f):
            folders_to_check.append(f)
        else:
            fb.error("'{}' is not a valid existing folder.".format(f))
            continue

    if len(folders_to_check) == 0:
        fb.error("None of the specified paths "
                 "seem to be existing folders.")
        exit(-1)

    for f in folders_to_check:

# ---------------------------------------------------------------------
#        fb.new_check("Each font in family has matching glyph names?")
#        directory = UpstreamDirectory(f)
#        # TODO does this glyphs list object get populated?
#        glyphs = []
#        for f in directory.get_fonts():
#            font = PiFont(os.path.join(self.operator.path, f))
#            glyphs_ = font.get_glyphs()
#
#            if glyphs and glyphs != glyphs_:
#                # TODO report which font
#                self.fail('Family has different glyphs across fonts')

# ---------------------------------------------------------------------
#        fb.new_check("Check that glyphs has same number of contours across family")
#        directory = UpstreamDirectory(f)
#
#        glyphs = {}
#        for f in directory.get_fonts():
#            font = PiFont(os.path.join(self.operator.path, f))
#            glyphs_ = font.get_glyphs()
#
#            for glyphcode, glyphname in glyphs_:
#                contours = font.get_contours_count(glyphname)
#                if glyphcode in glyphs and glyphs[glyphcode] != contours:
#                    msg = ('Number of contours of glyph "%s" does not match.'
#                           ' Expected %s contours, but actual is %s contours')
#                    self.fail(msg % (glyphname, glyphs[glyphcode], contours))
#                glyphs[glyphcode] = contours

# ---------------------------------------------------------------------
#        fb.new_check("Check that glyphs has same number of points across family")
#        directory = UpstreamDirectory(f)
#
#        glyphs = {}
#        for f in directory.get_fonts():
#            font = PiFont(os.path.join(self.operator.path, f))
#            glyphs_ = font.get_glyphs()
#
#            for g, glyphname in glyphs_:
#                points = font.get_points_count(glyphname)
#                if g in glyphs and glyphs[g] != points:
#                    msg = ('Number of points of glyph "%s" does not match.'
#                           ' Expected %s points, but actual is %s points')
#                    self.fail(msg % (glyphname, glyphs[g], points))
#                glyphs[g] = points

# ======================================================================
        def assertExists(folderpath, filenames, err_msg, ok_msg):
            if not isinstance(filenames, list):
                filenames = [filenames]

            missing = []
            for filename in filenames:
                fullpath = os.path.join(folderpath, filename)
                if os.path.exists(fullpath):
                    missing.append(fullpath)
            if len(missing) > 0:
                fb.error(err_msg.format(", ".join(missing)))
            else:
                fb.ok(ok_msg)

# ---------------------------------------------------------------------
        fb.new_check("Does this font folder contain COPYRIGHT file ?")
        assertExists(f, "COPYRIGHT.txt",
                        "Font folder lacks a copyright file at '{}'",
                        "Font folder contains COPYRIGHT.txt")

# ---------------------------------------------------------------------
        fb.new_check("Does this font folder contain a DESCRIPTION file ?")
        assertExists(f, "DESCRIPTION.en_us.html",
                        "Font folder lacks a description file at '{}'",
                        "Font folder should contain DESCRIPTION.en_us.html.")

# ---------------------------------------------------------------------
        fb.new_check("Does this font folder contain licensing files?")
        assertExists(f, ["LICENSE.txt", "OFL.txt"],
                        "Font folder lacks licencing files at '{}'",
                        "Font folder should contain licensing files.")

# ---------------------------------------------------------------------
        fb.new_check("Font folder should contain FONTLOG.txt")
        assertExists(f, "FONTLOG.txt",
                        "Font folder lacks a fontlog file at '{}'",
                        "Font folder should contain a 'FONTLOG.txt' file.")

# =======================================================================
# Tests for common upstream repository files.
# note:
# This test case is not related to font processing. It makes only common
# checks like one - test that upstream repository contains METADATA.pb)
# =======================================================================

# ---------------------------------------------------------------------
        fb.new_check("Repository contains METADATA.pb file?")
        fullpath = os.path.join(f, 'METADATA.pb')
        if not os.path.exists(fullpath):
            fb.error("File 'METADATA.pb' does not exist"
                     " in root of upstream repository")
        else:
            fb.ok("Repository contains METADATA.pb file.")

# ---------------------------------------------------------------------
#        fb.new_check("Copyright notice consistent "
#                     "across all fonts in this family?")
#        ufo_dirs = []
#        for root, dirs, files in os.walk(self.operator.path):
#            for d in dirs:
#                fullpath = os.path.join(root, d)
#                if os.path.splitext(fullpath)[1].lower() == '.ufo':
#                    ufo_dirs.append(fullpath)
#
#        copyright = None
#        for ufo_folder in ufo_dirs:
#            current_notice = self.lookup_copyright_notice(ufo_folder)
#            if current_notice is None:
#                continue
#            if copyright is not None and current_notice != copyright:
#                self.fail('"%s" != "%s"' % (current_notice, copyright))
#                break
#            copyright = current_notice
#
#        COPYRIGHT_REGEX = re.compile(r'Copyright.*?20\d{2}.*', re.U | re.I)
#        def grep_copyright_notice(self, contents):
#            match = COPYRIGHT_REGEX.search(contents)
#            if match:
#                return match.group(0).strip(',\r\n')
#            return
#
#        def lookup_copyright_notice(self, ufo_folder):
#            current_path = ufo_folder
#            try:
#                contents = open(os.path.join(ufo_folder, 'fontinfo.plist')).read()
#                copyright = self.grep_copyright_notice(contents)
#                if copyright:
#                    return copyright
#            except (IOError, OSError):
#                pass
#
#            while os.path.realpath(self.operator.path) != current_path:
#                # look for all text files inside folder
#                # read contents from them and compare with copyright notice
#                # pattern
#                files = glob.glob(os.path.join(current_path, '*.txt'))
#                files += glob.glob(os.path.join(current_path, '*.ttx'))
#                for filename in files:
#                    with open(os.path.join(current_path, filename)) as fp:
#                        match = COPYRIGHT_REGEX.search(fp.read())
#                        if not match:
#                           continue
#                        return match.group(0).strip(',\r\n')
#                current_path = os.path.join(current_path, '..')  # go up
#                current_path = os.path.realpath(current_path)
#            return

        fb.save_json_report("fontbakery-check-upstream-results.json")

if __name__ == '__main__':
    upstream_checks()






