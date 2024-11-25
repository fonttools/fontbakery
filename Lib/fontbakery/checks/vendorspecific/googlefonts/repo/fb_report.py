from fontbakery.prelude import check, Message, WARN


@check(
    id="googlefonts/repo/fb_report",
    conditions=["family_directory"],
    rationale="""
        A FontBakery report is ephemeral and so should be used for posting issues on a
        bug-tracker instead of being hosted in the font project repository.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2888",
)
def check_repo_fb_report(family_directory):
    """A font repository should not include FontBakery report files"""
    from fontbakery.utils import filenames_ending_in

    has_report_files = any(
        [
            f
            for f in filenames_ending_in(".json", family_directory)
            if '"result"' in open(f, encoding="utf-8").read()
        ]
    )
    if has_report_files:
        yield WARN, Message(
            "fb-report",
            "There's no need to keep a copy of FontBakery reports in the"
            " repository, since they are ephemeral; FontBakery has"
            " a 'github markdown' output mode to make it easy to file"
            " reports as issues.",
        )
