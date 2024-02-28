"""
FontBakery CheckRunner is the driver of an fontbakery suite of checks.


Separation of Concerns Disclaimer:
While created specifically for checking fonts and font-families this
module has no domain knowledge about fonts. It can be used for any kind
of (document) checking. Please keep it so. It will be valuable for other
domains as well.
Domain specific knowledge should be encoded only in the Profile (Checks,
Conditions) and MAYBE in *customized* reporters e.g. subclasses.

"""

from collections import OrderedDict
import concurrent.futures
import inspect
import threading
import traceback
from typing import Union, Tuple

from fontbakery.configuration import Configuration
from fontbakery.result import (
    CheckResult,
    Subresult,
    Identity,
)
from fontbakery.message import Message
from fontbakery.utils import is_negated
from fontbakery.status import (
    Status,
    ERROR,
    FAIL,
    PASS,
    SKIP,
)


class CheckRunner:
    def __init__(
        self,
        profile,
        context,
        config,
        jobs=0,
    ):
        # TODO: transform all iterables that are list like to tuples
        # to make sure that they won't change anymore.
        # Also remove duplicates from list like iterables

        # Add the profile's config values "underneath" the user's config
        self.config = Configuration(**profile.configuration_defaults)
        self.config.update(config)
        self._explicit_checks = config.get("explicit_checks")
        self._exclude_checks = config.get("exclude_checks")
        self._iterargs = OrderedDict()
        self._jobs = jobs
        # self._iterargs is the *count of each type of thing*.
        for singular, plural in profile.iterargs.items():
            # self._iterargs["fonts"] = len(values.fonts)
            self._iterargs[singular] = len(context.testables_by_type.get(singular, []))

        self.profile = profile
        self.context = context
        self.context.config = self.config  # Move later
        self.catch_errors = True

        for testable in self.context.testables:
            testable.context = self.context

    @staticmethod
    def _check_result(result) -> Subresult:
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
            return Subresult(ERROR, Message("api-violation", msg))

        if len(result) != 2:
            msg = f"Result must have 2 items, but it has {len(result)}."
            return Subresult(ERROR, Message("api-violation", msg))

        status, message = result
        # Allow booleans, but there's no way to issue a WARNING
        if isinstance(status, bool):
            # normalize
            status = PASS if status else FAIL

        if not isinstance(status, Status):
            msg = (
                f"Result item `status` must be an instance of Status,"
                f" but it is {status} and its type is {type(status)}."
            )
            return Subresult(FAIL, Message("api-violation", msg))

        if not isinstance(message, Message):
            message = Message(None, message)

        return Subresult(status, message)

    def get_iterarg(self, name, index):
        """Used by e.g. reporters"""
        return self.context.testables_by_type[name][index].file_displayname

    def _get(self, name, iterargs, condition=False):
        # Is this a property of the whole collection?
        if name in dir(self.context):
            return getattr(self.context, name)
        # Is it a property of the file we're testing?
        for thing, index in iterargs:
            specific_thing = self.context.testables_by_type[thing][index]
            # Allow "font" to return the Font object itself
            if name == thing:
                return specific_thing
            if name not in dir(specific_thing):
                continue
            return getattr(specific_thing, name)
        if condition:
            raise ValueError(f"Undefined condition {name}")

        raise ValueError(
            f"This can't happen: asked for {name} but nothing provides it."
        )

    def _get_check_dependencies(
        self, identity: Identity
    ) -> Union[
        Tuple[None, dict],  # Either we got args
        Tuple[Subresult, None],  # or we return a Skipped message
    ]:
        unfulfilled_conditions = []
        for condition in identity.check.conditions:
            negate, name = is_negated(condition)
            try:
                val = bool(self._get(name, identity.iterargs, condition=True))
            except Exception as err:
                if not self.catch_errors:
                    raise
                status = Subresult(ERROR, Message("error", str(err)))
                return (status, None)

            if negate:
                val = not val

            if not val:
                unfulfilled_conditions.append(condition)
        if unfulfilled_conditions:
            # This will make the check neither pass nor fail
            comma_separated = ", ".join(unfulfilled_conditions)
            return (
                Subresult(
                    SKIP,
                    Message(
                        "unfulfilled-conditions",
                        f"Unfulfilled Conditions: {comma_separated}",
                    ),
                ),
                None,
            )

        try:
            args = {
                name: self._get(name, identity.iterargs) for name in identity.check.args
            }
            # Run the generators now, so we can test if they're empty
            for k, v in args.items():
                if inspect.isgenerator(v) or inspect.isgeneratorfunction(v):
                    args[k] = list(v)

            if all(x is None for x in args.values()):
                status = Subresult(
                    SKIP, Message("no-arguments", "No applicable arguments")
                )
                return (status, None)
            return None, args
        except Exception as error:
            if not self.catch_errors:
                raise
            status = Subresult(ERROR, Message("failed-dependencies", error))
            return (status, None)

    def _run_check(self, identity: Identity):
        result = CheckResult(identity=identity)

        # Do we skip this check because of dependencies?
        skipped, args = self._get_check_dependencies(identity)
        if skipped:
            result.append(skipped)
            return result

        check = identity.check
        if check.configs:
            new_globals = {
                varname: self.config.get(check.id, {}).get(varname)
                for varname in check.configs
            }
            check.inject_globals(new_globals)

        try:
            subresults = check(**args)  # Might raise.
            if inspect.isgenerator(subresults) or inspect.isgeneratorfunction(
                subresults
            ):
                subresults = list(subresults)
            else:
                subresults = [subresults]
        except Exception as error:
            if not self.catch_errors:
                raise
            message = f"Failed with {type(error).__name__}: {error}\n```\n"
            message += "".join(traceback.format_tb(error.__traceback__))
            message += "\n```"
            subresults = [(ERROR, Message("failed-check", message))]

        result.extend(
            [
                self._override_status(self._check_result(result), check)
                for result in subresults
            ]
        )
        return result

    @property
    def order(self) -> Tuple[Identity, ...]:
        _order = []
        for section in self.profile.sections:
            for check in section.checks:
                if self._explicit_checks and all(
                    explicit not in check.id for explicit in self._explicit_checks
                ):
                    continue
                if self._exclude_checks and any(
                    excluded in check.id for excluded in self._exclude_checks
                ):
                    continue
                args = set(check.args)
                context_args = set(arg for arg in args if arg in dir(self.context))

                # Either this is a check which runs on the whole collection
                # (i.e. all of its arguments can be called as methods on the
                # CheckRunContext):
                if context_args == args:
                    # In which case, we run it once
                    _order.append(Identity(section, check, ()))
                    continue
                # Or it's a check which runs on each item in the collection.
                for singular, files in self.context.testables_by_type.items():
                    individual_args = args - context_args
                    if (
                        all(
                            arg in dir(file)
                            for arg in individual_args
                            for file in files
                        )
                        or singular in args
                    ):
                        # In which case, we run it once for each item
                        for i, file in enumerate(files):
                            _order.append(Identity(section, check, ((singular, i),)))
        return tuple(_order)

    def run(self, reporters):
        # Tell all the reporters we're starting
        for reporter in reporters:
            reporter.start(self.order)

        reporter_lock = threading.Lock()

        def distribute_result(result):
            with reporter_lock:
                for reporter in reporters:
                    reporter.receive_result(result)

        if self._jobs > 1:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=self._jobs
            ) as executor:
                for identity in self.order:
                    future = executor.submit(self._run_check, identity)
                    future.add_done_callback(
                        lambda future: distribute_result(future.result())
                    )
        else:
            for identity in self.order:
                result = self._run_check(identity)
                distribute_result(result)

        # Tell all the reporters we're done
        for reporter in reporters:
            reporter.end()

    def _override_status(self, subresult: Subresult, check):
        orig_status = subresult.status.name

        # Potentially override the status based on the profile.
        if check.id in self.profile.overrides:
            for override in self.profile.overrides[check.id]:
                if subresult.message.code == override["code"]:
                    subresult.status = Status(override["status"])
                    subresult.message.message += f"""

*Overridden*: This check was originally a {orig_status} but was
overridden by the {self.profile.name} profile:
{override.get("reason", "No reason given.")}
"""
                    return subresult
        # Potentially override the status based on the config file.
        # Replaces the status with config["overrides"][check.id][message.code]
        status_overrides = self.config.get("overrides", {}).get(check.id)
        if (
            not status_overrides
            or not isinstance(subresult.message, Message)
            or subresult.message.code not in status_overrides
        ):
            return subresult
        subresult.status = Status(status_overrides[subresult.message.code])
        subresult.message.message += f"""

*Overridden*: This check was originally a {orig_status} but was
overridden by the configuration file.
"""
        return subresult
