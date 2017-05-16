# -*- coding: <encoding name> -*-
from __future__ import absolute_import, print_function, unicode_literals

import types


class Status(object):
    """ If you create a custom Status symbol, please use reverse domain
    name notation as a prefix of `name`.
    This is because all statuses are registered globally and that would
    cause name collisions otherwise.

    However, it's an intended use case for your tests to be able to yield
    custom statuses. Interpreters of the test protocol will have to skip
    statuses unknown to them or treat them in an otherwise non-fatal fashion.
    """
    def __new__(cls, name):
        """ Don't create two instances with same name.

        >>> a = Status('PASS')
        >>> a
        <Status hello>
        >>> b = Status('PASS')
        >>> b
        <Status hello>
        >>> b is a
        True
        >>> b == a
        True
        """
        instance = cls.__instances.get(name, None)
        if instance is None:
            instance = cls.__instances[name] = super(Status, cls).__new__(cls)
            setattr(instance, '_Status__name', name)
        return instance

    __instances = {}

    def __str__(self):
        return '<Status {0}>'.format(self.__name)

    __repr__ = __str__

# Status messages of the test runner protocoll



# always allowed:
INFO = Status('INFO')
WARN = Status('WARN')



STARTTEST = Status('STARTTEST')
# only between STARTTEST and ENDTEST
SKIP = Status('SKIP')
PASS = Status('PASS')
FAIL = Status('FAIL')
# ends the last test started by STARTTEST
ENDTEST = Status('ENDTEST')


class FontBakeryRunnerError(Exception):
    pass

class APIViolationError(FontBakeryRunnerError):
    def __init__(self, message, result, *args):
        self.message = message
        self.result = result
        super(APIViolationError, self).__init__(message, result, *args)

class FailedConditionError(FontBakeryRunnerError):
    """ This is a serious problem with the test suite spec and it must
    be solved.
    """
    def __init__(self, failed_conditions, *args):
        message = 'Some conditions had errors: {0}'.format(
            ', '.join([condition for condition, err in failed_conditions]))
        self.failed_conditions = failed_conditions

        super(FailedConditionsError, self).__init__(message, result, *args)

