from fontbakery.prelude import check, INFO, Message

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
