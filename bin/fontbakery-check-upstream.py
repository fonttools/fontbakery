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
from fontbakery import checks
from fontbakery.fbchecklogger import FontBakeryCheckLogger
from fontbakery.targetfont import TargetFont
from fontbakery.upstreamdirectory import UpstreamDirectory


# set up some command line argument processing
description = 'Runs checks or tests on specified upstream folder(s)'
parser = argparse.ArgumentParser(description=description)
parser.add_argument('folders', nargs="+",
                    help="Test folder(s), can be a list")
parser.add_argument('--verbose', '-v', action='count',
                    help="Verbosity level", default=False)


def upstream_checks(config):
    fb = FontBakeryCheckLogger(config)

    # set up a basic logging config
    log_format = '%(levelname)-8s %(message)s'
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if args.verbose == 1:
        logger.setLevel(logging.INFO)
    elif args.verbose >= 2:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.ERROR)

    folders_to_check = []
    for f in config['folders']:
        if os.path.isdir(f):
            folders_to_check.append(f)
        else:
            print("ERROR: '{}' is not a valid existing folder.".format(f))
            continue

    if len(folders_to_check) == 0:
        print("ERROR: None of the specified paths "
              "seem to be existing folders.")
        exit(-1)

    for folder in folders_to_check:
        directory = UpstreamDirectory(folder)
        target = TargetFont()
        target.fullpath = folder

        checks.check_all_fonts_have_matching_glyphnames(fb, folder, directory)
        checks.check_glyphs_have_same_num_of_contours(fb, folder, directory)
        checks.check_glyphs_have_same_num_of_points(fb, folder, directory)
        checks.check_font_folder_contains_a_COPYRIGHT_file(fb, folder)
        checks.check_font_folder_contains_a_DESCRIPTION_file(fb, folder)
        checks.check_font_folder_contains_licensing_files(fb, folder)
        checks.check_font_folder_contains_a_FONTLOG_txt_file(fb, folder)
        checks.check_repository_contains_METADATA_pb_file(fb, f)
        checks.check_copyright_notice_is_consistent_across_family(fb, folder)

        fb.output_report(target)


if __name__ == '__main__':
  args = parser.parse_args()
  upstream_checks(config = {
    'folders': args.folders,
    'verbose': args.verbose,
    'json': True,
    'autofix': False,
    'ghm': False,
    'error': False
  })
