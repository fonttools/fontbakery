#!/usr/bin/env python3
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
import os
import sys
from fontTools.ttLib import TTFont

#if len(sys.argv) != 2:
#  sys.exit(f"usage: {sys.argv[0]} fontfile.ttf")
#
#fontname = sys.argv[1]

def ligatures(L):
  ligs = []
  for x in L:
    for subtable in x.SubTable:
      try:
        for glyph, ligatures in subtable.ligatures.items():
          for ligature in ligatures:
            lig = f"{glyph} {' '.join(ligature.Component)}" #" -> {ligature.LigGlyph}"
            ligs.extend([lig])
      except:
        print("duh!")
  return ligs

stats = {}
def compute_stats(dlig_list,
                  clig_list,
                  liga_list):
  global stats
  for ligature in dlig_list:
    if ligature in stats:
      stats[ligature]["dlig"] += 1
    else:
      stats[ligature] = {"dlig": 1, "clig": 0, "liga": 0}

  for ligature in clig_list:
    if ligature in stats:
      stats[ligature]["clig"] += 1
    else:
      stats[ligature] = {"dlig": 0, "clig": 1, "liga": 0}

  for ligature in liga_list:
    if ligature in stats:
      stats[ligature]["liga"] += 1
    else:
      stats[ligature] = {"dlig": 0, "clig": 0, "liga": 1}

badguys = []

try:
  fontdirs = open("latin-ext.txt").readlines()
except:
  sys.exit("\n"
           "\n"
           "Before using this tool, please generate a list of"
           " directories with latin-ext fonts by running the"
           " following commands:\n"
           "\n"
           "        cd github.com/google/fonts/\n"
           "        git grep -l latin-ext | cut -d\/ -f1,2 > latin-ext.txt\n"
           "\n"
           "This will create a file called 'latin-ext.txt'"
           " with one family directory per line, including only"
           " those families that are tagged 'latin-ext' on their"
           " METADATA.pb file."
           "\n"
           "\n"
           "Note: You might also want to craft this file manually"
           " depending on what set of font families you wish"
           " to run the tool against."
           "\n"
           "\n"
           "Once you have the latin-ext.txt file you can"
           " re-run this python script.\n"
           "\n")

for fontdir in fontdirs:
  dligs_in_family = []
  cligs_in_family = []
  ligas_in_family = []
  for fontname in os.listdir(fontdir.strip()):
    if not fontname.endswith(".ttf"):
      continue

    fullpath = os.path.join(fontdir.strip(), fontname)
    print(f"fullpath: '{fullpath}'")
    try:
      ttFont = TTFont(fullpath)
    except:
      print ("OuCH!!")
      continue

    if "GSUB" not in ttFont:
      continue #sys.exit("Font lacks a GSUB table!")

    dlig_indices = set()
    clig_indices = set()
    liga_indices = set()
    if not ttFont["GSUB"].table.FeatureList:
      continue

    for f in ttFont["GSUB"].table.FeatureList.FeatureRecord:
      for index in f.Feature.LookupListIndex:
        if f.FeatureTag == 'dlig':
            dlig_indices.add(index)
        elif f.FeatureTag == 'clig':
            clig_indices.add(index)
        elif f.FeatureTag == 'liga':
            liga_indices.add(index)

    dlig = [ttFont["GSUB"].table.LookupList.Lookup[index]
            for index in dlig_indices]
    clig = [ttFont["GSUB"].table.LookupList.Lookup[index]
            for index in clig_indices]
    liga = [ttFont["GSUB"].table.LookupList.Lookup[index]
            for index in liga_indices]

    for l in ligatures(dlig):
      if l not in dligs_in_family:
        dligs_in_family.append(l)

    for l in ligatures(liga):
      if l == 's t' and l not in dlig:
        if l not in badguys:
          print(f"DEBUG: '{l}': {fullpath}")
          badguys.append(l)

      if l not in ligas_in_family:
        ligas_in_family.append(l)

    for l in ligatures(clig):
      if l not in cligs_in_family:
        cligs_in_family.append(l)

  compute_stats(dligs_in_family,
                cligs_in_family,
                ligas_in_family)

#import ipdb; ipdb.set_trace()
stats = sorted(stats.items(), key=lambda x: x[1]["dlig"] + x[1]["clig"] + x[1]["liga"], reverse=False)
for l in stats:
  total = l[1]["dlig"] + l[1]["clig"] + l[1]["liga"]
  if l[1]["liga"] not in [0, total] or \
     l[1]["clig"] not in [0, total] or \
     l[1]["dlig"] not in [0, total]:
    print (f"'{l[0]}': {l[1]}")
