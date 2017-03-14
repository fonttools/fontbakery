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
from FontBakeryCheckLogger import FontBakeryCheckLogger
from TargetFont import TargetFont
import fontbakery_checks as checks
from fontTools import ttLib
from utils import get_bounding_box,\
                  fetch_vendorID_list,\
                  get_FamilyProto_Message,\
                  font_key,\
                  download_family_from_GoogleFontDirectory,\
                  fonts_from_zip


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
    if type(target) is TargetFont:
      fonts_to_check.append(target)
    else:
      # use glob.glob to accept *.ttf
      for fullpath in glob.glob(target):
        file_path, file_name = os.path.split(fullpath)
        if file_name.endswith(".ttf"):
          a_target = TargetFont()
          a_target.fullpath = fullpath
          fonts_to_check.append(a_target)
        else:
          logging.warning("Skipping '{}' as it does not seem "
                          "to be valid TrueType font file.".format(file_name))

# FIX-ME: Why do we attempt to sort the fonts here?
#         Do we expect to remove duplicates? It does not seem very important.
#         Anyway... this probably need some extra work to get the
#         font objects sorted by filename field...
  fonts_to_check.sort()

  if fonts_to_check == []:
    logging.error("None of the fonts are valid TrueType files!")

  checks.check_files_are_named_canonically(fb, fonts_to_check)

  if fb.config['webapp'] is True:
    # At the moment we won't perform
    # DESCRIPTION checks on the webapp
    # In particular, one of the checks depends on the magic python module
    # which is not supported on Google App Engine.
    pass
  else:
    # Perform a few checks on DESCRIPTION files

    # This expects all fonts to be in the same folder:
    a_font = fonts_to_check[0]

    # FIX-ME: This will not work if we have more than
    #         a single '/' char in the filename:
    folder_name = os.path.split(a_font.fullpath)[0]
    descfilepath = os.path.join(folder_name, "DESCRIPTION.en_us.html")
    if os.path.exists(descfilepath):
      fb.default_target = descfilepath
      contents = open(descfilepath).read()
      checks.check_DESCRIPTION_file_contains_broken_links(fb, contents)
      checks.check_DESCRIPTION_is_propper_HTML_snippet(fb, descfilepath)
      checks.check_DESCRIPTION_max_length(fb, descfilepath)
      checks.check_DESCRIPTION_min_length(fb, descfilepath)

  if not fb.config['inmem']:
    # this check does not make sense for in-memory file-like objects:
    checks.check_all_files_in_a_single_directory(fb, fonts_to_check)

  registered_vendor_ids = fetch_vendorID_list(logging)

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

  if fb.config['inmem'] or fb.config['webapp']:
    # TODO: Not sure why these are disabled. I need to review this.
    pass
  else:
    metadata_to_check = []
    for target in fonts_to_check:
      fontdir = os.path.dirname(target.fullpath)
      metadata = os.path.join(fontdir, "METADATA.pb")
      if not os.path.exists(metadata):
        logging.error("'{}' is missing"
                      " a METADATA.pb file!".format(target.fullpath))
      else:
        family = get_FamilyProto_Message(metadata)
        if family is None:
          logging.warning("Could not load data from METADATA.pb.")
        elif family not in metadata_to_check:
          metadata_to_check.append([fontdir, family])

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
          ttf[font_key(f)] = ttLib.TTFont(os.path.join(dirname,
                                                       f.filename))

      if dirname == "":
        fb.default_target = "Current Folder"
      else:
        fb.default_target = dirname
      # -----------------------------------------------------
      checks.check_font_designer_field_is_not_unknown(fb, family)
      checks.check_fonts_have_consistent_underline_thickness(fb, family, ttf)
      checks.check_fonts_have_consistent_PANOSE_proportion(fb, family, ttf)
      checks.check_fonts_have_consistent_PANOSE_family_type(fb, family, ttf)
      checks.check_fonts_have_equal_numbers_of_glyphs(fb, family, ttf)
      checks.check_fonts_have_equal_glyph_names(fb, family, ttf)
      checks.check_fonts_have_equal_unicode_encodings(fb, family, ttf)

  # ------------------------------------------------------
  vmetrics_ymin = 0
  vmetrics_ymax = 0
  for target in fonts_to_check:
    # this will both accept BytesIO or a filepath
    font = target.get_ttfont()

    font_ymin, font_ymax = get_bounding_box(font)
    vmetrics_ymin = min(font_ymin, vmetrics_ymin)
    vmetrics_ymax = max(font_ymax, vmetrics_ymax)

  checks.check_all_fontfiles_have_same_version(fb, fonts_to_check)
  # FSanches: I don't like the following few lines.
  #           They look very hacky even though they actually work... :-P
  a_font = fonts_to_check[0]
  family_dir = os.path.split(a_font.fullpath)[0]
  cross_family = os.path.join(family_dir, "CrossFamilyChecks")
  fb.output_report(TargetFont(desc={"filename": cross_family}))
  fb.reset_report()

