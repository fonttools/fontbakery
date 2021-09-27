"""
Font Bakery CheckRunner is the driver of a font bakery suite of checks.


Separation of Concerns Disclaimer:
While created specifically for checking fonts and font-families this
module has no domain knowledge about fonts. It can be used for any kind
of (document) checking. Please keep it so. It will be valuable for other
domains as well.
Domain specific knowledge should be encoded only in the Profile (Checks,
Conditions) and MAYBE in *customized* reporters e.g. subclasses.

"""
import os
import types
from collections import OrderedDict, Counter
import importlib
import inspect
from typing import Dict, Any

from fontbakery.callable import (
    FontbakeryCallable,
    FontBakeryCheck,
    FontBakeryCondition,
    FontBakeryExpectedValue,
)
from fontbakery.message import Message
from fontbakery.profile import Profile, get_module_profile
from fontbakery.utils import is_negated
from fontbakery.errors import (
    APIViolationError,
    CircularDependencyError,
    FailedCheckError,
    FailedConditionError,
    FailedDependenciesError,
    MissingConditionError,
    SetupError,
    MissingValueError,
    CircularAliasError,
    NamespaceError,
    ValueValidationError,
)
from fontbakery.section import Section
from fontbakery.status import (
    Status,
    DEBUG,
    PASS,
    SKIP,
    INFO,
    WARN,
    FAIL,
    ERROR,
    START,
    STARTCHECK,
    ENDCHECK,
    SECTIONSUMMARY,
    END,
)


