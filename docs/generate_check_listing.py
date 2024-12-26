from fontbakery.profiles.opentype import PROFILE as opentype_profile
from fontbakery.profiles.universal import PROFILE as universal_profile
from fontbakery.profiles.adobefonts import PROFILE as adobefonts_profile
from fontbakery.profiles.fontbureau import PROFILE as fontbureau_profile
from fontbakery.profiles.fontval import PROFILE as fontval_profile
from fontbakery.profiles.fontwerk import PROFILE as fontwerk_profile
from fontbakery.profiles.googlefonts import PROFILE as googlefonts_profile
from fontbakery.profiles.iso15008 import PROFILE as iso15008_profile
from fontbakery.profiles.microsoft import PROFILE as microsoft_profile
from fontbakery.profiles.notofonts import PROFILE as notofonts_profile
from fontbakery.profiles.typenetwork import PROFILE as typenetwork_profile

VENDOR_SPECIFIC_NAMES = [
    "adobefonts",
    "fontbureau",
    "fontval",
    "fontwerk",
    "googlefonts",
    "microsoft",
    "notofonts",
    "typenetwork",
]

seen = set()

for filename, profile, msg in [
    ("opentype", opentype_profile, "Conformance with the OpenType spec"),
    (
        "iso15008",
        iso15008_profile,
        "Conformance with the ISO15008 (car safety) standard",
    ),
    ("universal", universal_profile, "Universal: Generally agreed upon checks"),
    ("adobefonts", adobefonts_profile, "Vendor-specific: Adobe Fonts"),
    ("fontbureau", fontbureau_profile, "Vendor-specific: Fontbureau"),
    ("fontwerk", fontwerk_profile, "Vendor-specific: Fontwerk"),
    ("googlefonts", googlefonts_profile, "Vendor-specific: Google Fonts"),
    ("microsoft", microsoft_profile, "Vendor-specific: Microsoft"),
    ("notofonts", notofonts_profile, "Vendor-specific: Noto fonts"),
    ("typenetwork", typenetwork_profile, "Vendor-specific: Type Network"),
    ("fontval", fontval_profile, "3rd party tool: MS Font Validator wrapper"),
]:
    output = open(f"source/fontbakery/checks/{filename}.rst", "w")
    output.write(f"{'#'*len(msg)}\n{msg}\n{'#'*len(msg)}\n\n")

    for section, checks in profile["sections"].items():
        section_header = (
            f"\n{'-'*len(section)}\n"
            f"{section}\n"
            f"{'-'*len(section)}\n\n"
            f".. toctree::\n"
        )

        for checkid in checks:
            # we don´t want to document any given check more than once:
            if checkid in seen:
                continue
            else:
                seen.add(checkid)

            checkid = checkid.split("/")
            if checkid[0] in VENDOR_SPECIFIC_NAMES:
                vendor_profile = checkid.pop(0)
                if vendor_profile != filename:
                    # Sometimes other vendor checks are referenced in a vendor profile.
                    # But here we'll just list our own vendor-specific checks.
                    continue
                else:
                    f = f"vendorspecific.{vendor_profile}.{'.'.join(checkid)}"
            else:
                f = ".".join(checkid)

            if section_header:
                output.write(section_header)
                section_header = None

            output.write(f".. automodule:: fontbakery.checks.{f}\n    :members:\n")
    output.close()
