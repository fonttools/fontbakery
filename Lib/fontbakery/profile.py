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

    def _get_aggregate_args(self, item, key):
        """
        Get all arguments or mandatory arguments of the item.

        Item is a check or a condition, which means it can be dependent on
        more conditions, this climbs down all the way.
        """
        if key not in ("args", "mandatoryArgs"):
            raise TypeError(f'key must be "args" or "mandatoryArgs", got {key}')
        dependencies = list(getattr(item, key))
        if hasattr(item, "conditions"):
            dependencies += [name for negated, name in map(is_negated, item.conditions)]
        args = set()
        while dependencies:
            name = dependencies.pop()
            if name in args:
                continue
            args.add(name)
            # if this is a condition, expand its dependencies
            c = self.conditions.get(name, None)
            if c is None:
                continue
            dependencies += [
                dependency for dependency in getattr(c, key) if dependency not in args
            ]
        return args

    def get_iterargs(self, item):
        """Returns a tuple of all iterags for item, sorted by name."""
        # iterargs should always be mandatory, unless there's a good reason
        # not to, which I can't think of right now.

        args = self._get_aggregate_args(item, "mandatoryArgs")
        return tuple(sorted([arg for arg in args if arg in self.iterargs]))

    def _analyze_checks(self, all_args, checks):
        args = list(all_args)
        args.reverse()
        # (check, signature, scope)
        scopes = [(check, tuple(), tuple()) for check in checks]
        aggregatedArgs = {
            "args": {
                check.name: self._get_aggregate_args(check, "args") for check in checks
            },
            "mandatoryArgs": {
                check.name: self._get_aggregate_args(check, "mandatoryArgs")
                for check in checks
            },
        }
        saturated = []
        while args:
            new_scopes = []
            # args_set must contain all current args, hence it's before the pop
            args_set = set(args)
            arg = args.pop()
            for check, signature, scope in scopes:
                if not aggregatedArgs["args"][check.name] & args_set:
                    # there's no args no more or no arguments of check are in args
                    target = saturated
                elif (
                    arg == "*check"
                    or arg in aggregatedArgs["mandatoryArgs"][check.name]
                ):
                    signature += (1,)
                    scope += (arg,)
                    target = new_scopes
                else:
                    # there's still a tail of args and check requires one of the
                    # args in tail but not the current arg
                    signature += (0,)
                    target = new_scopes
                target.append((check, signature, scope))
            scopes = new_scopes
        return saturated + scopes

    def _execute_section(self, iterargs, section, items):
        if section is None:
            # base case: terminate recursion
            for check, signature, scope in items:
                yield check, []
        elif not section[0]:
            # no sectioning on this level
            for item in self._execute_scopes(iterargs, items):
                yield item
        elif section[1] == "*check":
            # enforce sectioning by check
            for section_item in items:
                for item in self._execute_scopes(iterargs, [section_item]):
                    yield item
        else:
            # section by gen_arg, i.e. ammend with changing arg.
            _, gen_arg = section
            for index in range(iterargs[gen_arg]):
                for check, args in self._execute_scopes(iterargs, items):
                    yield check, [(gen_arg, index)] + args

    def _execute_scopes(self, iterargs, scopes):
        generators = []
        items = []
        current_section = None
        last_section = None
        seen = set()
        for check, signature, scope in scopes:
            if len(signature):
                # items are left
                if signature[0]:
                    gen_arg = scope[0]
                    scope = scope[1:]
                    current_section = True, gen_arg
                else:
                    current_section = False, None
                signature = signature[1:]
            else:
                current_section = None

            assert (
                current_section not in seen
            ), f"Scopes are badly sorted. {current_section} in {seen}"

            if current_section != last_section:
                if items:
                    # flush items
                    generators.append(
                        self._execute_section(iterargs, last_section, items)
                    )
                    items = []
                    seen.add(last_section)
                last_section = current_section
            items.append((check, signature, scope))
        # clean up left overs
        if items:
            generators.append(self._execute_section(iterargs, current_section, items))

        for item in chain(*generators):
            yield item

    def _section_execution_order(
        self,
        section,
        iterargs,
        reverse=False,
        custom_order=None,
        explicit_checks: Optional[Iterable] = None,
        exclude_checks: Optional[Iterable] = None,
    ):
        """
        order must:
          a) contain all variable args (we're appending missing ones)
          b) not contian duplictates (we're removing repeated items)

        order may contain *iterargs otherwise it is appended
        to the end

        order may contain "*check" otherwise, it is like *check is appended
        to the end (Not done explicitly though).
        """
        stack = list(custom_order) if custom_order is not None else list(section.order)
        if "*iterargs" not in stack:
            stack.append("*iterargs")
        stack.reverse()

        full_order = []
        seen = set()
        while stack:
            item = stack.pop()
            if item in seen:
                continue
            seen.add(item)
            if item == "*iterargs":
                all_iterargs = list(iterargs.keys())
                # assuming there is a meaningful order
                all_iterargs.reverse()
                stack += all_iterargs
                continue
            full_order.append(item)

        # Filter down checks. Checks to exclude are filtered for last as the user
        # might e.g. want to include all tests with "kerning" in the ID, except for
        # "kerning_something". explicit_checks could then be ["kerning"] and
        # exclude_checks ["something"].
        checks = section.checks
        if explicit_checks:
            checks = [
                check
                for check in checks
                if any(include_string in check.id for include_string in explicit_checks)
            ]
        if exclude_checks:
            checks = [
                check
                for check in checks
                if not any(
                    exclude_string in check.id for exclude_string in exclude_checks
                )
            ]

        scopes = self._analyze_checks(full_order, checks)
        # check, signature, scope = item
        scopes.sort(key=lambda item: item[1], reverse=reverse)

        for check, args in self._execute_scopes(iterargs, scopes):
            # this is the iterargs tuple that will be used as a key for caching
            # and so on. we could sort it, to ensure it yields in the same
            # cache locations always, but then again, it is already in a well
            # defined order, by clustering.
            yield check, tuple(args)

    def execution_order(
        self, iterargs, custom_order=None, explicit_checks=None, exclude_checks=None
    ):
        # TODO: a custom_order per section may become necessary one day
        explicit_checks = set() if not explicit_checks else set(explicit_checks)
        for _, section in self._sections.items():
            for check, section_iterargs in self._section_execution_order(
                section,
                iterargs,
                custom_order=custom_order,
                explicit_checks=explicit_checks,
                exclude_checks=exclude_checks,
            ):
                yield Identity(section, check, section_iterargs)

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
