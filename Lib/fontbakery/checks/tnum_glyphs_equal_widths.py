from fontbakery.prelude import check, FAIL, PASS


def parse_unicode_escape(s):
    import ast

    s = s.replace('"', r"\"")
    return ast.literal_eval(f'"{s}"')


def verify_widths(ttFont, hbFont, check_text):
    """Shape text and verify all shaped glyphs are the same width"""
    import uharfbuzz as hb

    buffer = hb.Buffer()
    buffer.add_str(check_text)
    buffer.guess_segment_properties()
    hb.shape(hbFont, buffer, features={"tnum": True})

    assert buffer.content_type == hb.BufferContentType.GLYPHS

    glyphs_by_width = {}
    glyphOrder = ttFont.getGlyphOrder()
    for info, pos in zip(buffer.glyph_infos, buffer.glyph_positions):
        width = pos.x_advance
        # width to glyph name mapping
        glyph_name = glyphOrder[info.codepoint]
        if width in glyphs_by_width:
            glyphs_by_width[width].append(glyph_name)
        else:
            glyphs_by_width[width] = [glyph_name]

    return glyphs_by_width


def format_glyphs_by_width(glyphs_by_width):
    """
    Format glyphs_by_width as a string for output. Lists glyph groups sorted
    by the number of glyphs in each group.
    """
    output = ""
    lengths = {w: len(g) for w, g in glyphs_by_width.items()}
    output = "\n".join([f"{w}: {glyphs_by_width[w]}" for w in sorted(lengths.keys())])
    return output


# TODO: Compare this to googlefonts/family/tnum_horizontal_metrics as it seems that
#       it may be possible to merge the checks.
#
#       And see also typenetwork/family/tnum_horizontal_metrics
@check(
    id="tnum_glyphs_equal_widths",
    configs={"TEST_STR"},
    rationale="""
        Check to make sure all the tnum glyphs are the same width.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/4657",
)
def check_tnum_glyphs_equal_widths(ttFont):
    """Widths of tabular number glyphs."""
    import uharfbuzz as hb

    filename = ttFont.reader.file.name
    hbBlob = hb.Blob.from_file_path(filename)
    hbFace = hb.Face(hbBlob)
    hbFont = hb.Font(hbFace)

    check_text = "0123456789"
    if TEST_STR is not None:  # type: ignore # noqa:F821 pylint:disable=E0602
        check_text = TEST_STR  # type: ignore # noqa:F821 pylint:disable=E0602

    # Evaluate any unicode escape sequences, e.g. \N{PLUS SIGN}
    check_text = "".join(
        [parse_unicode_escape(line) for line in check_text.splitlines()]
    )

    # Check for existence of tnum opentype feature
    if "GSUB" not in ttFont:
        yield PASS, "Font does not contain GSUB table"
        return

    gsub = ttFont["GSUB"].table
    if not any(
        feature.FeatureTag == "tnum" for feature in gsub.FeatureList.FeatureRecord
    ):
        yield PASS, "Font does not contain tnum opentype feature"
        return

    # variable or static font
    if "fvar" in ttFont:
        fvar_table = ttFont["fvar"]

        # for each named instance in fvar
        for fvar_instance in fvar_table.instances:
            instance_coord_dict = fvar_instance.coordinates
            hbFont.set_variations(instance_coord_dict)

            # Shape set of characters and verify glyphs have same width
            glyphs_with_widths = verify_widths(ttFont, hbFont, check_text)
            if len(glyphs_with_widths) > 1:
                yield FAIL, (
                    f"tnum glyphs in instance {instance_coord_dict} "
                    f"do not align:\n{format_glyphs_by_width(glyphs_with_widths)}"
                )
            else:
                yield PASS, (
                    f"tnum glyphs in instance {instance_coord_dict} "
                    f"are all the same width: {next(iter(glyphs_with_widths.values()))}"  # pylint:disable=R1708
                )

    else:
        # Shape set of characters and verify glyphs have same width
        glyphs_with_widths = verify_widths(ttFont, hbFont, check_text)
        if len(glyphs_with_widths) > 1:
            yield FAIL, (
                f"tnum glyphs appear not to align:\n{format_glyphs_by_width(glyphs_with_widths)}"
            )
        else:
            yield PASS, (
                f"tnum glyphs are all the same width: {next(iter(glyphs_with_widths.values()))}"  # pylint:disable=R1708
            )