class TestRunner(object):
    def __init__(tests, conditions):
        self._tests = tests
        self._conditions = conditions

        self._cache = {
            'conditions': {}
        }

    def _check_result(self, result):
        """ Check that the test returned appropriate results:
             * a tuple (<Status>, message)
             * if message is an Exception `status` must not be PASS
           Returns a Tuple which replaces each failing result with a
           failure message: (<Status FAIL>,<APIViolationError>)

           Tests will be implemented by other parties. This is to
           help implementors creating good tests, to spot erroneous
           implementations early and to make it easier to handle
           the results tuple.
        """
        if not isinstance(result, tuple):
            return (FAIL, APIViolationError(
                'Result must be a tuple but '
                'it is {0}.'.format(type(result)), result))

        if len(result) != 2:
            return (FAIL, APIViolationError(
                'Result must have 2 items, but it '
                'has {0}.'.format(len(result)), result))

        status, message = result
        # Allow booleans, but there's no way to issue a WARNING
        if isinstance(status, types.BooleanType):
            # normalize
            status = PASS if status else FAIL
            result = (status, message)

        if not isinstance(status, Status):
            return (FAIL, APIViolationError(
                'Result item `status` must be an instance of '
                'Status, but it is {0} a {1}.'.format(status, type(status)), result))

        if status == PASS and isinstance(message, Exception):
            return (FAIL, APIViolationError(
                'Result item `status` cant be a {0} '
                'since `message` is an Exception'.format(PASS), result))
        # passed:
        return result

    def _exec_test_generator(self, gen):
        """ Execute a generator returned by a test callable.

           Yield each sub-result or, in case of an error, (FAIL, exception)
        """
        try:
           for sub_result in gen:
                # Collect as much as possible
                # list(gen) would in case only produce one
                # error entry. This loop however keeps
                # all sub_results upon the point of error
                # or ends the generator.
                yield sub_result
        except Exception as e:
            yield (FAIL, e)

    def _exec_test(self, test, args, kwds):
        """ Yields test sub results.

        `test` must be a callable

        Each test result is a tuple of: (<Status>, mixed message)
        `status`: must be an instance of Status.
                  If one of the `status` entries in one of the results
                  is FAIL, the whole test is considered failed.
                  WARN is most likely a PASS in a non strict mode and a
                  FAIL in a strict mode.
        `message`:
            * If it is an `Exception` type we expect `status`
              not to be PASS
            * If it is a `string` it's a description of what passed
              or failed.
            * we'll think of an AdvancedMessageType as well, so that
              we can connect the test result with more in depth
              knowledge from the test definition.
        """
        try:
            result = test(*args,**kwds)
        except Exception as e:
            result = (FAIL, e)

        # We allow the `test` callable to "yield" multiple
        # times, instead of returning just once. That's
        # a common thing for unit tests (testing multiple conditions
        # in one method) and a nice feature via yield. It will also
        # help us to be better compatible with our old style tests
        # or with pyunittest-like tests.
        if isinstance(result, types.GeneratorType):
            for sub_result in self._exec_test_generator(result):
                yield self._check_result(sub_result)
        else:
            yield self._check_result(result)

    def _get_condition(condition):
        if condition not in self._cache['conditions']:
            err, val = self._evaluate_condition(condition)
            self._cache['conditions'][condition] = err, val
        return self._cache['conditions'][condition]

    def _get_test_dependencies(self, test):
        # decide weather to run once or multiple times

        # FIXME: if a condition wants "font" we got to check it
        # once per font!
        # ALSO, if test also wants "font" the condition should only skip
        # if it is false for that single font required by the test!
        # this is a bit creepy to implement and requires some restructuring
        # here.
        failed_conditions = False
        unfulfilled_conditions = []
        for condition in test.conditions:
            err, val = self._get_condition(condition)
            if err:
                failed_conditions = True
                status = (FAIL, FailedConditionError(condition, err))
                yield (status, None, None)
                continue
            if not val:
                unfulfilled_conditions.push(condition)
        if failed_conditions:
            return
        if unfulfilled_conditions:
            # This will make the test neither pass nor fail
            status = (SKIP, 'Unfullfilled Conditions: {}'.format(
                                    ', '.join(unfulfilled_conditions)))
            yield (status, None, None)
            return

        argspec = getargspec()

        # has names
        mandatory = argspec.args[:-len(defaults)] \
                        if argspec.defaults is not None else argspec.args

        # has names
        optional = argspec.args[-len(defaults):] \
                        if argspec.defaults is not None else []

        # these only have the names of the arguments *args and **kwds
        # I'm not sure if we need to use them.
        # If there are no args or kwds however, it would be stupid to use
        # em at all.
        # values are None if not availabe
        varargs = argspec.varargs
        keywords = argspec.keywords


        # TODO: test_args =

        if 'font' in test_args:
            # if test has an argument "font" it will be executed once per
            # font in fonts. If it requires "fonts" instead, it is executed
            # once with all fonts.
            for font in fonts:
                yield skipped, args, kwds
        else:
             yield skipped, args, kwds

    def _run_tests(self, tests):
        """ returns all test results as a list of tuples:
            [(test, result), ...]
            where test is the actual test instance and result
            is like the return value of `exec_test`.
        """
        all_results = []
        for test in tests:

            # A test is more than just a function, it carries
            # a lot of meta-data for us, in this case we can use
            # meta-data to learn how to call the test (via
            # configuration or inspection, where inspection would be
            # the default and configuration could be used to override
            # inspection results).
            for skipped, args, kwds in self._get_test_dependencies(test):
                # FIXME: test is not a message
                # so, to us it as a message, it should have a "message-interface"
                # TODO: describe generic "message-interface"
                yield STARTTEST, test
                if skipped is not None:
                    # `skipped` is a normal result tuple (status, message)
                    # where `status` is either FAIL for unmet dependencies
                    # or SKIP for unmet conditions. A status of SKIP is
                    # never a failed test.
                    yield skipped
                else:
                    for sub_result in self._exec_test(test, args, kwds):
                        yield result
                    # The only reason to yield this is to make it testable
                    # that a test ran to its end, or, if we start to allow
                    # nestable subtests. Otherwise, a STARTTEST would end the
                    # previous test implicitly.
                    # We can also use it to display status updates to the user.
                yield ENDTEST, None

