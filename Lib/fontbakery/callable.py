# -*- coding: utf-8 -*-
"""
Font Bakery callable is the wrapper for your custom test code.


Separation of Concerns Disclaimer:
While created specifically for testing fonts and font-families this
module has no domain knowledge about fonts. It can be used for any kind
of (document) testing. Please keep it so. It will be valuable for other
domains as well.
Domain specific knowledge should be encoded only in the Spec (Tests,
Conditions) and MAYBE in *customized* reporters e.g. subclasses.

"""
from __future__ import absolute_import, print_function, unicode_literals
import sys
try:
  from inspect import getfullargspec as getargspec
except ImportError:
  from inspect import getargspec

from functools import wraps

def cached_getter(func):
  @wraps(func)
  def wrapper(self):
    attribute = '_{}'.format(func.__name__)
    value = getattr(self, attribute, None)
    if value is None:
      value = func(self)
      setattr(self, attribute, value)
    return value
  return wrapper

class FontbakeryCallable(object):
  def __init__(self, func):
    self._args = None
    self._mandatoryArgs = None
    self._optionalArgs = None
    # must be set by sub class
    self._func = func

  def __repr__(self):
    return'<{0}:{1}>'.format(type(self).__name__,
                getattr(self, 'id',
                  getattr(self, 'name',
                    super(FontbakeryCallable, self).__repr__()
          )))

  @property
  @cached_getter
  def args(self):
    return self.mandatoryArgs + self.optionalArgs

  _ignore_mandatory_args = set()
  @property
  @cached_getter
  def mandatoryArgs(self):
    argspec = getargspec(self._func)
    args = argspec.args[:-len(defaults)] \
             if argspec.defaults is not None else argspec.args

    if self._ignore_mandatory_args:
      args = [arg for arg in args if arg not in self._ignore_mandatory_args]
    return args

  @property
  @cached_getter
  def optionalArgs(self):
    argspec = getargspec(self._func)
    return argspec.args[-len(defaults):] \
             if argspec.defaults is not None else []

  def __call__(self, *args, **kwds):
    """ Each call to __call__ with the same arguments must return
    the same result.
    """
    return self._func(*args, **kwds)

# https://www.python.org/dev/peps/pep-0257/
def trim(docstring):
  """ trim docstrings """
  if not docstring:
      return ''
  # Convert tabs to spaces (following the normal Python rules)
  # and split into a list of lines:
  lines = docstring.expandtabs().splitlines()
  # Determine minimum indentation (first line doesn't count):
  indent = sys.maxint
  for line in lines[1:]:
      stripped = line.lstrip()
      if stripped:
          indent = min(indent, len(line) - len(stripped))
  # Remove indentation (first line is special):
  trimmed = [lines[0].strip()]
  if indent < sys.maxint:
      for line in lines[1:]:
          trimmed.append(line[indent:].rstrip())
  # Strip off trailing and leading blank lines:
  while trimmed and not trimmed[-1]:
      trimmed.pop()
  while trimmed and not trimmed[0]:
      trimmed.pop(0)
  # Return a single string:
  return '\n'.join(trimmed)

def get_doc_desc(func, description, documentation):
  doc = trim(func.__doc__)
  doclines = doc.split('\n')

  if not description:
    description = doclines[0] or None
    doclines = doclines[1:]
    # remove empty lines?
    while len(doclines) and not doclines[0]:
      doclines = doclines[1:]

  if not documentation and len(doclines):
    documentation = '\n'.join(doclines) or None

  return description, documentation

class FontBakeryCondition(FontbakeryCallable):
  def __init__(
       self,
       func,
       # id,
       name = None, # very short text
       description = None, # short text
       documentation=None, # long text, markdown?
      ):
    super(FontBakeryCondition, self).__init__(func)
    # self.id = id
    self.name = func.__name__ if name is None else name
    self.description, self.documentation = get_doc_desc(
                                        func, description, documentation)

class FontBakeryTest(FontbakeryCallable):
  def __init__(
       self,
       testfunc,
       id,
       description=None, # short text, this is mandatory
       name = None, # very short text
       conditions=None,
       # arguments_setup=None,
       documentation=None, # long text, markdown?
       advancedMessageSetup=None,
       priority=None
       ):
    """This is the base class for all tests. It will usually
    not be used directly to create test instances, rather
    decorators which are factories will init this class.

    Arguments:
    testfunc: callable, the test implementation itself.

    id: use reverse domain name notation as a namespace and a
    unique identifier (numbers or anything) but make sure that
    it **never** **ever** changes, that it is **unique until
    eternity**. This is meant to provide a way to track
    burn-down or regressions in a project over time and maybe
    to identify changed/updated test implementations for partial
    spec re-evaluation (in contrast to full spec evaluation) if
    the spec/test changed but not the font.

    description: text, used as one line short description
    read by humans

    name: text, used as a short label read by humans, defaults
    to testfunc.__name__

    conditions: a list of condition names that must be all true
    in order for this test to be executed. conditions are similar
    to tests, because they also inspect the test subject and they
    also belong to the spec. However, they do not get reported
    directly (there could be tests that report the result of a
    condition). Conditions are **probably** registered and
    referenced by name (like "isVariableFont"). We may accept a
    python function for combining or negating a condition. It
    receives the condition values as arguments, queried by name
    via inspection, and returns True or False.
    TODO: flesh out the format.

    NOTE: `arguments_setup` is postponed until we have a case where it's needed.
    arguments_setup: describes the arguments and position/keyword
    of arguments `testfunc` expects. Used to override any arguments
    inferred via inspection of `testfunc`.
    `TestRunner._get_test_dependencies` will use this information
    to prepare the arguments for this test.
    TODO: flesh out the format.

    documentation: text, used as a detailed documentation,
    read by humans(I suggest to make it markdown formatted).

    advancedMessageSetup: depending on the instance of
    AdvancedMessageType returned by the test, this is the
    counterpart for it. Needed to make sense/use of an
    advancedMessage.
    TODO: Make a proposal for this.
    TODO: This would be used to fix/hotfix issues etc. that means,
      advancedMessageSetup would know how to fix an issue by
      looking at an advancedMessage.
    TODO: The naming is a bit odd.

    priority: inherted from our legacy tests. Need to see if we
    use this at all now.
    """
    super(FontBakeryTest, self).__init__(testfunc)
    self.id = id
    self.name = testfunc.__name__ if name is None else name
    self.conditions = conditions or []
    self.description, self.documentation = get_doc_desc(
                                      testfunc, description, documentation)
    if not self.description:
      raise TypeError('{} needs a description.'.format(type(self).__name__))
    # self._arguments_setup = arguments_setup
    # self._conditions_setup = conditions_setup
    self._advancedMessageSetup = advancedMessageSetup

def condition(*args, **kwds):
  """Test wrapper, a factory for FontBakeryCondition

  Requires all arguments of FontBakeryCondition but not `func`
  which is passed via the decorator syntax.
  """
  if len(args) == 1 and len(kwds) == 0 and callable(args[0]):
    # used as `@decorator`
    func = args[0]
    return wraps(func)(FontBakeryCondition(func))
  else:
    # used as `@decorator()` maybe with args
    def wrapper(func):
      return wraps(func)(FontBakeryCondition(func, *args, **kwds))
  return wrapper

def test(*args, **kwds):
  """Test wrapper, a factory for FontBakeryTest

  Requires all arguments of FontBakeryTest but not `testfunc`
  which is passed via the decorator syntax.
  """
  def wrapper(testfunc):
    return wraps(testfunc)(FontBakeryTest(testfunc, *args, **kwds))
  return wrapper
