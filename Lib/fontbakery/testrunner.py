# -*- coding: utf-8 -*-
"""
Font Bakery TestRunner is the driver of a font bakery test suite.


Separation of Concerns Disclaimer:
While created specifically for testing fonts and font-families this
module has no domain knowledge about fonts. It can be used for any kind
of (document) testing. Please keep it so. It will be valuable for other
domains as well.
Domain specific knowledge should be encoded only in the Spec (Tests,
Conditions) and MAYBE in *customized* reporters e.g. subclasses.

"""
from __future__ import absolute_import, print_function, unicode_literals

import types
from collections import OrderedDict, Counter
from itertools import chain
import sys
import traceback

class Status(object):
  """ If you create a custom Status symbol, please keep in mind that
  all statuses are registered globally and that can cause name collisions.

  However, it's an intended use case for your tests to be able to yield
  custom statuses. Interpreters of the test protocol will have to skip
  statuses unknown to them or treat them in an otherwise non-fatal fashion.
  """
  def __new__(cls, name, weight=0):
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
      setattr(instance, '_Status__weight', weight)
    return instance

  __instances = {}

  def __str__(self):
    return '<Status {0}>'.format(self.__name)

  @property
  def name(self):
    return self.__name

  @property
  def weight(self):
    return self.__weight

  def __gt__(self, other):
    return self.weight > other.weight

  def __ge__(self, other):
    return self.weight >= other.weight

  def __lt__(self, other):
    return self.weight < other.weight

  def __le__(self, other):
    return self.weight <= other.weight

  __repr__ = __str__

# Status messages of the test runner protocoll

# Structuring statuses
#  * begin with "START" and "END"
#  * have weights < 0
#  * START statuses have even weight, corresponding END statuses have odd
#    weights, such that START.weight + 1 == END.weight
#  * the bigger the weight the bigger is the structure, structuring on a macro-level
#  * different structures can have the same weights, if they occur on the same level
#  * ENDTEST is the biggest structuring status
#
# Log statuses
#  * have weights >= 0
#  * the more important the status the bigger the weight
#  * ERROR has the biggest weight
#  * PASS is the lowest status a test can have,
#    i.e.: a test run must at least yield one log that is >= PASS
#
# From all the statuses that can occur within a test, the "worst" one
# is defining for the test overall status:
# ERROR > FAIL > WARN > SKIP > INFO > PASS > DEBUG
# Anything from WARN to PASS does not make a test fail.
# A result < PASS creates an ERROR. That means, DEBUG is not a valid
# result of a test, nor is any of the structuring statuses.
# A test with SKIP can't (MUST NOT) create any other event.

# Log statuses
# only between STARTTEST and ENDTEST:
DEBUG = Status('DEBUG', 0) # Silent by default
INFO = Status('INFO', 2)
WARN = Status('WARN', 4) # A test that results in WARN may indicate an error, but also may be OK
ERROR = Status('ERROR', 6) #  something a programmer must fix
PASS = Status('PASS', 1)
 # SKIP is heavier than PASS because it's likely more interesting to
 # see what got skipped, to reveal blind spots.
SKIP = Status('SKIP', 3)
FAIL = Status('FAIL', 5) # a status of ERROR will make a test fail as well


# Start of the test-suite. Must be always the first message, even in async mode.
# Message is the full execution order of the whole spec
START = Status('START', -6)
# Only between START and END.
# Message is the execution order of the section.
STARTSECTION = Status('STARTSECTION', -4)
# Only between STARTSECTION and ENDSECTION.
# Message is None.
STARTTEST = Status('STARTTEST', -2)
# Ends the last test started by STARTTEST.
# Message the the result status of the whole test, one of PASS, SKIP, FAIL, ERROR.
ENDTEST = Status('ENDTEST', -1)
# Ends the last section started by STARTSECTION.
# Message is a Counter dictionary where the keys are Status.name of
# the ENDTEST message. If serialized, some existing statuses may not be
# in the counter because they never occured in the section.
ENDSECTION = Status('ENDSECTION', -3)
# End of the test-suite. Must be always the last message, even in async mode.
# Message is a counter as described in ENDSECTION, but with the collected
# results of all tests in all sections.
END = Status('END', -5)

class FontBakeryRunnerError(Exception):
  pass

class APIViolationError(FontBakeryRunnerError):
  def __init__(self, message, result, *args):
    self.message = message
    self.result = result
    super(APIViolationError, self).__init__(message, *args)

