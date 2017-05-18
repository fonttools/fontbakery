# -*- coding: <encoding name> -*-
from __future__ import absolute_import, print_function, unicode_literals

import types
from collections import OrderedDict

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

        # font/fonts is an example of an argument, for conditions and
        # for tests where the singular form would run the callable once
        # per item and the plural form would run it once overall, with
        # all items as an argument:

        # it's getting very complex if a callable has multiple of these
        # singular/plural arguments and the intuitive thing to do would
        # be to run each possible combination.

        # for the example of font/fonts, this doesn't make much sense though:
        # in a singular execution the "font" of the condition and the "font"
        # of the test would be the same, only executed if the condition is
        # trueish. Hence, we are back to a linear complexity.

        # There is currently no more examples for this, but as a general rule
        # if there are any singular/plural args, they would change for the
        # conditions and the tests in the same way. So that "font" would
        # always have the same value for the condition and the subsequent
        # test.

        # it's also interesting to note, that if a condition has a
        # singular/plural arg and the test has not, the test would yield
        # the same result for each conditional execution, which is not
        # getting us anywhere.

        # one more thing: since the return value of a condition can be
        # used as an argument for a test, a condition itself can become
        # a singular/plural arg!


        # So: all requested singular-args by a test or it's conditions
        # must be collected. if we got "font" in multiple positions, it
        # will always refer to the same value in each position.
        # If we got another singular-arg, let's say "case/cases" we must
        # execute for each combination of font and case in fonts and cases


        self._iterated_args = {
            'font': 'fonts'
        }

        all_args = set()
        for condition in conditions:
            all_args.update(condition.arguments)
        all_args.uodate(test.arguments)

        used_iterated_args = all_args & set(self._iterated_args.keys())

        # if there are iterated args:
        #     for each compination of iteretad args
                #executes tests

                # we shouldn't re-yield a SKIP if all the conditions
                # where already run with the same arguments AND failed
                # because we get the same skipped message anyways
                # Though, we get a strange count on this in the end :-/
                # To keep a good overall count we should yield all occurences
                #
                # Another Problem: It's hard to cluster tests by font in
                # this example. It would be nice to be able to do this.
                # The problem is that if we run in a per font all tests
                # order, it's hard to cluster by test.
                #
                # Data model wise, we have a many to many relationship
                # and we can only run one thing in depth and one thing in
                # breath

                # In an Ideal world, we can decide both: how to run the tests
                # AND how to order them in the end. The latter means that we
                # yield the results in a way that they can be resorted/clustered
                # freely, once all results have been gathered.
                #
                #
                # So, we should first have a generator to `yield test, args`
                # in some specific order, then we can easily run the tests.
                #
                # generally, one question is, how to run tests without sargs
                # if order by sarg first. They can either run before all,
                # after all or when they occur?


                # iterate by test, then by font then by the other vargs
                # here tests would be clustered by test
                # if there are no test, we don't need to run at all,
                # this is because the tests are what is executed in the end
                # mode = ['*test', 'font', '*varg']
                # iterate by font, other vargs then tests
                # here tests would be clustered by font
                # also, if there are no fonts, we can't run tests in a
                # stupid scenario, we would still have to run once
                # mode = ['font', '*varg', '*test']

                # self._iterated_args could be called "dimensions" ?

                # we should enforce, that we always have a '*test' and a '*varg'
                # argument. Where '*varg' can have an internal ordering
                # and contains all vargs that are NOT explicitly mentioned

                # maybe best is to preprocess, iterate through all tests
                # and create a structure
                # (test, set(used_vargs))
                #
                # so in the case of ['font', '*varg', '*test'], where we
                # basically cluster by font in the iteration order
                # it would be nice to have tests without fonts executed
                # before all other.
                # because, that way, family wide tests would be the first
                # to be run
                #
                # ATTENTION: Much simpler though, could be to control this
                # externally to the TestRunner.
                # But, the reason to do this within could be to have the
                # data tighter together.

                # an execution model could be to have ordered by mode===exec_order
                # satisfy the first possible argument, then call recursively
                # to have the next possible argument satisfied

                # when all args are satisfied: yield/exec
                # otherwise: fail -> missing args
                # so if font is not requested, this arg will obviously be
                # skipped
                # The test would be executed in order though!

                # a way to order this could also be from general to special
                # where special means uses vargs where general means uses less
                # vargs.
                #
                # varg order would still have to be considered.
                # With each skipped varg, a test becomes heavier on the general
                # side.
                #
                # so, we can sort: naturally, general first, specific first
                # where also the varg order plays a role.
                #
                # A test that uses fonts and font is as specific as if it
                # uses only font. Using Fonts as well is not changing this.
                #
                # conditions can require other conditions, hence we need to
                # check for circular dependencies!
                #
                # custom args can override conditions by using the same
                # name, but we should info that for the whole run.
                # If that is the case, the args of the overridden condition
                # don't play any role anymore.

                # Natural order should always be a thing. Also, a spec should
                # be able to section tests, so that they are always executed
                # in a block. (Or at least, that the current section identifier
                # is bound to it ...
                # so, the problem of how to order these things is not so much semantic
                # but really rather organization.
                # then, having sections, a test that requests 'font' cold still
                # be executed by test per font
                # and not by font per test, but that's what we're looking for here!
                # so, we encounter a test with "font", it needs to be dropped into
                # the per-font -> test bucket
                # if it has no font, it's dropped into the generic bucket
                # within that bucket, the font argument is satisfied
                # within both, the generic and the per-font bucket, we need
                # to test for the next var-arg and order accordingly.
                # whether the specific or the generic bucket is executed
                # first is then irrelevant.

        # TODO: decide weather to run once or multiple times

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



