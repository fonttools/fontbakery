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
import argparse
import glob
import logging
import os
import sys
from fontbakery.fbchecklogger import FontBakeryCheckLogger
from fontbakery import checks
from fontTools import ttLib
from fontbakery.utils import (
                             get_bounding_box,
                             get_FamilyProto_Message,
                             font_key,
                             download_family_from_GoogleFontDirectory,
                             download_family_from_GoogleFontDirectory,
                             fonts_from_zip
                             )
cached_font_objects = {}
def ttf_cache(key):
  if key not in cached_font_objects.keys():
    cached_font_objects[key] = ttLib.TTFont(key)

  return cached_font_objects[key]


def fontbakery_check_ttf(config):
  '''Main sequence of checkers & fixers'''
  fb = FontBakeryCheckLogger(config)

  # set up a basic logging config
  handler = logging.StreamHandler()
  formatter = logging.Formatter('%(levelname)-8s %(message)s  ')
  handler.setFormatter(formatter)

  logger = logging.getLogger()
  logger.addHandler(handler)

  if config['verbose'] == 1:
    logger.setLevel(logging.INFO)
  elif config['verbose'] >= 2:
    logger.setLevel(logging.DEBUG)
  else:
    fb.progressbar = True
    logger.setLevel(logging.CRITICAL)

  if config['error']:
    fb.progressbar = False
    logger.setLevel(logging.ERROR)

  # ------------------------------------------------------
  logging.debug("Checking each file is a ttf")
  fonts_to_check = []
  for target in config['files']:
    # use glob.glob to accept *.ttf
    for fullpath in glob.glob(target):
      if fullpath.endswith(".ttf"):
        fonts_to_check.append(fullpath)
      else:
        logging.warning("Skipping '{}' as it does not seem "
                        "to be valid TrueType font file.".format(fullpath))

  if fonts_to_check == []:
    logging.error("CRITICAL ERROR: None of the fonts"
                  " are valid TrueType files!\n"
                  "Aborting.")
    sys.exit(-1)

  print (("Fontbakery will check the following files:\n\t"
          "{}\n\n").format("\n\t".join(fonts_to_check)))

  # This expects all fonts to be in the same folder:
  family_dir = os.path.split(fonts_to_check[0])[0]

  # Perform a few checks on DESCRIPTION files

  descfilepath = os.path.join(family_dir, "DESCRIPTION.en_us.html")
  if os.path.exists(descfilepath):
    fb.default_target = descfilepath
    checks.check_DESCRIPTION_is_propper_HTML_snippet(fb, descfilepath)

# DC This is definitely not step 1, cross-family comes after individual
# in order that individual hotfixes can enable cross-family checks to pass
###########################################################################
## Step 1: Cross-family tests
##         * Validates consistency of data throughout all TTF files
##           in a given family
##         * The list of TTF files in infered from the METADATA.pb file
##         * We avoid testing the same family twice by deduplicating the
##           list of METADATA.pb files first
###########################################################################

  metadata_to_check = []
  for target in fonts_to_check:
    metadata = os.path.join(family_dir, "METADATA.pb")
    if not os.path.exists(metadata):
      logging.error("'{}' is missing"
                    " a METADATA.pb file!".format(target))
    else:
      family = get_FamilyProto_Message(metadata)
      if family is None:
        logging.warning("Could not load data from METADATA.pb.")
      elif family not in metadata_to_check:
        metadata_to_check.append([family_dir, family])

  for dirname, family in metadata_to_check:
    ttf = {}
    for f in family.fonts:
      if font_key(f) in ttf.keys():
        # I think this will likely never happen. But just in case...
        logging.error("This is a fontbakery bug."
                      " We need to figure out a better hash-function"
                      " for the font ProtocolBuffer message."
                      " Please file an issue on"
                      " https://github.com/googlefonts"
                      "/fontbakery/issues/new")
      else:
        ttf[font_key(f)] = ttf_cache(os.path.join(dirname,
                                                  f.filename))

    if dirname == "":
      fb.default_target = "Current Directory"
    else:
      fb.default_target = dirname
    # -----------------------------------------------------
    checks.check_font_designer_field_is_not_unknown(fb, family)

  # FSanches: I don't like the following.
  #           It look very hacky even though it  actually works... :-P
  cross_family = os.path.join(family_dir, "CrossFamilyChecks")
  fb.output_report(cross_family)

  fb.reset_report()

