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
    if args.progress:
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
      if not os.path.exists(os.path.join(dirname, f.filename)):
        logging.warning(("METADATA.pb references a TTF file"
                         " that is missing: "
                         "'{}'").format(os.path.join(dirname, f.filename)))
        continue

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

  # ------------------------------------------------------
  vmetrics_ymin = 0
  vmetrics_ymax = 0
  for target in fonts_to_check:
    font = ttf_cache(target)

    font_ymin, font_ymax = get_bounding_box(font)
    vmetrics_ymin = min(font_ymin, vmetrics_ymin)
    vmetrics_ymax = max(font_ymax, vmetrics_ymax)

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
    checks.check_OS2_usWinAscent_and_Descent(fb, vmetrics_ymin, vmetrics_ymax)
    checks.check_OS2_Metrics_match_hhea_Metrics(fb, font)

    checks.check_with_ftxvalidator(fb, target)
    checks.check_with_msfontvalidator(fb, target)
    checks.check_with_otsanitise(fb, target)

    validation_state = checks.check_fforge_outputs_error_msgs(fb, target)
    if validation_state is not None:
      checks.perform_all_fontforge_checks(fb, validation_state)


    checks.check_Vertical_Metric_Linegaps(fb, font)
    checks.check_unitsPerEm_value_is_reasonable(fb, font)
    checks.check_font_version_fields(fb, font)
    checks.check_Digital_Signature_exists(fb, font, target)
    checks.check_font_contains_the_first_few_mandatory_glyphs(fb, font)

    missing = checks.check_font_contains_glyphs_for_whitespace_chars(fb, font)
    checks.check_font_has_proper_whitespace_glyph_names(fb, font, missing)
    checks.check_whitespace_glyphs_have_ink(fb, font, missing)
    checks.check_whitespace_glyphs_have_coherent_widths(fb, font, missing)

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

    checks.check_no_problematic_formats(fb, font)
    checks.check_for_unwanted_tables(fb, font)

    ttfautohint_missing = checks.check_hinting_filesize_impact(fb,
                                                               target,
                                                               filename)
    checks.check_version_format_is_correct_in_NAME_table(fb, font)
    checks.check_font_has_latest_ttfautohint_applied(fb,
                                                     font,
                                                     ttfautohint_missing)
    checks.check_name_table_entries_do_not_contain_linebreaks(fb, font)
    checks.check_glyph_names_are_all_valid(fb, font)
    checks.check_font_has_unique_glyph_names(fb, font)
    checks.check_no_glyph_is_incorrectly_named(fb, font)
    checks.check_EPAR_table_is_present(fb, font)
    checks.check_GASP_table_is_correctly_set(fb, font)

    has_kerning_info = checks.check_GPOS_table_has_kerning_info(fb, font)
    checks.check_nonligated_sequences_kerning_info(fb, font, has_kerning_info)
    checks.check_all_ligatures_have_corresponding_caret_positions(fb, font)
    checks.check_there_is_no_KERN_table_in_the_font(fb, font)
    checks.check_familyname_does_not_begin_with_a_digit(fb, font)
    checks.check_fullfontname_begins_with_the_font_familyname(fb, font)
    checks.check_unused_data_at_the_end_of_glyf_table(fb, font)
    checks.check_font_has_EURO_SIGN_character(fb, font)
    checks.check_font_follows_the_family_naming_recommendations(fb, font)
    checks.check_font_enables_smart_dropout_control(fb, font)
    checks.check_MaxAdvanceWidth_is_consistent_with_Hmtx_and_Hhea_tables(fb,
                                                                         font)
    checks.check_non_ASCII_chars_in_ASCII_only_NAME_table_entries(fb, font)

    checks.check_for_points_out_of_bounds(fb, font)
    checks.check_glyphs_have_unique_unicode_codepoints(fb, font)
    checks.check_all_glyphs_have_codepoints_assigned(fb, font)
    checks.check_that_glyph_names_do_not_exceed_max_length(fb, font)

##########################################################
## Metadata related checks:
##########################################################
    skip_gfonts = False
    is_listed_in_GFD = False
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

      checks.check_METADATA_Ensure_all_TTF_references_are_valid(fb, family)
      checks.check_METADATA_Ensure_designer_simple_short_name(fb, family)
      is_listed_in_GFD = checks.check_family_is_listed_in_GFDirectory(fb,
                                                                        family)
      checks.check_METADATA_Designer_exists_in_GWF_profiles_csv(fb, family)
      checks.check_METADATA_has_unique_full_name_values(fb, family)
      checks.check_METADATA_check_style_weight_pairs_are_unique(fb, family)
      checks.check_METADATA_license_is_APACHE2_UFL_or_OFL(fb, family)
      checks.check_METADATA_contains_at_least_menu_and_latin_subsets(fb,
                                                                     family)
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


##########################################################
## Step 3: Regression related checks:
# if family already exists on fonts.google.com
##########################################################

    # ------------------------------------------------------
    if is_listed_in_GFD:
      remote_fonts_zip = download_family_from_GoogleFontDirectory(family.name) # pylint: disable=no-member
      remote_fonts_to_check = fonts_from_zip(remote_fonts_zip)

      remote_styles = {}
      for remote_filename, remote_font in remote_fonts_to_check:
        fb.default_target = "GF:" + remote_filename
	if '-' in remote_filename[:-4]:
          remote_style = remote_filename[:-4].split('-')[1]
        else:
          # This is a non-canonical filename!
          remote_style = "Regular" #  But I'm giving it a chance here... :-)
        remote_styles[remote_style] = remote_font

        # Only perform tests if local fonts have the same styles
        if remote_style in local_styles:
          checks.check_regression_v_number_increased(
            fb,
            local_styles[style],
            remote_styles[style],
            f
          )
          checks.check_regression_glyphs_structure(
            fb,
            local_styles[style],
            remote_styles[style],
            f
          )
          checks.check_regression_ttfauto_xheight_increase(
            fb,
            local_styles[style],
            remote_styles[style],
            f
          )

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
parser.add_argument('-n', '--no-progress', action='store_false',
                    dest='progress',
                    help='Disables the display of a progress bar.')
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
