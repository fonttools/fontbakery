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
import logging
import os
from fontbakery.targetfont import TargetFont
from fontbakery.fbchecklogger import FontBakeryCheckLogger
from fontbakery import checks

# set up some command line argument processing
description = 'Runs checks on specified DESCRIPTION file(s)'
parser = argparse.ArgumentParser(description=description)
parser.add_argument('arg_filepaths', nargs="+", help="Test files,"
                                                     " can be a list")
parser.add_argument('--verbose', '-v', action='count',
                    help="Verbosity level", default=False)


def description_checks(config):
  fb = FontBakeryCheckLogger(config)

  # set up a basic logging config
  logger = logging.getLogger()
  if args.verbose == 1:
    logger.setLevel(logging.INFO)
  elif args.verbose >= 2:
    logger.setLevel(logging.DEBUG)
  else:
    logger.setLevel(logging.ERROR)

  files_to_check = []
  for f in config['files']:
    if os.path.basename(f).startswith('DESCRIPTION.'):
      files_to_check.append(f)
    else:
      print("ERROR: '{}' is not a DESCRIPTION file.".format(f))
      continue

  if len(files_to_check) == 0:
    print("ERROR: None of the specified files "
          "seem to be valid DESCRIPTION files.")
    exit(-1)

  for f in files_to_check:
    try:
      contents = open(f).read()
    except:
      print("ERROR: File '{}' does not exist.".format(f))
      continue
    target = TargetFont()
    target.fullpath = f

    checks.check_DESCRIPTION_file_contains_no_broken_links(fb, contents)
    checks.check_DESCRIPTION_is_propper_HTML_snippet(fb, f)
    checks.check_DESCRIPTION_min_length(fb, f)
    checks.check_DESCRIPTION_max_length(fb, f)
    fb.output_report(target)


if __name__ == '__main__':
  args = parser.parse_args()
  description_checks(config = {
    'files': args.arg_filepaths,
    'verbose': args.verbose,
    'json': True,
    'autofix': False,
    'ghm': False,
    'error': False
  })
