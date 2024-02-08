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
import inspect
import traceback
from typing import Union, Tuple

from fontbakery.result import (
    CheckResult,
    Subresult,
    Identity,
)
from fontbakery.message import Message
from fontbakery.utils import is_negated
from fontbakery.errors import (
    CircularDependencyError,
    FailedConditionError,
    MissingConditionError,
    MissingValueError,
)
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
        use_cache=True,
        jobs=0,
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
        self._jobs = jobs
        # self._iterargs is the *count of each type of thing*.
        for singular, plural in profile.iterargs.items():
            # self._iterargs["fonts"] = len(values.fonts)
            self._iterargs[singular] = len(list(getattr(context, plural)))

        self._profile = profile
        self.context = context

        self.use_cache = use_cache
        self._cache = {"conditions": {}, "order": None}

    @property
    def iterargs(self):
        """uses the singular name as key"""
        iterargs = OrderedDict()
        for name in self._iterargs:
            plural = self._profile.iterargs[name]
            iterargs[name] = tuple(self.context[plural])
        return iterargs

    @property
    def profile(self):
        return self._profile

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

    def get(self, key, iterargs, *args):
        return self._get(key, iterargs, None, *args)

    def get_iterarg(self, name, index):
        """Used by e.g. reporters"""
        plural = self._profile.iterargs[name]
        return list(getattr(self.context,plural))[index].file

    def _get(self, name, iterargs, path, *args):
        if hasattr(self.context, name):
            return getattr(self.context, name)
        return self.context.get_iterarg(name, iterargs)

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
                if hasattr(self.context, name):
                    # Runs on the whole collection
                        val = getattr(self.context, name)
                        err = None
                else:
                    val = self.context.get_iterarg(name, identity.iterargs)
            except Exception as err:
                status = Subresult(ERROR, Message("error", str(err)))
                return (status, None)

            if val is None:
                bool_val = False
            else:
                try:
                    _len = len(val)
                    bool_val = not _len == 0
                except TypeError:
                    # TypeError: object of type 'bool' has no len()
                    bool_val = bool(val)
            if negate:
                val = not val

            if not bool_val:
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
            args = self._get_args(identity.check, identity.iterargs)
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
            status = Subresult(ERROR, Message("failed-dependencies", error))
            return (status, None)

    def _run_check(self, identity: Identity):
        result = CheckResult(identity=identity)

        # Do we skip this check because of dependencies?
        skipped, args = self._get_check_dependencies(identity)
        if skipped:
            result.append(Subresult(SKIP, skipped.message))
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
        order = self._cache.get("order", None)
        if order is not None:
            return order  # pytype:disable=bad-return-type

        order = []
        # section, check, iterargs = identity
        for identity in self._profile.execution_order(
            self._iterargs,
            custom_order=self._custom_order,
            explicit_checks=self._explicit_checks,
            exclude_checks=self._exclude_checks,
        ):
            assert isinstance(identity, Identity)
            order.append(identity)
        self._cache["order"] = order = tuple(order)
        return order

    def run(self, reporters):
        # Tell all the reporters we're starting
        for reporter in reporters:
            reporter.start(self.order)

        def run_a_check(identity):
            result = self._run_check(identity)
            for reporter in reporters:
                reporter.receive_result(result)

        import concurrent.futures

        if self._jobs > 1:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=self._jobs
            ) as executor:
                list(executor.map(run_a_check, self.order))
        else:
            for identity in self.order:
                run_a_check(identity)

        # Tell all the reporters we're done
        for reporter in reporters:
            reporter.end()

    def _override_status(self, subresult: Subresult, check):
        # Potentially override the status based on the profile.
        if new_status := self.profile.should_override(check.id, subresult.message.code):
            subresult.status = new_status
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
        return subresult
