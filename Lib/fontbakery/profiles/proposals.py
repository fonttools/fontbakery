"""
This is a temporary profile where proposed new checks with incomplete or
experimental implementations can live for a while, until they're promoted
to one of the other profiles (either universal, or a vendor-specific one).
"""

from fontbakery.callable import check
from fontbakery.section import Section
from fontbakery.status import INFO  # FAIL, WARN, PASS
from fontbakery.fonts_profile import profile_factory
from fontbakery.message import Message

profile_imports = ((".", ("shared_conditions", "googlefonts_conditions")),)
profile = profile_factory(default_section=Section("Check Proposals"))

TEMPLATE_FOR_NEW_CHECK = '''
Please, feel free to use this template when adding new check proposals here:

@check(
    # Suggested profile: <profile-name>
    # Proponent: <name>
    id = 'com.<revese-domain>/check/<check-name>',
    rationale = """
        <insert rationale text here>
    """,
    proposal = 'https://github.com/fonttools/fontbakery/issues/<issue-number>'
)
def com_<revese_domain>_check_<check_name>(ttFont):
    """<insert a one-line short description here>"""

    yield INFO,\
          Message('stub',
                  "This proposed check was not yet implemented!\n")
'''


@check(
    suggested_profile="googlefonts",
    proponent="Rosalie Wagner (@RosaWagner)",
    id="com.google.fonts/check/mandatory_name_entries",
    rationale="""
        Any fonts checked with GF profile must contain these name IDs:

        * ID 0: Copyright string
                (Copyright: No complaint when everything is missing #3950)

        * ID 9: author's name

        * ID 13: License description

        * ID 14: License URL

        I think we don't care so much about Manufacturer's name,
        Manufacturer's URL and Designer's URL, but will confirm.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3963",
)
def com_google_fonts_check_mandatory_name_entries(ttFont):
    """Mandatory name table entries (other than font names)"""

    yield INFO, Message("stub", "This proposed check was not yet implemented!\n")


profile.auto_register(globals())
