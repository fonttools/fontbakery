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

"""
Script to find for TTF fonts in the given dir the character set coverage 
by family average and per style, and list missing characters.

Usage: $ ./famchar.py directory/
"""

import sys, os, glob, pprint
from fontaine.font import Font

# Need 1 arg 
if len(sys.argv) < 2:
    print __doc__
    sys.exit()
# Check the arg is a directory
workingDir = sys.argv[1]
if os.path.exists(workingDir):
    # If it is a directory, change context to it
    os.chdir(workingDir)
else:
    print __doc__
    sys.exit()

# Run pyFontaine on all the TTF fonts
fonts = {}
for filename in glob.glob("*.*tf"):
    fontaine = Font(filename)
    fonts[filename] = fontaine

# Make a plain dictionary 
family = {}
for fontfilename, fontaine in fonts.iteritems():
    # Use the font file name as a key to a dictionary of char sets
    family[fontfilename] = {}
    #print fontfilename
    for charset, coverage, percentcomplete, missingchars in fontaine.get_orthographies():
        # Use each char set name as a key to a dictionary of this font's coverage details
        charsetname = charset.common_name
        family[fontfilename][charsetname] = {}
        family[fontfilename][charsetname]['coverage'] = coverage # unsupport, fragmentary, partial, full
        family[fontfilename][charsetname]['percentcomplete'] = percentcomplete # int
        family[fontfilename][charsetname]['missingchars'] = missingchars # list of ord numbers
        # Use the char set name as a key to a list of the family's average coverage
        if not family.has_key(charsetname):
            family[charsetname] = []
        # Append the char set percentage of each font file to the list
        family[charsetname].append(percentcomplete) # [10, 32, 40, 40] etc
        # And finally, if the list now has all the font files, make it the mean average percentage
        if len(family[charsetname]) == len(fonts.items()):
            family[charsetname] = sum(family[charsetname]) / len(fonts.items())
        #print charsetname + ":", percentcomplete, "  "
    #print '\n' 


# # pprint the full dict, could be yaml/json/etc
# pp = pprint.PrettyPrinter(indent=1, width=1000, depth=6)
# pprint.pprint(family)

# # pprint all the totals
#import ipdb; ipdb.set_trace()
#for k in sorted(family.keys()):
#    if not k.endswith('.ttf'):
#        print k + ',' + str(family[k])

# Print just the bits we want on the dashboard
print "Family Averages:"
charsets = [u'GWF latin', u'Adobe Latin 3', u'Basic Cyrillic', u'GWF vietnamese', ]
for charset in charsets:
    print charset + ":", str(family[charset])


# # outputs AL3 and GWF CYR charset family percenetages:
#
# for fam in opensans oswald roboto droidsans lato opensanscondensed ptsans droidserif ptsansnarrow ubuntu sourcesanspro robotocondensed yanonekaffeesatz lora arvo nunito raleway lobster francoisone rokkitt oxygen ptserif arimo montserrat bitter merriweather shadowsintolight cabin dosis play cuprum craftygirls abel ubuntucondensed anton specialelite fjallaone mavenpro notosans comingsoon titilliumweb changaone signika vollkorn merriweathersans josefinsans asap questrial inconsolata armata archivonarrow dancingscript pacifico economica cabincondensed unkempt kreon muli comfortaa istokweb squadaone ptsanscaption exo philosopher cantarell nobile quicksand chewy josefinslab playfairdisplay ropasans denkone luckiestguy happymonkey indieflower telex newscycle pontanosans cantataone marvel breeserif fredokaone calligraffitti amaticsc permanentmarker cherrycreamsoda droidsansmono librebaskerville quattrocentosans rocksalt robotoslab gudea righteous oldstandardtt jockeyone playball noticiatext blackopsone karla monda alegreya; do echo -n "$fam,"; ~/src/bakery-xen/scripts/famchar.py */$fam; done

# # outputs number of styles:
#
# for fam in opensans oswald roboto droidsans lato opensanscondensed ptsans droidserif ptsansnarrow ubuntu sourcesanspro robotocondensed yanonekaffeesatz lora arvo nunito raleway lobster francoisone rokkitt oxygen ptserif arimo montserrat bitter merriweather shadowsintolight cabin dosis play cuprum craftygirls abel ubuntucondensed anton specialelite fjallaone mavenpro notosans comingsoon titilliumweb changaone signika vollkorn merriweathersans josefinsans asap questrial inconsolata armata archivonarrow dancingscript pacifico economica cabincondensed unkempt kreon muli comfortaa istokweb squadaone ptsanscaption exo philosopher cantarell nobile quicksand chewy josefinslab playfairdisplay ropasans denkone luckiestguy happymonkey indieflower telex newscycle pontanosans cantataone marvel breeserif fredokaone calligraffitti amaticsc permanentmarker cherrycreamsoda droidsansmono librebaskerville quattrocentosans rocksalt robotoslab gudea righteous oldstandardtt jockeyone playball noticiatext blackopsone karla monda alegreya; do echo -n "$fam,"; echo -n `ls -1 */$fam/*ttf | wc -l`; echo ' '; done
