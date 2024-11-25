from fontbakery.prelude import check, Message, FAIL


@check(
    id="googlefonts/repo/zip_files",
    conditions=["family_directory"],
    rationale="""
        Sometimes people check in ZIPs into their font project repositories. While we
        accept the practice of checking in binaries, we believe that a ZIP is a step
        too far ;)

        Note: a source purist position is that only source files and build scripts
        should be checked in.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2903",
)
def check_repo_zip_files(family_directory, config):
    """A font repository should not include ZIP files"""
    from fontbakery.utils import filenames_ending_in, pretty_print_list

    COMMON_ZIP_EXTENSIONS = [".zip", ".7z", ".rar"]
    zip_files = []
    for ext in COMMON_ZIP_EXTENSIONS:
        zip_files.extend(filenames_ending_in(ext, family_directory))

    if zip_files:
        files_list = pretty_print_list(config, zip_files, sep="\n\t* ")
        yield FAIL, Message(
            "zip-files",
            f"Please do not host ZIP files on the project repository."
            f" These files were detected:\n"
            f"\t* {files_list}",
        )
