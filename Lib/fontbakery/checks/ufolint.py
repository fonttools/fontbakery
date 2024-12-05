from fontbakery.prelude import check, ERROR, FAIL, PASS, Message


@check(
    id="ufolint",
    rationale="""
        ufolint is a tool that checks UFO source files for common issues.
        It is a good idea to run it before building a font to catch potential
        problems early in the process.
    """,
    proposal="https://github.com/fonttools/fontbakery/pull/1736",
)
def check_ufolint(ufo):
    """Run ufolint on UFO source directory."""

    # IMPORTANT: This check cannot use the 'ufo_font' condition because it makes it
    # skip malformed UFOs (e.g. if metainfo.plist file is missing).

    import subprocess

    ufolint_cmd = ["ufolint", ufo.file]

    try:
        subprocess.check_output(ufolint_cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        yield FAIL, Message(
            "ufolint-fail",
            ("ufolint failed the UFO source. Output follows :" "\n\n{}\n").format(
                e.output.decode()
            ),
        )
    except OSError:
        yield ERROR, Message("ufolint-unavailable", "ufolint is not available!")
    else:
        yield PASS, "ufolint passed the UFO source."
