from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from fontbakery.callable import condition
# used to inform get_module_specification whether and how to create a specification
from fontbakery.fonts_spec import spec_factory # NOQA pylint: disable=unused-import,cyclic-import

@condition
def ttFont(font):
  from fontTools.ttLib import TTFont
  return TTFont(font)


@condition
def is_ttf(ttFont):
  return 'glyf' in ttFont


@condition
def is_cff(ttFont):
  return 'CFF ' in ttFont


@condition
def ligatures(ttFont):
  all_ligatures = {}
  try:
    if "GSUB" in ttFont and ttFont["GSUB"].table.LookupList:
      for lookup in ttFont["GSUB"].table.LookupList.Lookup:
        if lookup.LookupType == 4:  # type 4 = Ligature Substitution
          for subtable in lookup.SubTable:
            for firstGlyph in subtable.ligatures.keys():
              all_ligatures[firstGlyph] = []
              for lig in subtable.ligatures[firstGlyph]:
                if lig.Component[0] not in all_ligatures[firstGlyph]:
                  all_ligatures[firstGlyph].append(lig.Component[0])
    return all_ligatures
  except:
    return -1  # Indicate fontTools-related crash...


@condition
def monospace_stats(ttFont):
  """Returns a dict with data related to the set of glyphs
     among which is a boolean indicating whether or not the
     given font is trully monospaced. The source of truth for
     if a font is monospaced is if at least 80% of all glyphs
     have the same width.
  """
  glyphs = ttFont.getGlyphSet()
  width_occurrences = {}
  width_max = 0
  # count how many times a width occurs
  for glyph_id in glyphs.keys():
    width = glyphs[glyph_id].width
    width_max = max(width, width_max)
    try:
      width_occurrences[width] += 1
    except KeyError:
      width_occurrences[width] = 1
  # find the most_common_width
  occurrences = 0
  for width in width_occurrences.keys():
    if width_occurrences[width] > occurrences:
      occurrences = width_occurrences[width]
      most_common_width = width
  # if more than 80% of glyphs have the same width
  # then the font is very likely considered to be monospaced
  seems_monospaced = occurrences > 0.80 * len(glyphs.keys())

  return {
      "seems_monospaced": seems_monospaced,
      "width_max": width_max,
      "most_common_width": most_common_width
  }


@condition
def seems_monospaced(monospace_stats):
  return monospace_stats['seems_monospaced']


@condition
def missing_whitespace_chars(ttFont):
  from fontbakery.utils import get_glyph_name
  space = get_glyph_name(ttFont, 0x0020)
  nbsp = get_glyph_name(ttFont, 0x00A0)
  # tab = get_glyph_name(ttFont, 0x0009)

  missing = []
  if space is None: missing.append("0x0020")
  if nbsp is None: missing.append("0x00A0")
  # fonts probably don't need an actual tab char
  # if tab is None: missing.append("0x0009")
  return missing


@condition
def vmetrics(ttFonts):
  from fontbakery.utils import get_bounding_box
  v_metrics = {"ymin": 0, "ymax": 0}
  for ttFont in ttFonts:
    font_ymin, font_ymax = get_bounding_box(ttFont)
    v_metrics["ymin"] = min(font_ymin, v_metrics["ymin"])
    v_metrics["ymax"] = max(font_ymax, v_metrics["ymax"])
  return v_metrics


@condition
def is_variable_font(ttFont):
  return "fvar" in ttFont.keys()


def get_instance_axis_value(ttFont, instance_name, axis_tag):
  if not is_variable_font(ttFont):
    return None

  instance = None
  for i in ttFont["fvar"].instances:
    name = ttFont["name"].getDebugName(i.subfamilyNameID)
    if name == instance_name:
      instance = i
      break

  if instance:
    for axis in ttFont["fvar"].axes:
      if axis.axisTag == axis_tag:
        return instance.coordinates[axis_tag]


@condition
def regular_wght_coord(ttFont):
  return get_instance_axis_value(ttFont, "Regular", "wght")


@condition
def bold_wght_coord(ttFont):
  return get_instance_axis_value(ttFont, "Bold", "wght")


@condition
def regular_wdth_coord(ttFont):
  return get_instance_axis_value(ttFont, "Regular", "wdth")


@condition
def regular_slnt_coord(ttFont):
  return get_instance_axis_value(ttFont, "Regular", "slnt")


@condition
def regular_ital_coord(ttFont):
  return get_instance_axis_value(ttFont, "Regular", "ital")


@condition
def regular_opsz_coord(ttFont):
  return get_instance_axis_value(ttFont, "Regular", "opsz")
