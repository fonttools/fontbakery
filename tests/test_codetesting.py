import os

from glyphsLib import GSFont
import pytest

from fontbakery.codetesting import (
    assert_PASS,
    assert_results_contain,
    assert_SKIP,
    GLYPHSAPP_TEST_FILE,
    PATH_TEST_DATA,
    portable_path,
    TEST_FILE,
)
from fontbakery.message import Message
from fontbakery.status import PASS, FAIL, WARN, ERROR, INFO, SKIP, DEBUG


def test_portable_path():
    test_path = "dir/subdir/file"
    assert portable_path(test_path) == f"{os.sep}".join(test_path.split("/"))


def test_TEST_FILE():
    file_path = "dir/file"
    assert TEST_FILE(file_path) == f"{PATH_TEST_DATA}{file_path}"


def test_GLYPHSAPP_TEST_FILE():
    glyphs_filename = "Comfortaa.glyphs"
    gfile = GLYPHSAPP_TEST_FILE(glyphs_filename)
    assert isinstance(gfile, GSFont)


def test_assert_SKIP_success(capsys):
    skip_msg = "SKIP message"
    skip_reason = "SKIP reason"
    results = [
        (PASS,),
        (SKIP, skip_msg),
    ]
    assert assert_SKIP(results, skip_reason) == skip_msg

    captured = capsys.readouterr()
    assert captured.out == f"Test SKIP {skip_reason}\n"


def test_assert_SKIP_failure(capsys):
    pass_msg = "PASS message"
    skip_reason = "SKIP reason"
    results = [
        (SKIP,),
        (PASS, pass_msg),
    ]
    with pytest.raises(AssertionError):
        assert_SKIP(results, skip_reason)

    captured = capsys.readouterr()
    assert captured.out == f"Test SKIP {skip_reason}\n"


def test_assert_PASS_success(capsys):
    pass_msg = "PASS message"
    pass_reason = "with a good font..."
    results = [
        (SKIP,),
        (PASS, pass_msg),
    ]
    assert assert_PASS(results) == pass_msg

    captured = capsys.readouterr()
    assert captured.out == f"Test PASS {pass_reason}\n"


def test_assert_PASS_failure(capsys):
    skip_msg = "SKIP message"
    pass_reason = "with a good font..."
    results = [
        (PASS,),
        (SKIP, skip_msg),
    ]
    with pytest.raises(AssertionError):
        assert_PASS(results)

    captured = capsys.readouterr()
    assert captured.out == f"Test PASS {pass_reason}\n"


def test_assert_PASS_ignore_error_true(capsys):
    error_msg = "ERROR message"
    pass_reason = "with a good font..."
    ignore = "an error"
    results = [
        (PASS,),
        (ERROR, error_msg),
    ]
    assert assert_PASS(results, ignore_error=ignore) is None

    captured = capsys.readouterr()
    assert captured.out == f"Test PASS {pass_reason}\n{ignore}\n"


def test_assert_PASS_ignore_error_false(capsys):
    error_msg = "ERROR message"
    pass_reason = "with a good font..."
    results = [
        (PASS,),
        (ERROR, error_msg),
    ]
    with pytest.raises(AssertionError):
        assert_PASS(results)

    captured = capsys.readouterr()
    assert captured.out == f"Test PASS {pass_reason}\n"


def test_assert_results_contain_expected_msgcode_string():
    bogus_msgcode = True
    with pytest.raises(Exception) as err:
        assert_results_contain([], PASS, bogus_msgcode)
    assert str(err.value) == "The expected message code must be a string"


def test_assert_results_contain_ignore_error_true(capsys):
    msg_code = "a message code"
    ignore = "an error"
    expected_status = PASS
    results = [
        (ERROR, ""),
        (FAIL, ""),
    ]
    assert (
        assert_results_contain(results, expected_status, msg_code, ignore_error=ignore)
        is None
    )

    captured = capsys.readouterr()
    assert captured.out == f"Test {expected_status} [{msg_code}]\n{ignore}\n"


def test_assert_results_contain_bare_string(capsys):
    msg_code = "a message code"
    bare_str = "just a string"
    reason = "just because..."
    expected_status = PASS
    results = [
        (WARN, bare_str),
        (INFO, bare_str),
    ]
    with pytest.raises(Exception) as err:
        assert_results_contain(results, expected_status, msg_code, reason)
    assert f"(Bare string: {bare_str!r})" in str(err.value)

    captured = capsys.readouterr()
    assert captured.out == f"Test {expected_status} {reason}\n"


def test_assert_results_contain_success_string_msg(capsys):
    msg_code = "a message code"
    expected_status = PASS
    results = [
        (PASS, msg_code),
    ]
    assert assert_results_contain(results, expected_status, msg_code) == msg_code

    captured = capsys.readouterr()
    assert captured.out == f"Test {expected_status} [{msg_code}]\n"


def test_assert_results_contain_failure_string_msg(capsys):
    msg_code = "a message code"
    expected_status = PASS
    results = [
        (DEBUG, msg_code),
    ]
    exception_message = (
        f"Expected to find {expected_status}, [code: {msg_code}]\n"
        f"But did not find it in:\n"
        f"{results}"
    )

    with pytest.raises(Exception) as err:
        assert_results_contain(results, expected_status, msg_code)
    assert str(err.value) == exception_message

    captured = capsys.readouterr()
    assert captured.out == f"Test {expected_status} [{msg_code}]\n"


def test_assert_results_contain_success_message_msg(capsys):
    msg_code = "a message code"
    msg_human = "human readable message"
    message = Message(msg_code, msg_human)
    expected_status = FAIL
    results = [
        (FAIL, message),
    ]
    assert assert_results_contain(results, expected_status, msg_code) == msg_human

    captured = capsys.readouterr()
    assert captured.out == f"Test {expected_status} [{msg_code}]\n"


def test_assert_results_contain_failure_message_msg(capsys):
    msg_code = "a message code"
    msg_human = "human readable message"
    message = Message(msg_code, msg_human)
    expected_status = FAIL
    results = [
        (ERROR, message),
    ]
    exception_message = (
        f"Expected to find {expected_status}, [code: {msg_code}]\n"
        f"But did not find it in:\n"
        f"{results}"
    )

    with pytest.raises(Exception) as err:
        assert_results_contain(results, expected_status, msg_code)
    assert str(err.value) == exception_message

    captured = capsys.readouterr()
    assert captured.out == f"Test {expected_status} [{msg_code}]\n"
