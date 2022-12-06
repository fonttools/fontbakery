"""
This is a temporary profile where proposed new checks with incomplete or
experimental implementations can live for a while, until they're promoted
to one of the other profiles (either universal, or a vendor-specific one).
"""

#from fontbakery.callable import check
from fontbakery.section import Section
#from fontbakery.status import PASS, FAIL, INFO
from fontbakery.fonts_profile import profile_factory
#from fontbakery.message import Message

profile = profile_factory(default_section=Section("Check Proposals"))

'''
Please, feel free to use this template when adding new check proposals here:

@check(
    # Suggested profile: <profile-name>
    # Proponent: <name>
    id = 'com.<revese-domain>/check/<check-name>',
    rationale = """
        <insert rationale text here>
    """,
    proposal = 'https://github.com/googlefonts/fontbakery/issues/<issue-number>'
)
def com_<revese_domain>_check_<check_name>(ttFont):
    """<insert a one-line short description here>"""

    yield INFO,\
          Message('stub',
                  "This proposed check was not yet implemented!")
'''


profile.auto_register(globals())
