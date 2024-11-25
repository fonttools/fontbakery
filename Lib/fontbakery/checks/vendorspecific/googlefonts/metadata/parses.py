import os

from fontbakery.prelude import check, Message, PASS, FATAL, SKIP
from fontbakery.utils import exit_with_install_instructions
from fontbakery.checks.vendorspecific.googlefonts.utils import get_FamilyProto_Message


@check(
    id="googlefonts/metadata/parses",
    conditions=["family_directory"],
    rationale="""
        The purpose of this check is to ensure that the METADATA.pb file is not
        malformed.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2248",
)
def check_metadata_parses(family_directory):
    """Check METADATA.pb parse correctly."""
    try:
        from google.protobuf import text_format
    except ImportError:
        exit_with_install_instructions("googlefonts")

    try:
        pb_file = os.path.join(family_directory, "METADATA.pb")
        get_FamilyProto_Message(pb_file)
        yield PASS, "METADATA.pb parsed successfuly."
    except text_format.ParseError as e:
        yield FATAL, Message(
            "parsing-error",
            f"Family metadata at {family_directory} failed to parse.\n"
            f"TRACEBACK:\n{e}",
        )
    except FileNotFoundError:
        yield SKIP, Message(
            "file-not-found",
            f"Font family at '{family_directory}' lacks a METADATA.pb file.",
        )
