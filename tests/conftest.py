import importlib
import sys
import pytest

from fontbakery.codetesting import CheckTester, checks_by_id


def registered_checks():
    return set(checks_by_id.keys())  # For the sole purpose of mimicking fontspector


def reload_module(module_name):
    module = importlib.import_module(module_name)
    importlib.reload(module)


class ImportRaiser:
    def __init__(self, module_name: str):
        self.module_name = module_name

    def find_spec(self, fullname, path, target=None):
        if fullname == self.module_name:
            raise ImportError()


def remove_import_raiser(module_name):
    for item in sys.meta_path:
        if hasattr(item, "module_name") and item.module_name == module_name:
            sys.meta_path.remove(item)


# FIXME: FSanches: I suspect I've overcomplicated this just because I do not yet
#                  fully understand how pytest.mark.parametrize handles the values.


@pytest.fixture
def check(request):
    if isinstance(request.param, str):
        return CheckTester(request.param)
    else:
        return CheckTester(request.param[0], profile=request.param[1])


has_tests = {}


def check_id(checkname, profile=None):
    has_tests[checkname] = True
    if profile is None:
        return pytest.mark.parametrize("check", [checkname], indirect=True)
    else:
        return pytest.mark.parametrize("check", [(checkname, profile)], indirect=True)


@pytest.hookimpl()
def pytest_sessionfinish(session):
    if session.config.option.keyword:
        return None
    all_checks = set(registered_checks())
    untested = sorted(list(all_checks - set(has_tests)))
    count_checks = len(all_checks)
    count_untested = len(untested)
    bullet_list = "\n".join(f"  - {checkname}" for checkname in untested)
    untested_percentage = count_untested / count_checks * 100
    if count_untested != 0:
        print(
            f"\n{count_untested} checks / {count_checks}"
            f" ({untested_percentage: .1f}%) are untested:\n{bullet_list}"
        )
