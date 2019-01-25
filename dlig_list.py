import os
import sys
from fontTools.ttLib import TTFont

#if len(sys.argv) != 2:
#  sys.exit(f"usage: {sys.argv[0]} fontfile.ttf")
#
#fontname = sys.argv[1]

def ligatures(dlig):
  ligs = []
  for x in dlig:
    for subtable in x.SubTable:
      try:
        for glyph, ligatures in subtable.ligatures.items():
          for ligature in ligatures:
            lig = f"{glyph} {' '.join(ligature.Component)} -> {ligature.LigGlyph}"
            ligs.extend([lig])
      except:
        print("duh!")
  return ligs

stats = {}
def compute_stats(lig_list):
  global stats
  for ligature in lig_list:
    if ligature in stats:
      stats[ligature] += 1
    else:
      stats[ligature] = 1

for fontdir in open("latin-ext.txt").readlines():
  ligs_in_family = []
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

    indices = set()
    if not ttFont["GSUB"].table.FeatureList:
      continue

    for f in ttFont["GSUB"].table.FeatureList.FeatureRecord:
      if f.FeatureTag == 'dlig':
        for index in f.Feature.LookupListIndex:
          indices.add(index)

    dlig = [ttFont["GSUB"].table.LookupList.Lookup[index]
            for index in indices]
    for l in ligatures(dlig):
      if l not in ligs_in_family:
        ligs_in_family.append(l)

  compute_stats(ligs_in_family)

stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
print ('\n'.join(map(lambda x: f"'{x[0]}': {x[1]}",stats)))