##########################################################################
# Step 2: Single TTF tests
#         * Tests that only check data of each TTF file, but not cross-
#           referencing with other fonts in the family
##########################################################################

  # ------------------------------------------------------
  for target in fonts_to_check:
    font = ttf_cache(target)
    fb.default_target = target
    fb.set_font(font)
    logging.info("OK: {} opened with fontTools".format(target))

    local_styles = {}
    # Determine weight from canonical filename
    file_path, filename = os.path.split(target)
    family, style = os.path.splitext(filename)[0].split('-')
    local_styles[style] = font

    canonical = checks.check_file_is_named_canonically(fb, target)
    if not canonical:
      print("\nAborted all remaining checks for this font "
            "due to its non-canonical filename.")
      fb.output_report(target)
      fb.reset_report()
      continue

    checks.check_post_italicAngle(fb, font, style)

    checks.check_head_macStyle(fb, font, style)

    checks.check_OS2_usWeightClass(fb, font, style)
    checks.check_OS2_fsSelection(fb, font, style)

    # PyFontaine-based glyph coverage checks:
    if config['coverage']:
      checks.check_glyphset_google_cyrillic_historical(fb, target)
      checks.check_glyphset_google_cyrillic_plus(fb, target)
      checks.check_glyphset_google_cyrillic_plus_locl(fb, target)
      checks.check_glyphset_google_cyrillic_pro(fb, target)
      checks.check_glyphset_google_greek_ancient_musical(fb, target)
      checks.check_glyphset_google_greek_archaic(fb, target)
      checks.check_glyphset_google_greek_coptic(fb, target)
      checks.check_glyphset_google_greek_core(fb, target)
      checks.check_glyphset_google_greek_expert(fb, target)
      checks.check_glyphset_google_greek_plus(fb, target)
      checks.check_glyphset_google_greek_pro(fb, target)
      checks.check_glyphset_google_latin_core(fb, target)
      checks.check_glyphset_google_latin_expert(fb, target)
      checks.check_glyphset_google_latin_plus(fb, target)
      checks.check_glyphset_google_latin_plus_optional(fb, target)
      checks.check_glyphset_google_latin_pro(fb, target)
      checks.check_glyphset_google_latin_pro_optional(fb, target)
      checks.check_glyphset_google_arabic(fb, target)
      checks.check_glyphset_google_vietnamese(fb, target)
      checks.check_glyphset_google_extras(fb, target)

