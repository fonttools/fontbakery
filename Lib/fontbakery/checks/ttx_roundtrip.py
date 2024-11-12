import os

from fontbakery.prelude import check, FAIL, INFO
from fontbakery.testable import TTCFont


@check(
    id="ttx_roundtrip",
    conditions=["not vtt_talk_sources"],
    rationale="""
        One way of testing whether or not fonts are well-formed at the
        binary level is to convert them to TTX and then back to binary. Structural
        problems within the binary font will show up as errors during conversion.
        This is not necessarily something that a designer will be able to address
        but is evidence of a potential bug in the font compiler used to generate
        the binary.""",
    proposal="https://github.com/fonttools/fontbakery/issues/1763",
)
def check_ttx_roundtrip(font):
    """Checking with fontTools.ttx"""
    from fontTools import ttx
    import subprocess
    import sys
    import tempfile

    font_file = font.file
    if isinstance(font, TTCFont):
        ttFont = ttx.TTFont(font.file, fontNumber=font.index)
        ttf_fd, font_file = tempfile.mkstemp()
        os.close(ttf_fd)
        ttFont.save(font_file)

    xml_fd, xml_file = tempfile.mkstemp()
    os.close(xml_fd)

    export_process = subprocess.Popen(
        # TTX still emits warnings & errors even when -q (quiet) is passed
        [sys.executable, "-m", "fontTools.ttx", "-qo", xml_file, font.file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    (export_stdout, export_stderr) = export_process.communicate()
    export_error_msgs = []
    for line in export_stdout.splitlines() + export_stderr.splitlines():
        if line not in export_error_msgs:
            export_error_msgs.append(line)

    if export_error_msgs:
        yield (
            INFO,
            (
                "While converting TTF into an XML file,"
                " ttx emited the messages listed below."
            ),
        )
        for msg in export_error_msgs:
            yield FAIL, msg.strip()

    import_process = subprocess.Popen(
        # TTX still emits warnings & errors even when -q (quiet) is passed
        [sys.executable, "-m", "fontTools.ttx", "-qo", os.devnull, xml_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    (import_stdout, import_stderr) = import_process.communicate()

    if import_process.returncode != 0:
        yield FAIL, (
            "TTX had some problem parsing the generated XML file."
            " This most likely mean there's some problem in the font."
            " Please inspect the output of ttx in order to find more"
            " on what went wrong. A common problem is the presence of"
            " control characteres outside the accepted character range"
            " as defined in the XML spec. FontTools has got a bug which"
            " causes TTX to generate corrupt XML files in those cases."
            " So, check the entries of the name table and remove any control"
            " chars that you find there. The full ttx error message was:\n"
            f"======\n{import_stderr or import_stdout}\n======"
        )

    import_error_msgs = []
    for line in import_stdout.splitlines() + import_stderr.splitlines():
        if line not in import_error_msgs:
            import_error_msgs.append(line)

    if import_error_msgs:
        yield INFO, (
            "While importing an XML file and converting it back to TTF,"
            " ttx emited the messages listed below."
        )
        for msg in import_error_msgs:
            yield FAIL, msg.strip()

    # and then we need to cleanup our mess...
    if os.path.exists(xml_file):
        os.remove(xml_file)
    if font_file != font.file and os.path.exists(font_file):
        os.remove(font_file)
