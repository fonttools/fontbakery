import os

from fontbakery.prelude import check, Message, FAIL, WARN


@check(
    id="googlefonts/metadata/undeclared_fonts",
    conditions=["family_metadata"],
    rationale="""
        The set of font binaries available, except the ones on a "static" subdir,
        must match exactly those declared on the METADATA.pb file.

        Also, to avoid confusion, we expect that font files (other than statics)
        are not placed on subdirectories.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2575",
)
def check_metadata_undeclared_fonts(family_metadata, family_directory):
    """Ensure METADATA.pb lists all font binaries."""

    pb_binaries = []
    for font_metadata in family_metadata.fonts:
        pb_binaries.append(font_metadata.filename)

    binaries = []
    for entry in os.listdir(family_directory):
        if entry != "static" and os.path.isdir(os.path.join(family_directory, entry)):
            for filename in os.listdir(os.path.join(family_directory, entry)):
                if filename[-4:] in [".ttf", ".otf"]:
                    path = os.path.join(family_directory, entry, filename)
                    yield WARN, Message(
                        "font-on-subdir",
                        f'The file "{path}" is a font binary'
                        f" in a subdirectory.\n"
                        f"Please keep all font files (except VF statics)"
                        f" directly on the root directory side-by-side"
                        f" with its corresponding METADATA.pb file.",
                    )
        else:
            # Note: This does not include any font binaries placed in a "static" subdir!
            if entry[-4:] in [".ttf", ".otf"]:
                binaries.append(entry)

    for filename in sorted(set(pb_binaries) - set(binaries)):
        yield FAIL, Message(
            "file-missing",
            f'The file "{filename}" declared on METADATA.pb'
            f" is not available in this directory.",
        )

    for filename in sorted(set(binaries) - set(pb_binaries)):
        yield FAIL, Message(
            "file-not-declared", f'The file "{filename}" is not declared on METADATA.pb'
        )