###
### This is a stub to build the test execution order logic
###

def  _get_exec_bucket_args(tests, head, tail, options):
    """
        This is just a subroutine of make_bucket.
        It also calls make_bucket itself, recursiveley.
    """
    specific_tests = []
    generic_tests = []
    saturated = []
    tailset = set(tail)
    for test in tests:
        if test.requires(head):
            specific_tests.append(test)
        elif not tail or not len(test.args & tailset):
            # there's no tail or no arguments of test are still in tail
            saturated.append(test)
        else:
            # there's still a tail and test requires one of the
            # args in tail
            generic_tests.append(test)

    generic_bucket = make_bucket(generic_tests, None, tail, **options)\
                                    if generic_tests else None
    specific_bucket = make_bucket(specific_tests, head, tail, **options)\
                                    if specific_tests else None
    return saturated, generic_bucket, specific_bucket

def make_bucket(tests, satisfies,  args, **options):
    """
        Sort the tests to get them into a nice execution order.
        Via "args" the clustering order of tests by their variable,
        iterable arguments can be controlled. A special value in
        args is "*test" which clusters by test.

        If the Keyword argument `generic_first` is False more generic
        tests will be executed after more specific ones (only looking at
        variable, iterable arguments). Defaults to True

        TODO: This needs better documentation. Maybe add examples.

    """
    if satisfies == '*test':
        return TestClusterBucket(make_bucket(tests, None, args, **options))

    head = args[0] if len(args) else None
    tail = args[1:]

    if head != "*test":
        (
            saturated,
            generic_bucket,
            specific_bucket
        ) = _get_exec_bucket_args(tests, head, tail, options)
    else:
        saturated = None
        generic_bucket = None
        specific_bucket = TestClusterBucket(make_bucket(tests, None, tail, **options))

    # run each sub bucket for each font
    return ExecutionBucket(
        satisfies=satisfies,
        saturated=saturated,
        generic_bucket=generic_bucket,
        specific_bucket= specific_bucket,
        **options
    )


