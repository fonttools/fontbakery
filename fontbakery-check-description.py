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
from __future__ import print_function
import argparse
import defusedxml.lxml
import logging
import magic
import os
import requests
import sys
import unittest
from lxml.html import HTMLParser

# =====================================
# Helper logging class
#TODO: This code is copied from fontbakery-check-ttf.py
#TODO: Deduplicate it by placing it in a shared external file.


class FontBakeryCheckLogger():
  all_checks = []
  current_check = None

  def save_json_report(self, filename="fontbakery-check-description-results.json"):
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

def description_checks():
    # set up some command line argument processing
    description = 'Runs checks or tests on specified DESCRIPTION.txt file(s)'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('file', nargs="+", help="Test files, can be a list")
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

    files_to_check = []
    for f in args.file:
        if os.path.basename(f).startswith('DESCRIPTION.'):
            files_to_check.append(f)
        else:
            fb.error("'{}' is not a DESCRIPTION file.".format(f))
            continue

    if len(files_to_check) == 0:
        fb.error("None of the specified files "
                 "seem to be valid DESCRIPTION files.")
        exit(-1)

    for f in files_to_check:
        try:
            contents = open(f).read()
        except:
            fb.error("File '{}' does not exist.".format(f))
            continue

# ---------------------------------------------------------------------
        fb.new_check("Does DESCRIPTION file contain broken links ?")
        doc = defusedxml.lxml.fromstring(contents, parser=HTMLParser())
        broken_links = []
        for link in doc.xpath('//a/@href'):
            try:
                response = requests.head(link)
                if response.status_code != requests.codes.ok:
                    broken_links.append(link)
            except requests.exceptions.RequestException:
                broken_links.append(link)

        if len(broken_links) > 0:
            fb.error(("The following links are broken"
                      " in the DESCRIPTION file:"
                      " '{}'").format("', '".join(broken_links)))
        else:
            fb.ok("All links in the DESCRIPTION file look good!")

# ---------------------------------------------------------------------
        fb.new_check("Is this a propper HTML file")
        if magic.from_file(f, mime=True) != 'text/html':
            fb.error("{} is not a propper HTML file.".format(f))
        else:
            fb.ok("{} is a propper HTML file.".format(f))

# ---------------------------------------------------------------------
        fb.new_check("DESCRIPTION.en_us.html is more than 500 bytes")
        statinfo = os.stat(f)
        if statinfo.st_size < 500:
            fb.error("{} must have size larger than 500 bytes".format(f))
        else:
            fb.ok("{} is larger than 500 bytes".format(f))

# ---------------------------------------------------------------------
        fb.save_json_report()

if __name__ == '__main__':
    description_checks()
