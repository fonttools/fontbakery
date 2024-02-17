"""
FontBakery CheckRunner is the driver of a fontbakery suite of checks.
"""
import glob
import importlib
import inspect
import logging
import os
import pkgutil
import warnings

from fontTools.ttLib.sfnt import readTTCHeader

import fontbakery.checks
from fontbakery.callable import FontBakeryCheck
from fontbakery.testable import CheckRunContext, FILE_TYPES, TTCFont
from fontbakery.errors import ValueValidationError
from fontbakery.profile import Profile, Section


ITERARGS = {val.singular: val.plural for val in FILE_TYPES}


def setup_context(files):
    context = CheckRunContext([])

    for pattern in files:
        if os.path.exists(pattern):
            subfiles = [pattern]
        else:
            subfiles = glob.glob(pattern)
        for file in subfiles:
            accepted = False
            # Special case for .ttc files, which add multiple testables
            # to the context.
            if file.endswith(".ttc") or file.endswith(".otc"):
                with open(file, "rb") as ttcfile:
                    ttc = readTTCHeader(ttcfile)
                    for i in range(ttc.numFonts):
                        context.testables.append(TTCFont(file, index=i))
                    accepted = True
                continue
            for filetype in FILE_TYPES:
                if file.endswith(tuple(filetype.extensions)):
                    context.testables.append(filetype(file))
                    accepted = True
            if not accepted:
                logging.info(
                    "Skipping '{}' as it does not"
                    " seem to be accepted by this profile.",
                    file,
                )
    if not context.testables:
        raise ValueValidationError("No applicable files found")
    return context


checks_by_id = {}
conditions_by_name = {}
checks_loaded = False

FILE_MODULE_NAME_PREFIX = "."


def get_module_from_file(filename):
    # filename = 'my/path/to/file.py'
    # module_name = 'file_module.file_py'
    module_name = f"{FILE_MODULE_NAME_PREFIX}{format(os.path.basename(filename).replace('.', '_'))}"  # noqa:E501 pylint:disable=C0301
    module_spec = importlib.util.spec_from_file_location(module_name, filename)
    if not module_spec:
        raise ValueError(f"Could not get module spec for file {filename}")
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    # assert module.__file__ == filename
    return module


def get_module(name):
    if os.path.isfile(name):
        # This name could also be the name of a module, but if there's a
        # file that we can load the file will win. Otherwise, it's still
        # possible to change the directory
        imported = get_module_from_file(name)
    else:
        # Fails with an appropriate ImportError.
        imported = importlib.import_module(name, package=None)
    return imported


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


def add_checks_to_nascent_profile(sections, section, checks, excluded=None):
    if section not in sections:
        sections[section] = Section(
            name=section,
            checks=[],
        )
    for check in checks:
        if check not in checks_by_id:
            raise ValueError(f"Check {check} not found")
        if excluded and check in excluded:
            continue
        check_object = checks_by_id[check]
        if not sections[section].has_check(check):
            sections[section].checks.append(check_object)


def profile_factory(module):
    # XXX replace with a singleton one day
    global checks_loaded  # pylint: disable=global-statement
    if not checks_loaded:
        load_all_checks()
        checks_loaded = True
    profile_data = getattr(module, "PROFILE")
    sections = {}

    for check_definition in profile_data.get("check_definitions", []):
        module = get_module(check_definition)
        load_checks_from_module(module)

    if "include_profiles" in profile_data:
        for profilename in profile_data["include_profiles"]:
            module = importlib.import_module(f"fontbakery.profiles.{profilename}")
            included_profile = profile_factory(module)
            for section in included_profile.sections:
                add_checks_to_nascent_profile(
                    sections,
                    section.name,
                    [check.id for check in section.checks],
                    excluded=profile_data.get("exclude_checks", []),
                )

    for section, checks in profile_data["sections"].items():
        add_checks_to_nascent_profile(
            sections, section, checks, excluded=profile_data.get("exclude_checks", [])
        )

    profile = Profile(
        name=profile_data.get(
            "name", module.__name__.replace("fontbakery.profiles.", "")
        ),
        iterargs=ITERARGS,
        sections=list(sections.values()),
        overrides=profile_data.get("overrides", {}),
    )
    profile.configuration_defaults = profile_data.get("configuration_defaults", {})
    return profile