class CheckRunner:
    def __init__(
        self,
        profile,
        values,
        config,
        values_can_override_profile_names=True,
        use_cache=True,
    ):
        # TODO: transform all iterables that are list like to tuples
        # to make sure that they won't change anymore.
        # Also remove duplicates from list like iterables

        # Add the profile's config values "underneath" the user's config
        self.config = profile.merge_default_config(config)
        self._custom_order = config["custom_order"]
        self._explicit_checks = config["explicit_checks"]
        self._exclude_checks = config["exclude_checks"]
        self._iterargs = OrderedDict()
        for singular, plural in profile.iterargs.items():
            if plural in values:
                values[plural] = tuple(values[plural])
                self._iterargs[singular] = len(values[plural])

        if not values_can_override_profile_names:
            for name in values:
                if profile.has(name) and profile.get_type(name) != "expected_values":
                    # Of course values can override
                    # expected_values, that's their purpose!
                    raise SetupError(
                        f'Values entry "{name}" collides with profile'
                        f" namespace as a {profile.get_type(name)}"
                    )

        self._profile = profile
        self._profile.test_dependencies()
        valid, message = self._profile.validate_values(values)
        if not valid:
            raise ValueValidationError(
                f"Validation of expected values failed:\n" f"{message}"
            )
        self._values = values

        self.use_cache = use_cache
        self._cache = {"conditions": {}, "order": None}

    def clearCache(self):
        # no need to clear 'order' cache IMO
        self._cache["conditions"] = {}

    @property
    def iterargs(self):
        """ uses the singular name as key """
        iterargs = OrderedDict()
        for name in self._iterargs:
            plural = self._profile.iterargs[name]
            iterargs[name] = tuple(self._values[plural])
        return iterargs

    @property
    def profile(self):
        return self._profile

    def _check_result(self, result):
        """Check that the check returned a well formed result:
        A tuple (<Status>, message)

        A boolean Status is allowd and will be transformed to:
        True <Status: PASS>, False <Status: FAIL>

        Checks will be implemented by other parties. This is to
        help implementors creating good checks, to spot erroneous
        implementations early and to make it easier to handle
        the results tuple.
        """
        if not isinstance(result, tuple):
            msg = f"Result must be a tuple but it is {type(result)}."
            return (FAIL, APIViolationError(msg, result))

        if len(result) != 2:
            msg = f"Result must have 2 items, but it has {len(result)}."
            return (FAIL, APIViolationError(msg, result))

        status, message = result
        # Allow booleans, but there's no way to issue a WARNING
        if isinstance(status, bool):
            # normalize
            status = PASS if status else FAIL
            result = (status, message)

        if not isinstance(status, Status):
            msg = (
                f"Result item `status` must be an instance of Status,"
                f" but it is {status} and its type is {type(status)}."
            )
            return (FAIL, APIViolationError(msg, result))

        return result

    def _exec_check(self, check: FontbakeryCallable, args: Dict[str, Any]):
        """Yields check sub results.

        Each check result is a tuple of: (<Status>, mixed message)
        `status`: must be an instance of Status.
              If one of the `status` entries in one of the results
              is FAIL, the whole check is considered failed.
              WARN is most likely a PASS in a non strict mode and a
              FAIL in a strict mode.
        `message`:
          * If it is an `Exception` type we expect `status`
            not to be PASS
          * If it is a `string` it's a description of what passed
            or failed.
          * we'll think of an AdvancedMessageType as well, so that
            we can connect the check result with more in depth
            knowledge from the check definition.
        """
        if check.configs:
            new_globals = {
                varname: self.config.get(check.id, {}).get(varname)
                for varname in check.configs
            }
            check.inject_globals(new_globals)
        try:
            # A check can be either a normal function that returns one Status or a
            # generator that yields one or more. The latter will return a generator
            # object that we can detect with types.GeneratorType.
            result = check(**args)  # Might raise.

            if isinstance(result, types.GeneratorType):
                # Iterate over sub-results one-by-one, list(result) would abort on
                # encountering the first exception.
                for sub_result in result:  # Might raise.
                    yield self._override_status(self._check_result(sub_result), check)
                return  # Do not fall through to rest of method.
        except Exception as e:
            error = FailedCheckError(e)
            result = (ERROR, error)

        yield self._override_status(self._check_result(result), check)

    def _evaluate_condition(self, name, iterargs, path=None):
        if path is None:
            # top level call
            path = []
        if name in path:
            dependencies = " -> ".join(path)
            msg = f'Condition "{name}" is' f" a circular dependency in {dependencies}"
            raise CircularDependencyError(msg)

        path.append(name)

        try:
            condition = self._profile.conditions[name]
        except KeyError as err:
            error = MissingConditionError(name, err)
            return error, None

        try:
            args = self._get_args(condition, iterargs, path)
        except Exception as err:
            error = FailedConditionError(condition, err)
            return error, None

        path.pop()
        try:
            return None, condition(**args)
        except Exception as err:
            error = FailedConditionError(condition, err)
            return error, None

    def _filter_condition_used_iterargs(self, name, iterargs):
        allArgs = set()
        names = list(self._profile.conditions[name].args)
        while names:
            name = names.pop()
            if name in allArgs:
                continue
            allArgs.add(name)
            if name in self._profile.conditions:
                names += self._profile.conditions[name].args
        return tuple((name, value) for name, value in iterargs if name in allArgs)

    def _get_condition(self, name, iterargs, path=None):
        # conditions are evaluated lazily
        used_iterargs = self._filter_condition_used_iterargs(name, iterargs)
        key = (name, used_iterargs)
        if not self.use_cache or key not in self._cache["conditions"]:
            err, val = self._evaluate_condition(name, used_iterargs, path)
            if self.use_cache:
                self._cache["conditions"][key] = err, val
        else:
            err, val = self._cache["conditions"][key]
        return err, val

    def get(self, key, iterargs, *args):
        return self._get(key, iterargs, None, *args)

    def get_iterarg(self, name, index):
        """ Used by e.g. reporters """
        plural = self._profile.iterargs[name]
        return self._values[plural][index]

    def _generate_iterargs(self, requirements):
        if not requirements:
            yield tuple()
            return
        name, length = requirements[0]
        for index in range(length):
            current = (name, index)
            for tail in self._generate_iterargs(requirements[1:]):
                yield (current,) + tail

    def _derive_iterable_condition(self, name, simple=False, path=None):
        # returns a generator, which is better for memory critical situations
        # than a list containing all results of the used conditions
        condition = self._profile.conditions[name]
        iterargs = self._profile.get_iterargs(condition)

        if not iterargs:
            # without this, we would return just an empty tuple
            raise TypeError(f'Condition "{name}" uses no iterargs.')

        # like [('font', 10), ('other', 22)]
        requirements = [(singular, self._iterargs[singular]) for singular in iterargs]
        for iterargs in self._generate_iterargs(requirements):
            error, value = self._get_condition(name, iterargs, path)
            if error:
                raise error
            if simple:
                yield value
            else:
                yield (iterargs, value)

    def _get(self, name, iterargs, path, *args):
        iterargsDict = dict(iterargs)
        has_fallback = bool(len(args))
        if has_fallback:
            fallback = args[0]

        # try this once before resolving aliases and once after
        if name in self._values:
            return self._values[name]

        original_name = name
        name = self._profile.resolve_alias(name)
        if name != original_name and name in self._values:
            return self._values[name]

        nametype = self._profile.get_type(name, None)

        if name in self._values:
            return self._values[name]

        if nametype == "expected_values":
            # No need to validate
            expected_value = self._profile.get(name)
            if expected_value.has_default:
                # has no default: fallback or MissingValueError
                return expected_value.default

        if nametype == "iterargs" and name in iterargsDict:
            index = iterargsDict[name]
            plural = self._profile.get(name)
            return self._values[plural][index]

        if nametype == "conditions":
            error, value = self._get_condition(name, iterargs, path)
            if error:
                raise error
            return value

        if nametype == "derived_iterables":
            condition_name, simple = self._profile.get(name)
            return self._derive_iterable_condition(condition_name, simple, path)

        if nametype == "config":
            return self.config

        if has_fallback:
            return fallback

        if original_name != name:
            report_name = f'"{original_name}" as "{name}"'
        else:
            report_name = f'"{name}"'
        raise MissingValueError(f"Value {report_name} is undefined.")

    def _get_args(self, item, iterargs, path=None):
        # iterargs can't be optional arguments yet, we wouldn't generate
        # an execution with an empty list. I don't know if that would be even
        # feasible, so I don't add this complication for the sake of clarity.
        # If this is needed for anything useful, we'll have to figure this out.
        args = {}
        for name in item.args:
            if name in args:
                continue
            try:
                args[name] = self._get(name, iterargs, path)
            except MissingValueError:
                if name not in item.optionalArgs:
                    raise
        return args

    def _get_check_dependencies(self, check, iterargs):
        unfulfilled_conditions = []
        for condition in check.conditions:
            negate, name = is_negated(condition)
            if name in self._values:
                # this is a handy way to set flags from the outside
                err, val = None, self._values[name]
            else:
                err, val = self._get_condition(name, iterargs)
            if negate:
                val = not val
            if err:
                status = (ERROR, err)
                return (status, None)

            # An annoying FutureWarning here (Python 3.8.3) on stderr:
            #     "FutureWarning: The behavior of this method will change in future
            #      versions. Use specific 'len(elem)' or 'elem is not None' test instead."
            # Actually not shure how to tackle this, since val is very unspecific
            # here intentionally. Where is the documentation for the change?
            if val is None:
                bool_val = False
            else:
                try:
                    _len = len(val)
                    bool_val = not _len == 0
                except TypeError:
                    # TypeError: object of type 'bool' has no len()
                    bool_val = bool(val)

            if not bool_val:
                unfulfilled_conditions.append(condition)
        if unfulfilled_conditions:
            # This will make the check neither pass nor fail
            comma_separated = ", ".join(unfulfilled_conditions)
            status = (SKIP, f"Unfulfilled Conditions: {comma_separated}")
            return (status, None)

        try:
            args = self._get_args(check, iterargs)
            # Run the generators now, so we can test if they're empty
            for k,v in args.items():
                if inspect.isgenerator(v) or inspect.isgeneratorfunction(v):
                    args[k] = list(v)

            if all(not x for x in args.values()):
                status = (SKIP, "No applicable arguments")
                return (status, None)
            return None, args
        except Exception as error:
            status = (ERROR, FailedDependenciesError(check, error))
            return (status, None)

    def _run_check(self, check, iterargs):
        summary_status = None
        # A check is more than just a function, it carries
        # a lot of meta-data for us, in this case we can use
        # meta-data to learn how to call the check (via
        # configuration or inspection, where inspection would be
        # the default and configuration could be used to override
        # inspection results).

        skipped = None
        if self._profile.check_skip_filter:
            iterargsDict = {
                key: self.get_iterarg(key, index) for key, index in iterargs
            }
            accepted, message = self._profile.check_skip_filter(
                check.id, **iterargsDict
            )
            if not accepted:
                skipped = (SKIP, "Filtered: {}".format(message or "(no message)"))

        if not skipped:
            skipped, args = self._get_check_dependencies(check, iterargs)

        # FIXME: check is not a message
        # so, to use it as a message, it should have a "message-interface"
        # TODO: describe generic "message-interface"
        yield STARTCHECK, None
        if skipped is not None:
            summary_status = skipped[0]
            # `skipped` is a normal result tuple (status, message)
            # where `status` is either FAIL for unmet dependencies
            # or SKIP for unmet conditions or ERROR. A status of SKIP is
            # never a failed check.
            # ERROR is either a missing dependency or a condition that raised
            # an exception. This shouldn't happen when everyting is set up
            # correctly.
            yield skipped
        else:
            for sub_result in self._exec_check(check, args):
                status, _ = sub_result
                if summary_status is None or status >= summary_status:
                    summary_status = status
                yield sub_result
            # The only reason to yield this is to make it testable
            # that a check ran to its end, or, if we start to allow
            # nestable subchecks. Otherwise, a STARTCHECK would end the
            # previous check implicitly.
            # We can also use it to display status updates to the user.
        if summary_status is None:
            summary_status = ERROR
            yield ERROR, (f"The check {check} did not yield any status")
        elif summary_status < PASS:
            summary_status = ERROR
            # got to yield it,so we can see it in the report
            yield ERROR, (
                f"The most significant status of {check}"
                f" was only {summary_status} but"
                f" the minimum is {PASS}"
            )

        yield ENDCHECK, summary_status

    @property
    def order(self):
        order = self._cache.get("order", None)
        if order is None:
            order = []
            # section, check, iterargs = identity
            for identity in self._profile.execution_order(
                self._iterargs,
                custom_order=self._custom_order,
                explicit_checks=self._explicit_checks,
                exclude_checks=self._exclude_checks,
            ):
                order.append(identity)
            self._cache["order"] = order = tuple(order)
        return order

    def check_order(self, order):
        """
        order must be a subset of self.order
        """
        own_order = self.order
        for item in order:
            if item not in own_order:
                raise ValueError(f"Order item {item} not found.")
        return order

    def _check_protocol_generator(self, next_check_identity):
        section, check, iterargs = next_check_identity
        for status, message in self._run_check(check, iterargs):
            yield status, message, (section, check, iterargs)

    def session_protocol_generator(self, order=None):
        order = order if order is not None else self.order
        yield from session_protocol_generator(self._check_protocol_generator, order)

    def run(self, order=None):
        order = order if order is not None else self.order
        session_gen = self.session_protocol_generator(order)
        next_check_gen = iter(order)
        yield from drive_session_protocol(session_gen, next_check_gen)

    def run_externally_controlled(self, receive_result_fn, next_check_gen, order=None):
        order = order if order is not None else self.order
        session_gen = self.session_protocol_generator(order)
        for result in drive_session_protocol(session_gen, next_check_gen):
            receive_result_fn(result)

    def _override_status(self, result, check):
        # Potentially override the status based on the config file.
        # Replaces the status with config["overrides"][check.id][message.code]
        status, message = result
        status_overrides = self.config.get("overrides", {}).get(check.id)
        if (
            not status_overrides
            or not isinstance(message, Message)
            or message.code not in status_overrides
        ):
            return result
        return Status(status_overrides[message.code]), message