class ProtocolViolationError(FontBakeryRunnerError):
  def __init__(self, message, *args):
    self.message = message
    super(ProtocolViolationError, self).__init__(message, *args)


class FailedTestError(FontBakeryRunnerError):
  def __init__(self, error, traceback, *args):
    message = 'Failed with {0}: {1}'.format(type(error).__name__, error)
    self.error = error
    self.traceback = traceback
    super(FailedTestError, self).__init__(message, *args)

class FailedConditionError(FontBakeryRunnerError):
  """ This is a serious problem with the test suite spec and it must
  be solved.
  """
  def __init__(self, condition, error, traceback, *args):
    message = 'The condtion {0} had an error: {1}: {2}'.format(condition, type(error).__name__, error)
    self.condition = condition
    self.error = error
    self.traceback = traceback
    super(FailedConditionError, self).__init__(message, *args)

class MissingConditionError(FontBakeryRunnerError):
  """ This is a serious problem with the test suite spec and it must
  be solved, most probably a typo.
  """
  def __init__(self, condition_name, error, traceback, *args):
    message = 'The condtion named {0} is missing: {1}: {2}'.format(
                              condition_name, type(error).__name__, error)
    self.error = error
    self.traceback = traceback
    super(MissingConditionError, self).__init__(message, *args)

class FailedDependenciesError(FontBakeryRunnerError):
  def __init__(self, test, error, traceback, *args):
    message = 'The test {0} had an error: {1}: {2}'.format(test, type(error).__name__, error)
    self.test = test
    self.error = error
    self.traceback = traceback
    super(FailedDependenciesError, self).__init__(message, *args)

class SetupError(FontBakeryRunnerError):
  pass

class MissingValueError(FontBakeryRunnerError):
  pass

class CircularAliasError(FontBakeryRunnerError):
  pass

class NamespaceError(FontBakeryRunnerError):
  pass

def get_traceback():
  """
  Returns a string with a traceback as the python interpreter would
  render it. Run this inside of the except block.
  """
  ex_type, ex, tb = sys.exc_info()
  result = traceback.format_exc(tb)
  del tb
  return result