class TestClusterBucket(object):
    def __init__(self, subbucket):
        self.subbucket = subbucket;

    def generate(self, args, world):
        tests = OrderedDict()

        for test, args in self.subbucket.generate(args, world):
            if test not in tests:
                tests[test] = []
            tests[test].append(args)

        for test in tests:
            for args in tests[test]:
                yield test, args



class ExecutionBucket(object):
    def __init__(self, satisfies,
                       saturated=None,
                       generic_bucket=None,
                       specific_bucket=None,
                       generic_first=True):
        self._satisfies = satisfies
        self._saturated = saturated
        self._generic_bucket = generic_bucket
        self._specific_bucket = specific_bucket
        self._generic_first = generic_first
        pass

    @property
    def subbuckets(self):
        generic_first = self._generic_first and self._generic_bucket
        generic_last = not self._generic_first and self._generic_bucket

        if generic_first:
            yield generic_first

        if self._specific_bucket:
            yield self._specific_bucket

        if generic_last:
            yield generic_last

    def generate(self, args, world):
        if self._satisfies:
            # this is a specific bucket, it ads one argument tuple
            # yields once per item in self._values
            # using tuples of (key, value) tuples will keep the information
            # of argument order
            items = world.get(self._satisfies, None)
            if items is not None:
                all_args = (args + ((self._satisfies, item),) for item in items)
            else:
                # If items is None, we still want to yield the test
                # eventually. It's just that we can't satisfy the
                # requested argument, but that will fail and be reported
                # when the test is actually called.
                all_args = [args]
        else:
            # this is a generic bucket
            # iterates once, doesn't add anything
            all_args = [args]

        for n_args in all_args:

            if self._generic_first and self._saturated:
                for test in self._saturated:
                    yield (test, n_args)

            for subbucket in self.subbuckets:
                for env in subbucket.generate(n_args, world):
                    yield env;

            if not self._generic_first and self._saturated:
                for test in self._saturated:
                    yield (test, n_args)

class Test(object):
    def __init__(self, name, args):
        self.name = name
        self.args = set(args)

    def requires(self, arg):
        return arg in self.args

    def __str__(self):
        return '<Test {0}>'.format(self.name)

    __repr__ = __str__


if __name__ == '__main__':
            # so how does this organize:
        #      test0(fonts)
        #      test4()
        #      test1(font1)
        #      test2(font1)
        #      test3(font1)
        #      test1(font2)
        #      test2(font2)
        #      test3(font2)
        #      test1(font3)
        #      test2(font3)
        #      test3(font3)
        # AND ALSO:
        #      test0(fonts)
        #      test4()
        #      test1(font1)
        #      test1(font2)
        #      test1(font3)
        #      test2(font1)
        #      test2(font2)
        #      test2(font3)
        #      test3(font1)
        #      test3(font2)
        #      test3(font3)
        #
        # generic_first = True

    tests = [Test(*setup) for setup in (
        ('test0', ('fonts', )),
        ('test1', ('font', 'other', )),
        ('test2', ('font', 'other')),
        ('test3', ('font', )),
        ('test4', tuple())
    )]

    world = {
        'font': ('font1', 'font2', 'font3'),
        'other': ('otherA', 'otherB')
    }

    # generic_first

    order = ['other', 'font', '*test']
    # another, higher level special argument will be "*vargs" which will
    # expand the not specially defined vargs in place
    # if neither "*vargs" nor "*test" is defined it equals to
    # ["*vargs", '*test'] but, '*test' won't have to be explicitly mentioned
    # while "*vargs" will be appended to the end if missing.

    b = make_bucket(tests, None, order, generic_first=False)
    for test, args in b.generate(tuple(), world):
        print('{0}({1})\t->\t{2}'.format(test.name,
                ', '.join(test.args),
                ', '.join(['<{0}>:{1}'.format(*arg) for arg in args]))
        )
