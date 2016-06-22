#!/usr/bin/env python
#
# The magic is in two places:
#
# 1. The GASP table. Vern Adams <vern@newtypography.co.uk>
#    suggests it should have value 15 for all sizes.
#
# 2. The PREP table. Raph Levien <firstname.lastname@gmail.com>
#    suggests using his code to turn on 'drop out control'
#
# PUSHW_1
#  511
# SCANCTRL
# PUSHB_1
#  4
# SCANTYPE
#
# This script depends on fontTools Python library, available
# in most packaging systems and sf.net/projects/fonttools/
#
# Usage:
#
# $ ./fontbakery-fix-nonhinting.py FontIn.ttf FontOut.ttf

# Import our system library and fontTools ttLib
import sys
from fontTools import ttLib
from fontTools.ttLib.tables import ttProgram

# Open the font file supplied as the first argument on the command line
fontfile = sys.argv[1]
font = ttLib.TTFont(fontfile)

# Save a backup
backupfont = fontfile[0:-4] + '-backup-fonttools-prep-gasp' + fontfile[-4:]
# print "Saving to ", backupfont
font.save(backupfont)
print backupfont, "saved."

# Print the Gasp table
if "gasp" in font:
    print ("GASP was: ", font["gasp"].gaspRange)
else:
    print ("GASP wasn't there")

# Print the PREP table
if "prep" in font:
    print ("PREP was: ", ttProgram.Program.getAssembly(font["prep"].program))
else:
    print ("PREP wasn't there")

# Create a new GASP table
gasp = ttLib.newTable("gasp")

# Set GASP to the magic number
gasp.gaspRange = {65535: 15}

# Create a new hinting program
program = ttProgram.Program()

assembly = ['PUSHW[]', '511', 'SCANCTRL[]', 'PUSHB[]', '4', 'SCANTYPE[]']
program.fromAssembly(assembly)

# Create a new PREP table
prep = ttLib.newTable("prep")

# Insert the magic program into it
prep.program = program

# Add the tables to the font, replacing existing ones
font["gasp"] = gasp
font["prep"] = prep

# Print the Gasp table
print "GASP now: ", font["gasp"].gaspRange

# Print the PREP table
print "PREP now: ", ttProgram.Program.getAssembly(font["prep"].program)

# Save the new file with the name of the input file
newfont = fontfile[0:-4] + '-after-fonttools-prep-gasp' + fontfile[-4:]
font.save(newfont)
print newfont, "saved."