class TestRunner(object):
  def __init__(self, spec, values
             , values_can_override_spec_names=True
             , explicit_tests = None
             ):
    # TODO: transform all iterables that are list like to tuples
    # to make sure that they won't change anymore.
    # Also remove duplicates from list like iterables

    self._explicit_tests = explicit_tests
    self._iterargs = OrderedDict()
    for singular, plural in spec.iterargs.items():
      values[plural] = tuple(values[plural])
      self._iterargs[singular] = len(values[plural])

    if not values_can_override_spec_names:
      for name in values:
        if spec.has(name):
          raise SetupError('Values entry "{}" collides with spec '\
                      'namespace as a {}'.format(k, spec.get_type(name)))

    self._spec = spec;
    # spec.validate(values)?
    self._values = values;

    self._cache = {
      'conditions': {}
    , 'order': None
    }

  def _check_result(self, result):
    """ Check that the test returned a well formed result:
          a tuple (<Status>, message)

        A boolean Status is allowd and will be transformed to:
        True <Status: PASS>, False <Status: FAIL>

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
      tb = get_traceback()
      error = FailedTestError(e, tb)
      yield (ERROR, error)

  def _exec_test(self, test, args):
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
      result = test(**args)
    except Exception as e:
      tb = get_traceback()
      error = FailedTestError(e, tb)
      result = (FAIL, error)

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

  def _evaluate_condition(self, name, iterargs, path=None):
    if path is None:
      # top level call
      path = []
    if name in path:
      raise CircularDependencyError('Condition "{0}" is a circular dependency in {1}'\
                                  .format(condition, ' -> '.join(path)))
    path.append(name)

    try:
      condition = self._spec.conditions[name]
    except KeyError as err:
      tb = get_traceback()
      error = MissingConditionError(name, err, tb)
      return error, None

    args = self._get_args(condition, iterargs, path)
    path.pop()
    try:
      return None, condition(**args)
    except Exception as err:
      tb = get_traceback()
      error = FailedConditionError(condition, err, tb)
      return error, None

  def _get_condition(self, name, iterargs, path=None):
    # conditions are evaluated lazily
    key = (name, iterargs)
    if key not in self._cache['conditions']:
      err, val = self._evaluate_condition(name, iterargs, path)
      self._cache['conditions'][key] = err, val
    else:
      err, val = self._cache['conditions'][key]
    return err, val

  def get(self, key, iterargs, *args):
    return self._get(key, iterargs, None, *args)

  def get_iterarg(self, name, index):
    """ Used by e.g. reporters """
    plural = self._spec.iterargs[name]
    return self._values[plural][index]

  def _generate_iterargs(self, requirements):
    if not requirements:
      yield tuple()
      return
    name, length = requirements[0]
    for index in range(length):
      current = (name, index)
      for tail in self._generate_iterargs(requirements[1:]):
        yield (current, ) + tail

  def _derive_iterable_condition(self, name, simple=False, path=None):
    # should we cache this?
    condition = self._spec.conditions[name]
    iterargs = self._spec.get_iterargs(condition)

    if not iterargs:
      # without this, we would return just an empty tuple
      raise TypeError('Condition "{}" uses no iterargs.'.format(name))

    # like [('font', 10), ('other', 22)]
    requirements = [(singular, self._iterargs[singular])
                                            for singular in iterargs]
    result = []
    for iterargs in self._generate_iterargs(requirements):
      error, value = self._get_condition(name, iterargs, path)
      if error:
        raise error
      if simple:
        result.append(value)
      else:
        result.append((iterargs, value))
    return tuple(result)

  def _resolve_alias(self, original_name):
    name = original_name
    seen = set()
    path = []
    while name in self._spec.aliases:
      if name in seen:
        raise CircularAliasError('Alias for "{}" has a circular reference'\
                        ' in {}'.format(original_name, '->'.join(path)))
      seen.add(name)
      path.append(name)
      name = self._spec.aliases[name]
    return name

  def _get(self, name, iterargs, path, *args):
    iterargsDict = dict(iterargs)
    has_fallback = bool(len(args))
    if has_fallback:
      fallback = args[0]

    # try this once before resolving aliases and once after
    if name in self._values:
      return self._values[name]

    original_name = name
    name = self._resolve_alias(name)
    if name != original_name and name in self._values:
      return self._values[name]

    nametype = self._spec.get_type(name, None)

    if name in self._values:
      return self._values[name]

    if name in iterargsDict:
      assert nametype == 'iterargs'
      index = iterargsDict[name]
      plural = self._spec.get(name)
      return self._values[plural][index]

    if nametype == 'conditions':
      error, value = self._get_condition(name, iterargs, path)
      if error:
        raise error
      return value

    if nametype == 'derived_iterables':
      condition_name, simple = self._spec.get(name)
      return self._derive_iterable_condition(condition_name, simple, path)

    if has_fallback:
      return fallback

    if original_name != name:
      report_name = '"{}" as "{}"'.format(original_name, name)
    else:
      report_name = '"{}"'.format(name)
    raise MissingValueError('Value {} is undefined.'.format(report_name))

  def _get_args(self, item, iterargs, path=None):
    # iterargs can't be optional arguments yet, we wouldn't generate
    # an execution with an empty list. I don't know if that would be even
    # feasible, so I don't add this complication for the sake of clarity.
    # If this is needed for anything useful, we'll have to figure this out.
    args = {}
    for name in item.args:
      if name in args:
        continue;
      try:
        args[name] = self._get(name, iterargs, path)
      except MissingValueError:
        if name not in item.optionalArgs:
          raise
    return args;

  def _is_negated(self, name):
    stripped = name.strip()
    if stripped.startswith('not '):
      return True, stripped[4:].strip()
    if stripped.startswith('!'):
      return True, stripped[1:].strip()
    return False, stripped

  def _get_test_dependencies(self, test, iterargs):
    unfulfilled_conditions = []
    for condition in test.conditions:
      negate, name = self._is_negated(condition)
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
      if not val:
        unfulfilled_conditions.append(condition)
    if unfulfilled_conditions:
      # This will make the test neither pass nor fail
      status = (SKIP, 'Unfulfilled Conditions: {}'.format(
                                    ', '.join(unfulfilled_conditions)))
      return (status, None)

    try:
      return None, self._get_args(test, iterargs)
    except Exception as error:
      tb = get_traceback()
      status = (ERROR, FailedDependenciesError(test, error, tb))
      return (status, None)

  def _run_test(self, test, iterargs):
    summary_status = None
    # A test is more than just a function, it carries
    # a lot of meta-data for us, in this case we can use
    # meta-data to learn how to call the test (via
    # configuration or inspection, where inspection would be
    # the default and configuration could be used to override
    # inspection results).
    skipped, args = self._get_test_dependencies(test, iterargs)
    # FIXME: test is not a message
    # so, to use it as a message, it should have a "message-interface"
    # TODO: describe generic "message-interface"
    yield STARTTEST, None
    if skipped is not None:
      summary_status = skipped[0]
      # `skipped` is a normal result tuple (status, message)
      # where `status` is either FAIL for unmet dependencies
      # or SKIP for unmet conditions or ERROR. A status of SKIP is
      # never a failed test.
      # ERROR is either a missing dependency or a condition that raised
      # an exception. This shouldn't happen when everyting is set up
      # correctly.
      yield skipped
    else:
      for sub_result in self._exec_test(test, args):
        status, _ = sub_result
        if summary_status is None or status >= summary_status:
          summary_status = status
        yield sub_result
      # The only reason to yield this is to make it testable
      # that a test ran to its end, or, if we start to allow
      # nestable subtests. Otherwise, a STARTTEST would end the
      # previous test implicitly.
      # We can also use it to display status updates to the user.
    if summary_status < PASS:
      summary_status = ERROR
      # got to yield it,so we can see it in the report
      yield ERROR, ('The most significant status of {} was only {} but the '
                   'minimum is {}').format(test, summary_status, PASS)

    yield ENDTEST, summary_status

  # old, more straight forward, but without a point to extract the order
  # def run(self):
  #   for section in self._spec.sections:
  #     yield STARTSECTION, section
  #     for test, iterargs in section.execution_order(self._iterargs
  #                            , getConditionByName=self._spec.conditions.get):
  #       for event in self._run_test(test, iterargs):
  #         yield event;
  #     yield ENDSECTION, None

  @property
  def order(self):
    order = self._cache.get('order', None)
    if order is None:
      order = []
      # section, test, iterargs = identity
      for identity in self._spec.execution_order(self._iterargs,
                                    explicit_tests=self._explicit_tests):
        order.append(identity)
      self._cache['order'] = order = tuple(order)
    return order

  def run(self):
    testrun_summary = Counter()

    # prepare: we'll have less ENDSECTION code in the actual run
    # also, we can prepare section_order tuples
    section = None
    oldsection = None
    section_order = None
    section_orders = []
    for section, test, iterargs in self.order:
      if oldsection != section:
        if oldsection is not None:
          section_orders.append((oldsection, tuple(section_order)))
        oldsection = section
        section_order = []
      section_order.append((test, iterargs))
    if section is not None:
      section_orders.append((section, tuple(section_order)))

    # run
    yield START, self.order, (None, None, None)
    section = None
    old_section = None
    for section, section_order in section_orders:
      section_summary = Counter()
      yield STARTSECTION, section_order, (section, None, None)
      for test, iterargs in section_order:
        for status, message in self._run_test(test, iterargs):
          yield status, message, (section, test, iterargs);
        # after _run_test the last status must be ENDTEST
        assert status == ENDTEST
        # message is the summary_status of the test when status is ENDTEST
        section_summary[message.name] += 1
      yield ENDSECTION, section_summary, (section, None, None)
      testrun_summary.update(section_summary)
    yield END, testrun_summary, (None, None, None)

def distribute_generator(gen, targets_callbacks):
  for item in gen:
    for target in targets_callbacks:
      target(item)

class Section(object):
  def __init__(self, name, tests=None, order=None, description=None):
    self.name = name
    self.description = description
    self._add_test_callbacks = []
    self._tests = [] if tests is None else list(tests)
    # a list of iterarg-names
    self._order = order or []

  def __repr__(self):
    return '<Section: {0}>'.format(self.name)

  @property
  def order(self):
    return self._order[:]

  @property
  def tests(self):
    return self._tests

  def on_add_test(self, callback):
    self._add_test_callbacks.append(callback)

  def add_test(self, test):
    """
    Please use rather `register_test` as a decorator.
    """
    for callback in self._add_test_callbacks:
      callback(self, test)
    self._tests.append(test)
    return test

  def register_test(self, func):
    """
    # register in `special_section`
    @my_section.register_test
    @test(id='com.example.fontbakery/test/0')
    def my_test():
      yield PASS, 'example'
    """
    return self.add_test(func)

class Spec(object):
  def __init__(self
             , sections=None
             , iterargs=None
             , derived_iterables=None
             , conditions=None
             , aliases=None
             , default_section=None):
    '''
      sections: a list of sections, which are ideally ordered sets of
          individual tests.
          It makes no sense to have tests repeatedly, they yield the same
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
         our expectations! These values must be treated asuser input!
    '''
    self._namespace = {}

    self.iterargs = {}
    if iterargs:
      self._add_dict_to_namespace('iterargs', iterargs)

    self.derived_iterables = {}
    if derived_iterables:
      self._add_dict_to_namespace('derived_iterables', derived_iterables)

    self.aliases = {}
    if aliases:
      self._add_dict_to_namespace('aliases', aliases)

    self.conditions = {}
    if conditions:
      self._add_dict_to_namespace('conditions', conditions)

    self._test_registry = {}
    self._sections = OrderedDict()
    if sections:
      for section in sections:
        self.add_section(section)

    if not default_section:
      default_section = sections[0] if len(sections) else Section('Default')
    self._default_section = default_section
    self.add_section(self._default_section)

  _valid_namespace_types = {'iterargs', 'derived_iterables', 'aliases'
                                                          , 'conditions'}

  def _add_dict_to_namespace(self, type, data):
    for key, value in data.items():
      self.add_to_namespace(type, key, value)

  def add_to_namespace(self, type, name, value, force=False):
    if type not in self._valid_namespace_types:
      raise TypeError('Unknow type "{}" valid are: {}'.format(
                          type, ', '.join(self._valid_namespace_types)))
    if name in self._namespace and not force:
      raise NamespaceError('Name "{}" is already registered in "{}".' \
                                                  .format(name, type))
    self._namespace[name] = type
    target = getattr(self, type)
    target[name] = value

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
    marker_fallback = {}
    val = self.get(name, marker_fallback)
    return val is not marker_fallback

  def _get_aggregate_args(self, item, key):
    """
      Get all arguments or mandatory arguments of the item.

      Item is a test or a condition, which means it can be dependent on
      more conditions, this climbs down all the way.
    """
    if not key in ('args', 'mandatoryArgs'):
      raise TypeError('key must be "args" or "mandatoryArgs", got {}').format(key)
    dependencies = list(getattr(item, key))
    if hasattr(item, 'conditions'):
      dependencies += item.conditions
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
      dependencies += [dependency for dependency in getattr(c, key)
                                              if dependency not in args]
    return args

  def get_iterargs(self, item):
    """ Returns a tuple of all iterags for item, sorted by name."""
    # iterargs should always be mandatory, unless there's a good reason
    # not to, which I can't think of right now.
    args = self._get_aggregate_args(item, 'mandatoryArgs')
    return tuple(sorted([arg for arg in args if arg in self.iterargs]))

  def _analyze_tests(self, all_args, tests):
    args = list(all_args)
    args.reverse()
              #(test, signature, scope)
    scopes = [(test, tuple(), tuple()) for test in tests]
    aggregatedArgs = {
      'args': {test.name:self._get_aggregate_args(test, 'args')
                                          for test in tests }
    , 'mandatoryArgs': {test.name: self._get_aggregate_args(test, 'mandatoryArgs')
                                          for test in tests }
    }
    saturated = []
    while args:
      new_scopes = []
      # args_set must contain all current args, hence it's before the pop
      args_set = set(args)
      arg = args.pop()
      for test, signature, scope in scopes:
        if not len(aggregatedArgs['args'][test.name] & args_set):
          # there's no args no more or no arguments of test are
          # in args
          target = saturated
        elif arg == '*test' or arg in aggregatedArgs['mandatoryArgs'][test.name]:
          signature += (1, )
          scope += (arg, )
          target = new_scopes
        else:
          # there's still a tail of args and test requires one of the
          # args in tail but not the current arg
          signature += (0, )
          target = new_scopes
        target.append((test, signature, scope))
      scopes = new_scopes
    return saturated + scopes;

  def _execute_section(self, iterargs, section, items):
    if section is None:
      # base case: terminate recursion
      for test, signature, scope in items:
        yield test, []
    elif not section[0]:
      # no sectioning on this level
      for item in self._execute_scopes(iterargs, items):
        yield item
    elif section[1] == '*test':
      # enforce sectioning by test
      for section_item in items:
        for item in self._execute_scopes(iterargs, [section_item]):
          yield item
    else:
      # section by gen_arg, i.e. ammend with changing arg.
      _, gen_arg = section
      for index in range(iterargs[gen_arg]):
        for test, args in self._execute_scopes(iterargs, items):
          yield test, [(gen_arg, index)] + args

  def _execute_scopes(self, iterargs, scopes):
    generators = []
    items = []
    current_section = None
    last_section = None
    seen = set()
    for test, signature, scope in scopes:
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

      assert current_section not in seen, 'Scopes are badly sorted.{0} in {1}'.format(current_section, seen)

      if current_section != last_section:
        if len(items):
          # flush items
          generators.append(self._execute_section(iterargs, last_section, items))
          items = []
          seen.add(last_section)
        last_section = current_section
      items.append((test, signature, scope))
    # clean up left overs
    if len(items):
      generators.append(self._execute_section(iterargs, current_section, items))

    for item in chain(*generators):
      yield item

  def _section_execution_order(self, section, iterargs
                             , reverse=False
                             , explicit_tests=None):
    """
      order must:
        a) contain all variable args (we're appending missing ones)
        b) not contian duplictates (we're removing repeated items)

      order may contain *iterargs otherwise it is appended
      to the end

      order may contain "*test" otherwise, it is like *test is appended
      to the end (Not done explicitly though).
    """
    stack = section.order[:]
    if '*iterargs' not in stack:
      stack.append('*iterargs')
    stack.reverse()

    full_order = []
    seen = set()
    while len(stack):
      item = stack.pop()
      if item in seen:
        continue
      seen.add(item)
      if item == '*iterargs':
        all_iterargs = list(iterargs.keys())
        # assuming there is a meaningful order
        all_iterargs.reverse()
        stack += all_iterargs
        continue
      full_order.append(item)

    tests = [test for test in section.tests \
                        if not explicit_tests or test.id in explicit_tests]
    scopes = self._analyze_tests(full_order, tests)
    key = lambda (test, signature, scope): signature
    scopes.sort(key=key, reverse=reverse)

    for test, args in self._execute_scopes(iterargs, scopes):
      # this is the iterargs tuple that will be used as a key for caching
      # and so on. we could sort it, to ensure it yields in the same
      # cache locations always, but then again, it is already in a well
      # defined order, by clustering.
      yield test, tuple(args)

  def execution_order(self, iterargs, explicit_tests=None):
    explicit_tests = set() if not explicit_tests else set(explicit_tests)
    for _, section in self._sections.items():
      for test, iterargs in self._section_execution_order(section, iterargs
                                          , explicit_tests=explicit_tests):
        yield (section, test, iterargs)

  def _register_test(self, section, func):
    key = '{}'.format(func)
    other_section = self._test_registry.get(key, None)
    if other_section:
      raise SetupError('Test {} is already registered in {}, tried to '
                       'register in {}.'.format(key, other_section, section))
    self._test_registry[key] = section

  def add_section(self, section):
    key = '{}'.format(section)
    if key in self._sections:
      # the string representation of a section must be unique.
      # string representations of section and test will be used as unique keys
      if self._sections[key] is not section:
        raise SetupError('A section with key {} is already registered'.format(section))
      return
    self._sections[key] = section
    section.on_add_test(self._register_test)
    for test in section.tests:
      self._register_test(section, test)

  def _add_test(self, section, func):
    self.add_section(section)
    section.add_test(func)
    return func

  def register_test(self, section=None, *args, **kwds):
    """
    Usage:
    # register in default section
    @spec.register_test
    @test(id='com.example.fontbakery/test/0')
    def my_test():
      yield PASS, 'example'

    # register in `special_section` also register that section in the spec
    @spec.register_test(special_section)
    @test(id='com.example.fontbakery/test/0')
    def my_test():
      yield PASS, 'example'

    """
    if section and len(kwds) == 0 and callable(section):
      func = section
      section = self._default_section
      return self._add_test(section, func)
    else:
      return partial(self._add_test, section)

  def _add_condition(self, condition, name=None):
    self.add_to_namespace('conditions', name or condition.name, condition)
    return condition

  def register_condition(self, *args, **kwds):
    """
    Usage:

    @spec.register_condition
    @condition
    def myCondition():
      return 123

    #or

    @spec.register_condition(name='my_condition')
    @condition
    def myCondition():
      return 123
    """
    if len(args) == 1 and len(kwds) == 0 and callable(args[0]):
      return self._add_condition(args[0])
    else:
      return partial(self._add_condition, *args, **kwds)


