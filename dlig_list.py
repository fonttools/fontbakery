import sys
from fontTools.ttLib import TTFont

if len(sys.argv) != 2:
  sys.exit(f"usage: {sys.argv[0]} fontfile.ttf")
  
fontname = sys.argv[1]
ttFont = TTFont(fontname)
if "GSUB" not in ttFont:
  sys.exit("Font lacks a GSUB table!")

indices = set()
for f in ttFont["GSUB"].table.FeatureList.FeatureRecord:
  if f.FeatureTag == 'dlig':
    for index in f.Feature.LookupListIndex:
      indices.add(index)

dlig = [ttFont["GSUB"].table.LookupList.Lookup[index]
        for index in indices]
    
def ligatures(dlig):
  ligs = []
  for x in dlig:
    for subtable in x.SubTable:
      for glyph, ligatures in subtable.ligatures.items():
        for ligature in ligatures:
          lig = f"{glyph} {' '.join(ligature.Component)} -> {ligature.LigGlyph}"
          ligs.extend([lig])
  return ligs

print ('\n'.join(ligatures(dlig)))
