from typing import Iterable, Optional
from collections import OrderedDict
from itertools import chain
import re
import logging

from fontbakery.errors import NamespaceError, SetupError
from fontbakery.result import Identity
from fontbakery.configuration import Configuration
from fontbakery.section import Section
from fontbakery.status import Status
from fontbakery.utils import is_negated


class Profile:
    """
    Profiles may specify default configuration values (used to parameterize
    checks), which are then overridden by values in the user's configuration
    file.
    """

    configuration_defaults = {}

    def __init__(
        self,
        sections=None,
        iterargs=None,
        derived_iterables=None,
        conditions=None,
        expected_values=None,
        default_section=None,
        profile_tag=None,
        overrides=None,
    ):
        """
          sections: a list of sections, which are ideally ordered sets of
              individual checks.
              It makes no sense to have checks repeatedly, they yield the same
              results anyway, thus we don't allow this.
          iterargs: maping 'singular' variable names to the iterable in values
              e.g.: `{'font': 'fonts'}` in this case fonts must be iterable AND
              'font' may not be a value NOR a condition name.
          derived_iterables: a dictionary {"plural": ("singular", bool simple)}
              where singular points to a condition, that consumes directly or indirectly
              iterargs. plural will be a list of all values the condition produces
              with all combination of it's iterargs.
              If simple is False, the result returns tuples of: (iterars, value)
              where iterargs is a tuple of ('iterargname', number index)
              Especially for cases where only one iterarg is involved, simple
              can be set to True and the result list will just contain the values.
              Example:

              @condition
              def ttFont(font):
                  return TTFont(font)

              values={'fonts': ['font_0', 'font_1']}
              iterargs={'font': 'fonts'}

              derived_iterables={'ttFonts': ('ttFont', True)}
              # Then:
              ttfons = (
                  <TTFont object from font_0>
                , <TTFont object from font_1>
              )

              # However
              derived_iterables={'ttFonts': ('ttFont', False)}
              ttfons = [
                  ((('font', 0), ), <TTFont object from font_0>)
                , ((('font', 1), ), <TTFont object from font_1>)
              ]

        We will:
          a) get all needed values/variable names from here
          b) add some validation, so that we know the values match
             our expectations! These values must be treated as user input!
        """
        self._namespace = {"config": "config"}  # Filled in by checkrunner

        self.iterargs = {}
        if iterargs:
            self._add_dict_to_namespace("iterargs", iterargs)

        self.derived_iterables = {}
        if derived_iterables:
            self._add_dict_to_namespace("derived_iterables", derived_iterables)

        self.conditions = {}
        if conditions:
            self._add_dict_to_namespace("conditions", conditions)

        self.expected_values = {}
        if expected_values:
            self._add_dict_to_namespace("expected_values", expected_values)

        self._check_registry = {}
        self._sections = OrderedDict()
        if sections:
            for section in sections:
                self.add_section(section)

        if not default_section:
            default_section = (
                sections[0] if sections and len(sections) else Section("Default")
            )
        self._default_section = default_section
        self.add_section(self._default_section)

        # currently only used for new check ids in self.check_log_override
        # only a-z everything else is deleted
        self.profile_tag = re.sub(
            r"[^a-z]", "", (profile_tag or self._default_section.name).lower()
        )

        self.overrides = overrides or {}

    _valid_namespace_types = {
        "iterargs": "iterarg",
        "derived_iterables": "derived_iterable",
        "conditions": "condition",
        "expected_values": "expected_value",
    }

    @property
    def sections(self):
        return self._sections.values()

    def _add_dict_to_namespace(self, ns_type, data):
        for key, value in data.items():
            self.add_to_namespace(
                ns_type, key, value, force=getattr(value, "force", False)
            )

    def add_to_namespace(self, ns_type, name, value, force=False):
        if ns_type not in self._valid_namespace_types:
            valid_types = ", ".join(self._valid_namespace_types)
            raise TypeError(
                f'Unknow type "{ns_type}"' f" Valid types are: {valid_types}"
            )

        if name in self._namespace:
            registered_type = self._namespace[name]
            registered_value = getattr(self, registered_type)[name]
            if ns_type == registered_type and registered_value == value:
                # if the registered equals: skip silently. Registering the same
                # value multiple times is allowed, so we can easily expand profiles
                # that define (partly) the same entries
                return

            if not force:
                msg = (
                    f'Name "{name}" is already registered'
                    f' in "{registered_type}" (value: {registered_value}).'
                    f' Requested registering in "{ns_type}" (value: {value}).'
                )
                raise NamespaceError(msg)
            else:
                # clean the old type up
                del getattr(self, registered_type)[name]

        self._namespace[name] = ns_type
        target = getattr(self, ns_type)
        target[name] = value

    def test_expected_checks(self, expected_check_ids, exclusive=False):
        """Self-test to make a sure profile maintainer is aware of changes in
        the profile.
        Raises SetupError if expected check ids are missing in the profile (removed)
        If `exclusive=True` also raises SetupError if check ids are in the
        profile that are not in expected_check_ids (newly added).

        This is handy if `profile.auto_register` is used and the profile maintainer
        is looking for a high level of control over the profile contents,
        especially for a warning when the profile contents have changed after an
        update.
        """
        s = set()
        duplicates = set(x for x in expected_check_ids if x in s or s.add(x))
        if duplicates:
            raise SetupError(
                "Profile has duplicated entries in its list"
                " of expected check IDs:\n" + "\n".join(duplicates)
            )

        expected_check_ids = set(expected_check_ids)
        registered_checks = set(self._check_registry.keys())
        missing_checks = expected_check_ids - registered_checks
        unexpected_checks = None
        if exclusive:
            unexpected_checks = registered_checks - expected_check_ids
        message = []
        if missing_checks:
            message.append("missing checks: {};".format(", ".join(missing_checks)))
        if unexpected_checks:
            message.append(
                "unexpected checks: {};".format(", ".join(unexpected_checks))
            )
        if message:
            raise SetupError(
                "Profile fails expected checks test:\n" + "\n".join(message)
            )

        def is_numerical_id(checkid):
            try:
                int(checkid.split("/")[-1])
                return True
            except ValueError:
                return False

        numerical_check_ids = [c for c in registered_checks if is_numerical_id(c)]
        if numerical_check_ids:
            list_of_checks = "\t- " + "\n\t- ".join(numerical_check_ids)
            raise SetupError(
                f"\n"
                f"\n"
                f"Numerical check IDs must be renamed to keyword-based IDs:\n"
                f"{list_of_checks}\n"
                f"\n"
                f"See also: https://github.com/fonttools/fontbakery/issues/2238\n"
                f"\n"
            )

    def get_type(self, name, *args):
        has_fallback = bool(args)
        if has_fallback:
            fallback = args[0]

        if name not in self._namespace:
            if has_fallback:
                return fallback
            raise KeyError(name)

        return self._namespace[name]

    def get(self, name, *args):
        has_fallback = bool(args)
        if has_fallback:
            fallback = args[0]

        try:
            target_type = self.get_type(name)
        except KeyError:
            if not has_fallback:
                raise
            return fallback

        target = getattr(self, target_type)
        if name not in target:
            if has_fallback:
                return fallback
            raise KeyError(name)
        return target[name]

    def has(self, name):
        marker_fallback = object()
        val = self.get(name, marker_fallback)
        return val is not marker_fallback

    def _register_check(self, section, func):
        other_section = self._check_registry.get(func.id, None)
        if other_section:
            other_check = other_section.get_check(func.id)
            if other_check is func:
                if other_section is not section:
                    logging.debug(
                        "Check {} is already registered in {}, skipping "
                        "register in {}.",
                        func,
                        other_section,
                        section,
                    )
                return False  # skipped
            else:
                raise SetupError(
                    f'Check id "{func}" is not unique!'
                    f" It is already registered in {other_section} and"
                    f" registration for that id is now requested in {section}."
                    f" BUT the current check is a different object than"
                    f" the registered check."
                )
        self._check_registry[func.id] = section
        return True

    def _unregister_check(self, section, check_id):
        assert (
            section == self._check_registry[check_id]
        ), "Registered section must match"
        del self._check_registry[check_id]
        return True

    def remove_check(self, check_id):
        section = self._check_registry[check_id]
        section.remove_check(check_id)

    def should_override(self, check_id, code) -> Optional[Status]:
        if check_id in self.overrides:
            for override in self.overrides[check_id]:
                if code == override["code"]:
                    return Status(override["status"])
        return None

    def get_check(self, check_id):
        section = self._check_registry[check_id]
        return section.get_check(check_id), section

    def add_section(self, section):
        key = str(section)
        if key in self._sections:
            # the string representation of a section must be unique.
            # string representations of section and check will be used as unique keys
            if self._sections[key] is not section:
                raise SetupError(f"A section with key {section} is already registered")
            return
        self._sections[key] = section
        section.on_add_check(self._register_check)
        section.on_remove_check(self._unregister_check)

        for check in section.checks:
            self._register_check(section, check)

    def _get_section(self, key):
        return self._sections[key]

    def setup_argparse(self, argument_parser):
        """
        Set up custom arguments needed for this profile.
        Return a list of keys that will be set to the `values` dictonary
        """
        pass

    def get_deep_check_dependencies(self, check):
        seen = set()
        dependencies = list(check.args)
        # XXXX fix later
        # if hasattr(check, "conditions"):
        #     dependencies += [
        #         name for negated, name in map(is_negated, check.conditions)
        #     ]
        while dependencies:
            name = dependencies.pop()
            if name in seen:
                continue
            seen.add(name)
            condition = self.conditions.get(name, None)
            if condition is not None:
                dependencies += condition.args
        return seen

    @property
    def checks(self):
        for section in self.sections:
            for check in section.checks:
                yield check

    def get_checks_by_dependencies(self, *dependencies, subset=False):
        deps = set(dependencies)  # faster membership checking
        result = []
        for check in self.checks:
            check_deps = self.get_deep_check_dependencies(check)
            if (subset and deps.issubset(check_deps)) or (
                not subset and len(deps.intersection(check_deps))
            ):
                result.append(check)
        return result

    def merge_default_config(self, user_config):
        """
        Forms a configuration object based on defaults provided by the profile,
        overridden by values in the user's configuration file.
        """
        copy = Configuration(**self.configuration_defaults)
        copy.update(user_config)
        return copy
