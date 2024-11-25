from difflib import Differ

from fontbakery.prelude import check, Message, WARN


@check(
    id="googlefonts/license/OFL_body_text",
    conditions=["is_ofl", "license_contents"],
    rationale="""
        Check OFL body text is correct.
        Often users will accidently delete parts of the body text.
    """,
    severity=10,  # max severity because licensing mistakes can cause legal problems.
    proposal="https://github.com/fonttools/fontbakery/issues/3352",
)
def check_license_OFL_body_text(license_contents):
    """Check OFL body text is correct."""
    from fontbakery.constants import OFL_BODY_TEXT

    # apply replacements so we get ideal license contents as of 2024.
    # We want https and openfontslicense.org as the url. We also don't
    # seem to care if the last line is an empty line.
    # Not having these will raise warns in other checks.
    if license_contents[-1] == "\n":
        license_contents = license_contents[:-1]

    license_contents = (
        license_contents.replace("http://", "https://")
        .replace(
            "https://scripts.sil.org/OFL",
            "https://openfontlicense.org",
        )
        .replace("<", "\\<")
        .splitlines(keepends=True)[1:]
    )

    diff = Differ()
    res = diff.compare(OFL_BODY_TEXT.splitlines(keepends=True), license_contents)

    changed_lines = [
        f"\\{line}".replace("\n", "\\n") for line in res if line.startswith(("-", "+"))
    ]

    if changed_lines:
        output = "\n\n".join(changed_lines)
        yield WARN, Message(
            "incorrect-ofl-body-text",
            "The OFL.txt body text is incorrect. Please use "
            "https://github.com/googlefonts/Unified-Font-Repository"
            "/blob/main/OFL.txt as a template. "
            "You should only modify the first line.\n\n"
            "Lines changed:\n\n"
            f"{output}\n\n",
        )
