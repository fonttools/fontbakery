target_modules = [
 "fontbakery-build-font2ttf",
# "fontbakery-build-fontmetadata", # these 1st ones rely on old codebase modules
  "fontbakery-check-description",
  "fontbakery-check-ttf",
  "fontbakery-check-upstream",
# "fontbakery-crawl", # I need to look at this one carefully later
  "fontbakery-fix-ascii-fontmetadata",
  "fontbakery-fix-familymetadata",
  "fontbakery-fix-gasp",
  "fontbakery-fix-glyph-private-encoding",
  "fontbakery-fix-glyphs",
  "fontbakery-fix-nameids",
# "fontbakery-fix-nonhinting", #this one do not even use argparse module
  "fontbakery-fix-ttfautohint",
  "fontbakery-fix-vendorid",
  "fontbakery-fix-vertical-metrics",
  "fontbakery-list-panose",
  "fontbakery-list-weightclass",
  "fontbakery-list-widthclass",
  "fontbakery-metadata-vs-api",
# "fontbakery-stats-deva-per-day", #this one do not even use argparse module
  "fontbakery-update-families"
]


help_text = {}
for module_name in target_modules:
  target = __import__(module_name)
  help_text[module_name] = target.parser.format_help()

# We need to extend this list with our 
# minimal common interface for all scripts:
mandatory_args = ["[-h]"]

# This is a catch-all that contains most args
# used in some of the current scripts.
# We probably want to reduce this list to the bare minimum
# and maybe make some of these mandatory.
optional_args = [
  "[-v]",
  "[--autofix]",
  "[--csv]",
  "[--verbose]",
  "[-a ASCENTS]",
  "[-ah ASCENTS_HHEA]",
  "[-at ASCENTS_TYPO]",
  "[-aw ASCENTS_WIN]",
  "[-d DESCENTS]",
  "[-dh DESCENTS_HHEA]",
  "[-dt DESCENTS_TYPO]",
  "[-dw DESCENTS_WIN]",
  "[-l LINEGAPS]",
  "[-lh LINEGAPS_HHEA]",
  "[-lt LINEGAPS_TYPO]",
  "[--api API]",
  "[--cache CACHE]",
  "[--set SET]",
  "[--platform PLATFORM]",
  "[--id ID]",
  "[--ignore-copy-existing-ttf]",
  "[--with-otf]"
]

failed = False
for arg in mandatory_args:
  missing = []
  for module_name in help_text.keys():
    if arg not in help_text[module_name]:
      missing.append(module_name)

  if missing != []:
    failed = True
    print (("ERROR: These modules lack the {} command line argument:"
            "\nERROR:\t{}\n").format(arg, '\nERROR:\t'.join(missing)))

import re
for module_name in help_text.keys():
  text = help_text[module_name]
  args = re.findall('(\[\-[^\[]*\])', text)
#  print (args)
#  print ("INFO: {}: {}".format(module_name, text))
  for arg in args:
    if arg not in optional_args + mandatory_args:
      print (("WARNING: Module {} has cmdline argument {}"
              " which is not in the list of optional ones."
              "").format(module_name, arg))

# TODO: we also need to verify positional attributes like font and ttfont

if failed:
  sys.exit(-1)

