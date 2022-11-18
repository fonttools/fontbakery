from typing import Iterable
from collections import OrderedDict
from functools import wraps, partial
from itertools import chain
import re
import importlib
import inspect
import types
import json
import logging

from fontbakery.errors import NamespaceError, SetupError, CircularAliasError
from fontbakery.callable import (
    FontbakeryCallable,
    FontBakeryCheck,
    FontBakeryCondition,
    FontBakeryExpectedValue,
)
from fontbakery.configuration import Configuration
from fontbakery.message import Message
from fontbakery.section import Section
from fontbakery.utils import is_negated
from fontbakery.status import DEBUG


def get_module_profile(module, name=None):
    """
    Get or create a profile from a module and return it.

    If the name `module.profile` is present the value of that is returned.
    Otherwise, if the name `module.profile_factory` is present, a new profile
    is created using `module.profile_factory` and then `profile.auto_register`
    is called with the module namespace.
    If neither name is defined, the module is not considered a profile-module
    and None is returned.

    TODO: describe the `name` argument and better define the signature of `profile_factory`.

    The `module` argument is expected to behave like a python module.
    The optional `name` argument is used when `profile_factory` is called to
    give a name to the default section of the new profile. If name is not
    present `module.__name__` is the fallback.

    `profile_factory` is called like this:
        `profile = module.profile_factory(default_section=default_section)`

    """
    try:
        # if profile is defined we just use it
        return module.profile
    except AttributeError:  # > 'module' object has no attribute 'profile'
        # try to create one on the fly.
        # e.g. module.__name__ == "fontbakery.profiles.cmap"
        if "profile_factory" not in module.__dict__:
            return None
        default_section = Section(name or module.__name__)
        profile = module.profile_factory(
            default_section=default_section, module_spec=module.__spec__
        )
        profile.auto_register(module.__dict__)
        return profile


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
        aliases=None,
        expected_values=None,
        default_section=None,
        check_skip_filter=None,
        profile_tag=None,
        module_spec=None,
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
        self._namespace = {
            "config": "config"  # Filled in by checkrunner
        }

        self.iterargs = {}
        if iterargs:
            self._add_dict_to_namespace("iterargs", iterargs)

        self.derived_iterables = {}
        if derived_iterables:
            self._add_dict_to_namespace("derived_iterables", derived_iterables)

        self.aliases = {}
        if aliases:
            self._add_dict_to_namespace("aliases", aliases)

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

        self._check_skip_filter = check_skip_filter

        # Used in multiprocessing because pickling the profiles fail on
        # Mac and Windows. See: googlefonts/fontbakery#2982
        # module_locator can actually a module.__spec__ but also just a dict
        # self.module_locator will always be just a dict
        if module_spec is None:
            # This is a bit of a hack, but the idea is to reduce boilerplate
            # when writing modules that directly define a profile.
            try:
                frame = inspect.currentframe().f_back
                while frame:
                    # Note, if __spec__ is a local variable we shpuld be at a
                    # module top level. It should also be the correct ModuleSpec
                    # according to how we do this "usually" (as documented and
                    # practiced as far as I'm aware of), e.g. the profile module
                    # defines a profile object directly by calling a Profile constructor
                    # (e.g. profies.ufo_sources) or indirectly via a profile_factory
                    # (e.g. profiles.google_fonts). Otherwise, if this fails
                    # or finds a wrong ModuleSpec, there's still the option to
                    # pass module_spec as an argument (module.__spec__), which is
                    # actually demonstrated in get_module_profile.
                    if "__spec__" in frame.f_locals:
                        module_spec = frame.f_locals["__spec__"]
                        if module_spec and isinstance(
                            module_spec, importlib.machinery.ModuleSpec
                        ):
                            break
                        module_spec = None  # reset
                    frame = frame.f_back
            finally:
                del frame

        # If not module_spec: this is only a problem in multiprocessing, in
        # that case we'll be failing to access this with an AttributeError.
        if module_spec is not None:
            self.module_locator = dict(name=module_spec.name, origin=module_spec.origin)

    _valid_namespace_types = {
        "iterargs": "iterarg",
        "derived_iterables": "derived_iterable",
        "aliases": "alias",
        "conditions": "condition",
        "expected_values": "expected_value",
    }

    @property
    def sections(self):
        return self._sections.values()

    def _add_dict_to_namespace(self, type, data):
        for key, value in data.items():
            self.add_to_namespace(
                type, key, value, force=getattr(value, "force", False)
            )

    def add_to_namespace(self, type, name, value, force=False):
        if type not in self._valid_namespace_types:
            valid_types = ", ".join(self._valid_namespace_types)
            raise TypeError(f'Unknow type "{type}"' f" Valid types are: {valid_types}")

        if name in self._namespace:
            registered_type = self._namespace[name]
            registered_value = getattr(self, registered_type)[name]
            if type == registered_type and registered_value == value:
                # if the registered equals: skip silently. Registering the same
                # value multiple times is allowed, so we can easily expand profiles
                # that define (partly) the same entries
                return

            if not force:
                msg = (
                    f'Name "{name}" is already registered'
                    f' in "{registered_type}" (value: {registered_value}).'
                    f' Requested registering in "{type}" (value: {value}).'
                )
                raise NamespaceError(msg)
            else:
                # clean the old type up
                del getattr(self, registered_type)[name]

        self._namespace[name] = type
        target = getattr(self, type)
        target[name] = value

    def test_dependencies(self):
        """Raises SetupError if profile uses any names that are not declared
        in the its namespace.
        """
        seen = set()
        failed = []
        # make this simple, collect all used names
        for section_name, section in self._sections.items():
            for check in section.checks:
                dependencies = list(check.args)
                if hasattr(check, "conditions"):
                    dependencies += [
                        name for negated, name in map(is_negated, check.conditions)
                    ]

                while dependencies:
                    name = dependencies.pop()
                    if name in seen:
                        continue
                    seen.add(name)
                    if name not in self._namespace:
                        failed.append(name)
                        continue
                    # if this is a condition, expand its dependencies
                    condition = self.conditions.get(name, None)
                    if condition is not None:
                        dependencies += condition.args
        if len(failed):
            comma_separated = ", ".join(failed)
            raise SetupError(
                f"Profile uses names that are not declared"
                f" in its namespace: {comma_separated}."
            )

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
        if len(duplicates):
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
            except:
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
                f"See also: https://github.com/googlefonts/fontbakery/issues/2238\n"
                f"\n"
            )

    def resolve_alias(self, original_name):
        name = original_name
        seen = set()
        path = []
        while name in self.aliases:
            if name in seen:
                names = " -> ".join(path)
                raise CircularAliasError(
                    f'Alias for "{original_name}" has'
                    f" a circular reference in {names}"
                )
            seen.add(name)
            path.append(name)
            name = self.aliases[name]
        return name

    def validate_values(self, values):
        """
        Validate values if they are registered as expected_values and present.

        * If they are not registered they shouldn't be used anywhere at all
          because profile can self check (profile.check_dependencies) for
          missing/undefined dependencies.

        * If they are not present in values but registered as expected_values
          either the expected value has a default value OR a request for that
          name will raise a KeyError on runtime. We don't know if all expected
          values are actually needed/used, thus this fails late.
        """
        messages = []
        for name, value in values.items():
            if name not in self.expected_values:
                continue
            valid, message = self.expected_values[name].validate(value)
            if valid:
                continue
            messages.append(f"{name}: {message} (value: {value})")
        if len(messages):
            return False, "\n".join(messages)
        return True, None

    def get_type(self, name, *args):
        has_fallback = bool(args)
        if has_fallback:
            fallback = args[0]

        if not name in self._namespace:
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
        if not key in ("args", "mandatoryArgs"):
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
        """ Returns a tuple of all iterags for item, sorted by name."""
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
                if not len(aggregatedArgs["args"][check.name] & args_set):
                    # there's no args no more or no arguments of check are
                    # in args
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
                if len(items):
                    # flush items
                    generators.append(
                        self._execute_section(iterargs, last_section, items)
                    )
                    items = []
                    seen.add(last_section)
                last_section = current_section
            items.append((check, signature, scope))
        # clean up left overs
        if len(items):
            generators.append(self._execute_section(iterargs, current_section, items))

        for item in chain(*generators):
            yield item

    def _section_execution_order(
        self,
        section,
        iterargs,
        reverse=False,
        custom_order=None,
        explicit_checks: Iterable = None,
        exclude_checks: Iterable = None,
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
        while len(stack):
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
                yield (section, check, section_iterargs)

    def _register_check(self, section, func):
        other_section = self._check_registry.get(func.id, None)
        if other_section:
            other_check = other_section.get_check(func.id)
            if other_check is func:
                if other_section is not section:
                    logging.debug(
                        "Check {} is already registered in {}, skipping "
                        "register in {}.".format(func, other_section, section)
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

    def check_log_override(
        self,
        override_check_id
        # see def check_log_override
        ,
        *args,
        **kwds,
    ):
        new_id = f"{override_check_id}:{self.profile_tag}"
        old_check, section = self.get_check(override_check_id)
        new_check = check_log_override(old_check, new_id, *args, **kwds)
        new_check.conditions = old_check.conditions
        section.replace_check(override_check_id, new_check)
        return new_check

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

    def _add_check(self, section, func):
        self.add_section(section)
        section.add_check(func)
        return func

    def register_check(self, section=None, *args, **kwds):
        """
        Usage:
        # register in default section
        @profile.register_check
        @check(id='com.example.fontbakery/check/0')
        def my_check():
          yield PASS, 'example'

        # register in `special_section` also register that section in the profile
        @profile.register_check(special_section)
        @check(id='com.example.fontbakery/check/0')
        def my_check():
          yield PASS, 'example'

        """
        if section and len(kwds) == 0 and callable(section):
            func = section
            section = self._default_section
            return self._add_check(section, func)
        else:
            return partial(self._add_check, section)

    def _add_condition(self, condition, name=None):
        self.add_to_namespace(
            "conditions", name or condition.name, condition, force=condition.force
        )
        return condition

    def register_condition(self, *args, **kwds):
        """
        Usage:

        @profile.register_condition
        @condition
        def myCondition():
          return 123

        #or

        @profile.register_condition(name='my_condition')
        @condition
        def myCondition():
          return 123
        """
        if len(args) == 1 and len(kwds) == 0 and callable(args[0]):
            return self._add_condition(args[0])
        else:
            return partial(self._add_condition, *args, **kwds)

    def register_expected_value(self, expected_value, name=None):
        name = name or expected_value.name
        self.add_to_namespace(
            "expected_values", name, expected_value, force=expected_value.force
        )
        return True

    @staticmethod
    def _get_package(symbol_table):
        package = symbol_table.get("__package__", None)
        if package is not None:
            return package
        name = symbol_table.get("__name__", None)
        if name is None or "." not in name:
            return None
        return name.rpartition(".")[0]

    def _load_profile_imports(self, symbol_table):
        """
        profile_imports is a list of module names or tuples
        of (module_name, names to import)
        in the form of ('.', names) it behaces like:
        from . import name1, name2, name3
        or similarly
        import .name1, .name2, .name3

        i.e. "name" in names becomes ".name"
        """
        results = []
        if "profile_imports" not in symbol_table:
            return results

        package = self._get_package(symbol_table)
        profile_imports = symbol_table["profile_imports"]

        for item in profile_imports:
            if isinstance(item, str):
                # import the whole module
                module_name, names = (item, None)
            else:
                # expecting a 2 items tuple or list
                # import only the names from the module
                module_name, names = item

            if "." in module_name and len(set(module_name)) == 1 and names is not None:
                # if you execute `from . import mod` from a module in the pkg package
                # then you will end up importing pkg.mod
                module_names = [f"{module_name}{name}" for name in names]
                names = None
            else:
                module_names = [module_name]

            for module_name in module_names:
                module = importlib.import_module(module_name, package=package)
                if names is None:
                    results.append(module)
                else:
                    #  1. check if the imported module has an attribute by that name
                    #  2. if not, attempt to import a submodule with that name
                    #  3. if the attribute is not found, ImportError is raised.
                    #  …
                    for name in names:
                        try:
                            results.append(getattr(module, name))
                        except AttributeError:
                            # attempt to import a submodule with that name
                            sub_module_name = ".".join([module_name, name])
                            sub_module = importlib.import_module(
                                sub_module_name, package=package
                            )
                            results.append(sub_module)
        return results

    def auto_register(self, symbol_table, filter_func=None, profile_imports=None):
        """Register items from `symbol_table` in the profile.

        Get all items from `symbol_table` dict and from `symbol_table.profile_imports`
        if it is present. If they an item is an instance of FontBakeryCheck,
        FontBakeryCondition or FontBakeryExpectedValue and register it in
        the default section.
        If an item is a python module, try to get a profile using `get_module_profile(item)`
        and then using `merge_profile`;
        If the profile_imports kwarg is given, it is used instead of the one taken from
        the module namespace.

        To register the current module use explicitly:
          `profile.auto_register(globals())`
          OR maybe: `profile.auto_register(sys.modules[__name__].__dict__)`
        To register an imported module explicitly:
          `profile.auto_register(module.__dict__)`

        if filter_func is defined it is called like:
        filter_func(type, name_or_id, item)
        where
        type: one of "check", "module", "condition", "expected_value", "iterarg",
              "derived_iterable", "alias"
        name_or_id: the name at which the item will be registered.
              if type == 'check': the check.id
              if type == 'module': the module name (module.__name__)
        item: the item to be registered
        if filter_func returns a falsy value for an item, the item will
        not be registered.
        """
        if profile_imports:
            symbol_table = symbol_table.copy()  # Avoid messing with original table
            symbol_table["profile_imports"] = profile_imports

        all_items = list(symbol_table.values()) + self._load_profile_imports(
            symbol_table
        )
        namespace_types = (FontBakeryCondition, FontBakeryExpectedValue)
        namespace_items = []

        for item in all_items:
            if isinstance(item, namespace_types):
                # register these after all modules have been registered. That way,
                # "local" items can optionally force override items registered
                # previously by modules.
                namespace_items.append(item)
            elif isinstance(item, FontBakeryCheck):
                if filter_func and not filter_func("check", item.id, item):
                    continue
                self.register_check(item)
            elif isinstance(item, types.ModuleType):
                if filter_func and not filter_func("module", item.__name__, item):
                    continue
                profile = get_module_profile(item)
                if profile:
                    self.merge_profile(profile, filter_func=filter_func)

        for item in namespace_items:
            if isinstance(item, FontBakeryCondition):
                if filter_func and not filter_func("condition", item.name, item):
                    continue
                self.register_condition(item)
            elif isinstance(item, FontBakeryExpectedValue):
                if filter_func and not filter_func("expected_value", item.name, item):
                    continue
                self.register_expected_value(item)

    def merge_profile(self, profile, filter_func=None):
        """Copy all namespace items from profile to self.

        Namespace items are: 'iterargs', 'derived_iterables', 'aliases',
                             'conditions', 'expected_values'

        Don't change any contents of profile ever!
        That means sections are cloned not used directly

        filter_func: see description in auto_register
        """
        # 'iterargs', 'derived_iterables', 'aliases', 'conditions', 'expected_values'
        for ns_type in self._valid_namespace_types:
            # this will raise a NamespaceError if an item of profile.{ns_type}
            # is already registered.
            ns_dict = getattr(profile, ns_type)
            if filter_func:
                ns_type_singular = self._valid_namespace_types[ns_type]
                ns_dict = {
                    name: item
                    for name, item in ns_dict.items()
                    if filter_func(ns_type_singular, name, item)
                }
            self._add_dict_to_namespace(ns_type, ns_dict)

        check_filter_func = (
            None
            if not filter_func
            else lambda check: filter_func("check", check.id, check)
        )
        for section in profile.sections:
            my_section = self._sections.get(str(section), None)
            if not len(section.checks):
                continue
            if my_section is None:
                # create a new section: don't change other module/profile contents
                my_section = section.clone(check_filter_func)
                self.add_section(my_section)
            else:
                # order, description are not updated
                my_section.merge_section(section, check_filter_func)

    @property
    def check_skip_filter(self):
        """ return the current check_skip_filter function or None """
        return self._check_skip_filter

    @check_skip_filter.setter
    def check_skip_filter(self, check_skip_filter):
        """ Set a check_skip_filter function.

        A check_skip_filter has a signature like:

        ```
        def check_skip_filter(check_id: str, **iterargsDict : dict) \
                                    -> Tuple[accepted: bool, message: str]
          …
        ```

        If present, this function is called just before a check
        with `check_id` is executed. `iterargsDict` is a dictionary
        containing key:value pairs of the "iterable arguments" that will be
        applied for that check execution.

        If the returned `accepted` is falsy, the check will be SKIPed using
        `message` for reporting.

        There's no full resolution of all check arguments at this point,
        That can be achieved with the `conditions=[]` argument of the
        check constructor/decorator. This is for more general filtering.
        """
        self._check_skip_filter = check_skip_filter

    @staticmethod
    def serialize_identity(identity):
        """Return a json string that can also  be used as a key.

        The JSON is explicitly unambiguous in the item order
        entries (dictionaries are not ordered usually)
        Otherwise it is valid JSON
        """
        section, check, iterargs = identity
        values = map(
            # separators are without space, which is the default in JavaScript;
            # just in case we need to make these keys in JS.
            partial(json.dumps, separators=(",", ":"))
            # iterargs are sorted, because it doesn't matter for the result
            # but it gives more predictable keys.
            # Though, arguably, the order generated by the profile is also good
            # and conveys insights on how the order came to be (clustering of
            # iterargs). `sorted(iterargs)` however is more robust over time,
            # the keys will be the same, even if the sorting order changes.
            ,
            [str(section), check.id, sorted(iterargs)],
        )
        return '{{"section":{},"check":{},"iterargs":{}}}'.format(*values)

    def deserialize_identity(self, key):
        item = json.loads(key)
        section = self._get_section(item["section"])
        check, _ = self.get_check(item["check"])
        # tuple of tuples instead list of lists
        iterargs = tuple(tuple(item) for item in item["iterargs"])
        return section, check, iterargs

    def serialize_order(self, order):
        return map(self.serialize_identity, order)

    def deserialize_order(self, serialized_order):
        return tuple(self.deserialize_identity(item) for item in serialized_order)

    def setup_argparse(self, argument_parser):
        """
        Set up custom arguments needed for this profile.
        Return a list of keys that will be set to the `values` dictonary
        """
        pass

    def get_deep_check_dependencies(self, check):
        seen = set()
        dependencies = list(check.args)
        if hasattr(check, "conditions"):
            dependencies += [
                name for negated, name in map(is_negated, check.conditions)
            ]
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


def _check_log_override(overrides, status, message):
    # These constants are merely meant to be used
    # so that the check_override declarations are more readable:
    from fontbakery.message import (KEEP_ORIGINAL_STATUS,
                                    KEEP_ORIGINAL_MESSAGE)
    result_status = status
    result_message = message
    override = False
    for override_target, new_status, new_message_string in overrides:
        # Override is only possible by matching message.code
        if (
            not hasattr(result_message, "code")
            or result_message.code != override_target
        ):
            continue
        override = True
        if new_status is not KEEP_ORIGINAL_STATUS:
            result_status = new_status
        if new_message_string is not KEEP_ORIGINAL_MESSAGE:
            # If it looks like an instance of Message we reuse the code,
            # as it is the same condition this makes totally sense.
            result_message = Message(result_message.code, new_message_string)
        # Break the for loop, we had a successful override.
        break
    return override, result_status, result_message


def check_log_override(check, new_id, overrides, reason=None):
    """Returns a new FontBakeryCheck that is decorating (wrapping) check,
    but with overrides applied to returned statuses when they match.

    The new FontBakeryCheck is always a generator check, even if the old
    check is just a normal function that returns (instead of yields)
    its result. Also, the new check yields an INFO Status for each
    overridden original status.

    Arguments:

    check: the FontBakeryCheck to be decorated
    new_id: string, must be unique of course and should not(!) be check.id
            as we essentially create a new, different check.
    overrides: a tuple of override triple-tuples
               ((override_target, new_status, new_message_string), ...)
               override_target: string, specific Message.code
               new_status: Status or None, keep old status
               new_message_string: string or None, keep old message
    """

    @wraps(check)  # defines __wrapped__
    def override_wrapper(*args, **kwds):
        # A check can be either a normal function that returns one Status or a
        # generator that yields one or more. The latter will return a generator
        # object that we can detect with types.GeneratorType.
        result = check(*args, **kwds)  # Might raise.
        if not isinstance(result, types.GeneratorType):
            # Now it iterates
            # make these always iterators, it's nicer to handle
            # also we can mix-in new status messages
            result = (result,)
        # Iterate over sub-results one-by-one, list(result) would abort on
        # encountering the first exception.
        for (status, message) in result:  # Might raise.
            overriden, result_status, result_message = _check_log_override(
                overrides, status, message
            )
            if overriden:
                # nothing changed (despite of a match in override rules)
                if result_status == status and result_message == message:
                    yield DEBUG, (
                        "A check status override rule matched but"
                        " did not change the resulting status."
                    )
                # Both changed
                elif result_status != status and result_message != message:
                    yield DEBUG, (
                        f"Overridden check status and message,"
                        f" original: {status} {message}"
                    )
                # Only status changed
                elif result_status != status and result_message == message:
                    yield DEBUG, f"Overridden check status, original: {status}"
                # Only message changed
                elif result_status == status and result_message != message:
                    yield DEBUG, f"Overridden check message, original: {message}"

            yield result_status, result_message

    # Make the callable here and return that.
    new_check = FontBakeryCheck(
        override_wrapper,
        new_id
        # Untouched, the reason for this checks existence stays the same!
        ,
        rationale=check.rationale
        # the "Derived ..." part should be prominent, so we always see it
        ,
        description=f"{check.description} (derived from {check.id})"
        # ONLY if there's a reason for derivation, otherwise will take
        # the documentation from the __doc__ string of check.
        ,
        documentation=(f"{reason}\n" f"\n" f"{check.documentation}")
        if reason and check.documentation
        else (reason or check.documentation or None),
    )

    # reconstruct a proper doc string from the changes we made.
    # This is really backwards! But, it's so fundamental how python doc
    # strings work, that I think it's solid enough.
    new_check.__doc__ = f"{new_check.description}\n" f"\n" f"{new_check.documentation}"
    return new_check
