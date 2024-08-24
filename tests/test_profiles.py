import inspect
import pkgutil
import importlib
import warnings

import fontbakery
import fontbakery.checks
from fontbakery.callable import FontBakeryCheck

checks_by_id = {}


def load_checks_from_module(module):
    for name, definition in inspect.getmembers(module):
        if isinstance(definition, FontBakeryCheck):
            checks_by_id[definition.id] = definition


def load_all_checks(package=fontbakery.checks):
    for _, import_path, _ in pkgutil.walk_packages(
        path=package.__path__, prefix=package.__name__ + "."
    ):
        try:
            module = importlib.import_module(import_path)
        except ImportError as e:
            warnings.warn("Failed to load %s: %s" % (import_path, e))
            continue
        load_checks_from_module(module)


load_all_checks()


def test_rationale_field():
    for checkid, definition in checks_by_id.items():
        assert definition.rationale is not None
        assert definition.rationale.strip() != ""