##########################################################################
# Step 2: Single TTF tests
#         * Tests that only check data of each TTF file, but not cross-
#           referencing with other fonts in the family
##########################################################################

  # ------------------------------------------------------
  for target in fonts_to_check:
    font = target.get_ttfont()
    fb.default_target = target.fullpath
    fb.set_font(font)
    logging.info("OK: {} opened with fontTools".format(target.fullpath))

    local_styles = {}
    # Determine weight from canonical filename
    file_path, filename = os.path.split(target.fullpath)
    family, style = os.path.splitext(filename)[0].split('-')
    local_styles[style] = font

    checks.check_font_has_post_table_version_2(fb, font)
    checks.check_OS2_fsType(fb)
    checks.check_main_entries_in_the_name_table(fb, font, target.fullpath)
    checks.check_OS2_achVendID(fb, font, registered_vendor_ids)
    checks.check_name_entries_symbol_substitutions(fb, font)
    checks.check_OS2_usWeightClass(fb, font, style)
    checks.check_fsSelection_REGULAR_bit(fb, font, style)
    checks.check_italicAngle_value_is_negative(fb, font)
    checks.check_italicAngle_value_is_less_than_20_degrees(fb, font)
    checks.check_italicAngle_matches_font_style(fb, font, style)
    checks.check_fsSelection_ITALIC_bit(fb, font, style)
    checks.check_macStyle_ITALIC_bit(fb, font, style)
    checks.check_fsSelection_BOLD_bit(fb, font, style)
    checks.check_macStyle_BOLD_bit(fb, font, style)

    found = checks.check_font_has_a_license(fb, file_path)
    checks.check_copyright_entries_match_license(fb, found, file_path, font)
    checks.check_font_has_a_valid_license_url(fb, found, font)
    checks.check_description_strings_in_name_table(fb, font)
    checks.check_description_strings_do_not_exceed_100_chars(fb, font)

    monospace_detected = checks.check_font_is_truly_monospaced(fb, font)
    checks.check_if_xAvgCharWidth_is_correct(fb, font)
    checks.check_with_ftxvalidator(fb, target.fullpath)
    checks.check_with_msfontvalidator(fb, target.fullpath)
    checks.check_with_otsanitise(fb, target.fullpath)

    validation_state = checks.check_fforge_outputs_error_msgs(fb,
                                                              target.fullpath)
    if validation_state is not None:
      checks.perform_all_fontforge_checks(fb, validation_state)

    checks.check_OS2_usWinAscent_and_Descent(fb, vmetrics_ymin, vmetrics_ymax)
    checks.check_Vertical_Metric_Linegaps(fb, font)
    checks.check_OS2_Metrics_match_hhea_Metrics(fb, font)
    checks.check_unitsPerEm_value_is_reasonable(fb, font)
    checks.check_font_version_fields(fb, font)
    checks.check_Digital_Signature_exists(fb, font, target.fullpath)
    checks.check_font_contains_the_first_few_mandatory_glyphs(fb, font)

    missing = checks.check_font_contains_glyphs_for_whitespace_chars(fb, font)
    checks.check_font_has_proper_whitespace_glyph_names(fb, font, missing)
    checks.check_whitespace_glyphs_have_ink(fb, font, missing)
    checks.check_whitespace_glyphs_have_coherent_widths(fb, font, missing)
    checks.check_with_pyfontaine(fb, target.fullpath)
    checks.check_no_problematic_formats(fb, font)
    checks.check_for_unwanted_tables(fb, font)

    ttfautohint_missing = checks.check_hinting_filesize_impact(fb,
                                                               target.fullpath,
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
    checks.check_hhea_table_and_advanceWidth_values(fb,
                                                    font,
                                                    monospace_detected)

##########################################################
## Metadata related checks:
##########################################################
    skip_gfonts = False
    is_listed_in_GFD = False
    if not fb.config['webapp']:
      fontdir = os.path.dirname(target.fullpath)
      metadata = os.path.join(fontdir, "METADATA.pb")
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

        found_regular = checks.check_font_has_Regular_style(fb, family)
        checks.check_Regular_is_400(fb, family, found_regular)

        for f in family.fonts:
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
      remote_fonts_zip = download_family_from_GoogleFontDirectory(family.name)
      remote_fonts_to_check = fonts_from_zip(remote_fonts_zip)

      remote_styles = {}
      for target in remote_fonts_to_check:
        fb.default_target = target.fullpath
        remote_font = target.get_ttfont()
        remote_family, remote_style = target.fullpath[:-4].split('-')
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

    if not fb.config['webapp']:
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

  if fb.config['webapp']:
    return fb.json_report_files
  else:
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
                    help='Output only errors')
parser.add_argument('-a', '--autofix', action='store_true', default=0)
parser.add_argument('-j', '--json', action='store_true',
                    help='Output check results in JSON format')
parser.add_argument('-m', '--ghm', action='store_true',
                    help='Output check results in GitHub Markdown format')

__author__ = "The Font Bakery Authors"
if __name__ == '__main__':
  args = parser.parse_args()
  config = {
    'files': args.arg_filepaths,
    'autofix': args.autofix,
    'verbose': args.verbose,
    'json': args.json,
    'ghm': args.ghm,
    'error': args.error,
    'inmem': False,
    'webapp': False
  }
  # Notes on the meaning of some of the configuration parameters:
  #
  # inmem:  Indicated that results should be saved in-memory
  #         instead of written to the filesystem.
  #         This may become a command line option (if needed in the future)
  #         but right now it is only really used by other scripts that
  #         import this as a module (such as our webapp code).
  #
  # webapp: Indicates that we're running as back-end code for
  #         the FontBakery webapp. This is needed because currently there
  #         are a few features that must be disabled due to lack of support
  #         in the Google App Engine environment.
  fontbakery_check_ttf(config)