##########################################################
## Metadata related checks:
##########################################################
    skip_gfonts = False
    metadata = os.path.join(family_dir, "METADATA.pb")
    if not os.path.exists(metadata):
      logging.warning(("{} is missing a METADATA.pb file!"
                       " This will disable all Google-Fonts-specific checks."
                       " Please considering adding a METADATA.pb file to the"
                       " same folder as the font files.").format(filename))
      skip_gfonts = True
    else:
      family = get_FamilyProto_Message(metadata)
      if family is None:
        logging.warning("Could not load data from METADATA.pb.")
        skip_gfonts = True
        break

      fb.default_target = metadata

      checks.check_METADATA_subsets_alphabetically_ordered(fb,
                                                           metadata,
                                                           family)
      checks.check_Copyright_notice_is_the_same_in_all_fonts(fb, family)
      checks.check_METADATA_family_values_are_all_the_same(fb, family)

      found_regular = checks.check_font_has_regular_style(fb, family)
      checks.check_regular_is_400(fb, family, found_regular)

      for f in family.fonts: # pylint: disable=no-member
                             # (I know this is good, but pylint
                             #  seems confused here)
        if filename == f.filename:
          ###### Here go single-TTF metadata tests #######
          # ----------------------------------------------

          checks.check_font_on_disk_and_METADATA_have_same_family_name(fb,
                                                                       font,
                                                                       f)
          checks.check_METADATA_postScriptName_matches_name_table_value(fb,
                                                                        font,
                                                                        f)
          checks.check_METADATA_fullname_matches_name_table_value(fb,
                                                                  font,
                                                                  f)
          checks.check_METADATA_fonts_name_matches_font_familyname(fb,
                                                                   font,
                                                                   f)
          checks.check_METADATA_fullName_matches_postScriptName(fb, f)
          checks.check_METADATA_filename_matches_postScriptName(fb, f)

          ffname = checks.check_METADATA_name_contains_good_font_name(fb,
                                                                      font,
                                                                      f)
          if ffname is not None:
            checks.check_METADATA_fullname_contains_good_fname(fb, f, ffname)
            checks.check_METADATA_filename_contains_good_fname(fb, f, ffname)
            checks.check_METADATA_postScriptName_contains_good_fname(fb,
                                                                     f,
                                                                     ffname)

          checks.check_Copyright_notice_matches_canonical_pattern(fb, f)
          checks.check_Copyright_notice_does_not_contain_Reserved_Name(fb, f)
          checks.check_Copyright_notice_does_not_exceed_500_chars(fb, f)
          checks.check_Filename_is_set_canonically(fb, f)
          checks.check_METADATA_font_italic_matches_font_internals(fb,
                                                                   font,
                                                                   f)

          if checks.check_METADATA_fontstyle_normal_matches_internals(fb,
                                                                      font,
                                                                      f):
            checks.check_Metadata_keyvalue_match_to_table_name_fields(fb,
                                                                      font,
                                                                      f)

          checks.check_fontname_is_not_camel_cased(fb, f)
          checks.check_font_name_is_the_same_as_family_name(fb, family, f)
          checks.check_font_weight_has_a_canonical_value(fb, f)
          checks.check_METADATA_weigth_matches_OS2_usWeightClass_value(fb, f)
          checks.check_Metadata_weight_matches_postScriptName(fb, f)
          checks.check_METADATA_lists_fonts_named_canonicaly(fb, font, f)
          checks.check_Font_styles_are_named_canonically(fb, font, f)

    # Google-Fonts specific check:
    checks.check_font_em_size_is_ideally_equal_to_1000(fb, font, skip_gfonts)

    # ------------------------------------------------------
    fb.output_report(target)
    fb.reset_report()

    # ----------------------------------------------------
    # https://github.com/googlefonts/fontbakery/issues/971
    # DC: Each fix line should set a fix flag, and
    # if that flag is True by this point, only then write the file
    # and then say any further output regards fixed files, and
    # re-run the script on each fixed file with logging level = error
    # so no info-level log items are shown
    font_file_output = os.path.splitext(filename)[0] + ".fix"
    if config['autofix']:
      font.save(font_file_output)
      logging.info("{} saved\n".format(font_file_output))
    font.close()

    # -------------------------------------------------------
    if not config['verbose'] and \
       not config['json'] and \
       not config['ghm'] and \
       not config['error']:
      # in this specific case, the user would have no way to see
      # the actual check results. So here we inform the user
      # that at least one of these command line parameters
      # needs to be used in order to see the details.
      print ("In order to see the actual check result messages,\n"
             "use one of the following command-line parameters:\n"
             "  --verbose\tOutput results to stdout.\n"
             "  --json \tSave results to a file in JSON format.\n"
             "  --ghm  \tSave results to a file in GitHub Markdown format.\n"
             "  --error\tPrint only the error messages "
             "(outputs to stderr).\n")

  if len(fb.json_report_files) > 0:
    print(("Saved check results in "
           "JSON format to:\n\t{}"
           "").format('\n\t'.join(fb.json_report_files)))
  if len(fb.ghm_report_files) > 0:
    print(("Saved check results in "
           "GitHub Markdown format to:\n\t{}"
           "").format('\n\t'.join(fb.ghm_report_files)))


# set up some command line argument processing
parser = argparse.ArgumentParser(description="Check TTF files"
                                             " for common issues.")
parser.add_argument('arg_filepaths', nargs='+',
                    help='font file path(s) to check.'
                         ' Wildcards like *.ttf are allowed.')
parser.add_argument('-v', '--verbose', action='count', default=0)
parser.add_argument('-e', '--error', action='store_true',
                    help='Output only errors.')
parser.add_argument('-a', '--autofix', action='store_true', default=0)
parser.add_argument('-b', '--burndown', action='store_true', default=0,
                    help='Compute and output burndown-chart'
                         ' stats in JSON format.')
parser.add_argument('-j', '--json', action='store_true',
                    help='Output check results in JSON format.')
parser.add_argument('-m', '--ghm', action='store_true',
                    help='Output check results in GitHub Markdown format.')
pyfontaine_parser = parser.add_mutually_exclusive_group(required=False)
pyfontaine_parser.add_argument('--coverage',
                               help='Run glyph coverage checks'
                                    ' using PyFontaine.',
                               dest='coverage', action='store_true')
pyfontaine_parser.add_argument('--no-coverage',
                               help='Disable all PyFontaine'
                                    ' (glyph coverage) checks.',
                               dest='coverage', action='store_false')
parser.set_defaults(coverage=True)


__author__ = "The Font Bakery Authors"
if __name__ == '__main__':
  args = parser.parse_args()
  fontbakery_check_ttf(config = {
    'files': args.arg_filepaths,
    'autofix': args.autofix,
    'verbose': args.verbose,
    'json': args.json,
    'ghm': args.ghm,
    'error': args.error,
    'burndown': args.burndown,
    'coverage': args.coverage
  })
