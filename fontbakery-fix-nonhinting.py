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
import argparse
import os
import sys
from fontTools import ttLib
from fontTools.ttLib.tables import ttProgram

description = 'Fixes TTF GASP table so that its program ' \
              'contains the minimal recommended instructions'
parser = argparse.ArgumentParser(description=description)
parser.add_argument('fontfile_in',
                     nargs=1,
                    help="Font in OpenType (TTF/OTF) format")
parser.add_argument('fontfile_out',
                    nargs=1,
                    help="Filename for the output")

def main():
  args = parser.parse_args()

  # Open the font file supplied as the first argument on the command line
  fontfile_in = os.path.abspath(args.fontfile_in[0])
  font = ttLib.TTFont(fontfile_in)

  # Save a backup
  backupfont = '{}-backup-fonttools-prep-gasp{}'.format(fontfile_in[0:-4],
                                                        fontfile_in[-4:])
  # print "Saving to ", backupfont
  font.save(backupfont)
  print backupfont, " saved."

  # Print the Gasp table
  if "gasp" in font:
      print ("GASP was: ", font["gasp"].gaspRange)
  else:
      print ("GASP wasn't there")

  # Print the PREP table
  if "prep" in font:
    old_program = ttProgram.Program.getAssembly(font["prep"].program)
    print ("PREP was:\n\t" + "\n\t".join(old_program))
  else:
    print ("PREP wasn't there")

  # Create a new GASP table
  gasp = ttLib.newTable("gasp")

  # Set GASP to the magic number
  gasp.gaspRange = {0xFFFF: 15}

  # Create a new hinting program
  program = ttProgram.Program()

  assembly = ['PUSHW[]',
              '511',
              'SCANCTRL[]',
              'PUSHB[]',
              '4',
              'SCANTYPE[]']
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
  current_program = ttProgram.Program.getAssembly(font["prep"].program)
  print ("PREP now:\n\t" + "\n\t".join(current_program))

  # Save the new file with the name of the input file
  fontfile_out = os.path.abspath(args.fontfile_out[0])
  font.save(fontfile_out)
  print fontfile_out, " saved."

if __name__ == "__main__":
  main()

