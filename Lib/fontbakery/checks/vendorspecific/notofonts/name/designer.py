from fontbakery.prelude import check, WARN, FAIL, Message
from fontbakery.constants import NameID


NOTO_DESIGNERS = [
    "Nadine Chahine - Monotype Design Team",
    "Jelle Bosma - Monotype Design Team",
    "Danh Hong and the Monotype Design Team",
    "Indian Type Foundry and the Monotype Design Team",
    "Ben Mitchell and the Monotype Design Team",
    "Vaibhav Singh and the Monotype Design Team",
    "Universal Thirst, Indian Type Foundry and the Monotype Design Team",
    "Monotype Design Team",
    "Ek Type & Mukund Gokhale",
    "Ek Type",
    "JamraPatel",
    "Dalton Maag Ltd",
    "Amélie Bonet and Sol Matas",
    "Ben Nathan",
    "Indian type Foundry, Jelle Bosma, Monotype Design Team",
    "Indian Type Foundry, Tom Grace, and the Monotype Design Team",
    "Jelle Bosma - Monotype Design Team, Universal Thirst",
    "Juan Bruce, Universal Thirst, Indian Type Foundry and the Monotype Design Team.",
    "Lisa Huang",
    "Mangu Purty",
    "Mark Jamra, Neil Patel",
    "Monotype Design Team (Regular), Sérgio L. Martins (other weights)",
    "Monotype Design Team 2013. Revised by David WIlliams 2020",
    "Monotype Design Team and DaltonMaag",
    "Monotype Design Team and Neelakash Kshetrimayum",
    "Monotype Design Team, Akaki Razmadze",
    "Monotype Design Team, Lewis McGuffie",
    "Monotype Design Team, Nadine Chahine and Nizar Qandah",
    "Monotype Design Team, Sérgio Martins",
    "Monotype Design Team. David Williams.",
    "Patrick Giasson and the Monotype Design Team",
    "David Williams",
    "LIU Zhao",
    "Steve Matteson",
    "Juan Bruce",
    "Sérgio Martins",
    "Lewis McGuffie",
    "YANG Xicheng",
]


@check(
    id="notofonts/name/designer",
    rationale="""
        Noto fonts must contain known designer entries in the name table.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/3681",
)
def check_designer(ttFont):
    """Ensure the designer is a known Noto designer."""
    from fontbakery.utils import get_name_entry_strings

    designers = get_name_entry_strings(ttFont, NameID.DESIGNER)
    if not designers:
        yield FAIL, Message("no-designer", "The font contained no designer name.")

    for designer in designers:
        if designer not in NOTO_DESIGNERS:
            yield WARN, Message(
                "unknown-designer",
                f"The font's designer name '{designer}' was "
                f"not a known Noto font designer.",
            )