def drive_session_protocol(session_gen, next_check_gen):
    # can't send anything but None on first iteration
    value = None
    try:
        while True:
            result = session_gen.send(value)
            yield result
            value = None
            if result[0] in (START, ENDCHECK):
                # get the next check, if None protocol will wrap up
                value = next(next_check_gen, None)
    except StopIteration:
        pass


def session_protocol_generator(check_protocol_generator, order):
    # init

    # Could use self.order, but the truth is, we don't know.
    # However, self.order still should contain each check_identity
    # just to make sure we can actually run the check!
    # Let's just assume that _run_check will fail otherwise...
    sections = OrderedDict()
    next_check_identity = yield START, order, (None, None, None)
    while next_check_identity:

        for event in check_protocol_generator(next_check_identity):
            # send(check_identity) always after ENDCHECK
            next_check_identity = yield event
        # after _run_check the last status must be ENDCHECK
        status, message, (section, check, iterargs) = event
        event = None
        assert status == ENDCHECK

        # message is the summary_status of the check when status is ENDCHECK
        section_key = str(section)
        if section_key not in sections:
            sections[section_key] = ([], Counter(), section)
        section_order, section_summary, _ = sections[section_key]
        section_order.append((check, iterargs))
        # message is the summary_status of the check when status is ENDCHECK
        section_summary[message.name] += 1

    checkrun_summary = Counter()
    for _, (section_order, section_summary, section) in sections.items():
        yield SECTIONSUMMARY, (section_order, section_summary), (section, None, None)
        checkrun_summary.update(section_summary)
    yield END, checkrun_summary, (None, None, None)


def distribute_generator(gen, targets_callbacks):
    for item in gen:
        for target in targets_callbacks:
            target(item)


FILE_MODULE_NAME_PREFIX = "."


def get_module_from_file(filename):
    # filename = 'my/path/to/file.py'
    # module_name = 'file_module.file_py'
    module_name = f"{FILE_MODULE_NAME_PREFIX}{format(os.path.basename(filename).replace('.', '_'))}"
    module_spec = importlib.util.spec_from_file_location(module_name, filename)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    # assert module.__file__ == filename
    return module


def _get_module_from_locator(module_locator):
    if module_locator["name"].startswith(FILE_MODULE_NAME_PREFIX):
        return get_module_from_file(module_locator["origin"])
    # Fails with an appropriate ImportError.
    return importlib.import_module(module_locator["name"], package=None)


def get_profile_from_module_locator(module_locator):
    module = _get_module_from_locator(module_locator)
    return get_module_profile(module)
