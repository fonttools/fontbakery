"""
Font Bakery callable is the wrapper for your custom check code.


Separation of Concerns Disclaimer:
While created specifically for running checks on fonts and font-families
this module has no domain knowledge about fonts. It can be used for any
kind of (document) checking. Please keep it so. It will be valuable for
other domains as well.
Domain specific knowledge should be encoded only in the Profile (Checks,
Conditions) and MAYBE in *customized* reporters e.g. subclasses.

"""
import inspect

from functools import wraps, update_wrapper

def cached_getter(func):
  """Decorate a property by executing it at instatiation time and cache the
  result on the instance object."""
  @wraps(func)
  def wrapper(self):
    attribute = f'_{func.__name__}'
    value = getattr(self, attribute, None)
    if value is None:
      value = func(self)
      setattr(self, attribute, value)
    return value
  return wrapper

class FontbakeryCallable:
  def __init__(self, func):
    self._args = None
    self._mandatoryArgs = None
    self._optionalArgs = None
    # must be set by sub class

    # this is set by update_wrapper
    # self.__wrapped__ = func

    # https://docs.python.org/2/library/functools.html#functools.update_wrapper
    # Update a wrapper function to look like the wrapped function.
    # ... assigns to the wrapper function’s __name__, __module__ and __doc__
    update_wrapper(self, func)

  def __repr__(self):
    return'<{}:{}>'.format(type(self).__name__,
                getattr(self, 'id',
                  getattr(self, 'name',
                    super(FontbakeryCallable, self).__repr__()
          )))

  @property
  @cached_getter
  def args(self):
    return self.mandatoryArgs + self.optionalArgs

  @property
  @cached_getter
  def mandatoryArgs(self):
    args = list()
    # make follow_wrapped=True explicit, even though it is the default!
    sig = inspect.signature(self, follow_wrapped=True)
    for name, param in sig.parameters.items():
      if param.default is not inspect.Parameter.empty\
            or param.kind not in (
                  inspect.Parameter.POSITIONAL_OR_KEYWORD
                , inspect.Parameter.POSITIONAL_ONLY):
        # has a default i.e. not mandatory or not positional of any kind
        print(f'{param.default is inspect.Parameter.empty} param.kind: {param.kind} param.default: {param.default} BREAK')
        break
      args.append(name)
    return tuple(args)

  @property
  @cached_getter
  def optionalArgs(self):
    args = list()
    # make follow_wrapped=True explicit, even though it is the default!
    sig = inspect.signature(self, follow_wrapped=True)
    for name, param in sig.parameters.items():
      if param.default is inspect.Parameter.empty:
        # is a mandatory
        continue

      if param.kind not in (
                  inspect.Parameter.POSITIONAL_OR_KEYWORD
                , inspect.Parameter.POSITIONAL_ONLY):
        # no more positional of any kind
        print(f'{param.default is inspect.Parameter.empty} param.kind: {param.kind} param.default: {param.default} BREAK')
        break
      args.append(name)
    return tuple(args)

  def __call__(self, *args, **kwds):
    """ Each call to __call__ with the same arguments must return
    the same result.
    """
    return self.__wrapped__(*args, **kwds)

def get_doc_desc(func, description, documentation):
  doc = inspect.getdoc(func) or ""

  doclines = doc.split('\n')

  if not description:
    description = []
    while len(doclines) and doclines[0]:
      # consume until first empty line
      description.append(doclines[0])
      doclines = doclines[1:]
    # This removes line breaks
    description = ' '.join(description)

  # remove preceding empty lines
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
       force=False
      ):
    super(FontBakeryCondition, self).__init__(func)
    # self.id = id
    self.name = func.__name__ if name is None else name
    self.description, self.documentation = get_doc_desc(
                                        func, description, documentation)
    self.force = force

class FontBakeryCheck(FontbakeryCallable):
  def __init__(
       self,
       checkfunc,
       id,
       advancedMessageSetup=None,
       description=None, # short text, this is mandatory
       documentation=None,
       name = None, # very short text
       conditions=None,
       # arguments_setup=None,
       rationale=None, # long text explaining why this check is needed. Using markdown, perhaps?
       misc_metadata=None, # miscelaneous free-form metadata fields
                           # some of them may be promoted to first-class metadata fields
                           # if they start being used by the check-runner.
                           # Below are a few candidates for that:
       #affects=None, # A list of tuples each indicating Browser/OS/Application
       #              # and the affected versions range.
       #request=None, # An URL to the original request for implementation of this check.
       #              # This is typically a github issue tracker URL.
       #example_failures=None, # A reference to some font or family that originally failed due to
       #                       # the problems that this check tries to detect and report.
       #priority=None
       ):
    """This is the base class for all checks. It will usually
    not be used directly to create check instances, rather
    decorators which are factories will init this class.

    Arguments:
    checkfunc: callable, the check implementation itself.

    id: use reverse domain name notation as a namespace and a
    unique identifier (numbers or anything) but make sure that
    it **never** **ever** changes, that it is **unique until
    eternity**. This is meant to provide a way to track
    burn-down or regressions in a project over time and maybe
    to identify changed/updated check implementations for partial
    profile re-evaluation (in contrast to full profile evaluation)
    if the profile/check changed but not the font.

    description: text, used as one line short description
    read by humans

    name: text, used as a short label read by humans, defaults
    to checkfunc.__name__

    conditions: a list of condition names that must be all true
    in order for this check to be executed. conditions are similar
    to checks, because they also inspect the check subject and they
    also belong to the profile. However, they do not get reported
    directly (there could be checks that report the result of a
    condition). Conditions are **probably** registered and
    referenced by name (like "isVariableFont"). We may accept a
    python function for combining or negating a condition. It
    receives the condition values as arguments, queried by name
    via inspection, and returns True or False.
    TODO: flesh out the format.

    NOTE: `arguments_setup` is postponed until we have a case where it's needed.
    arguments_setup: describes the arguments and position/keyword
    of arguments `checkfunc` expects. Used to override any arguments
    inferred via inspection of `checkfunc`.
    `CheckRunner._get_check_dependencies` will use this information
    to prepare the arguments for this check.
    TODO: flesh out the format.

    documentation: text, used as a detailed documentation,
    read by humans(I suggest to make it markdown formatted).

    advancedMessageSetup: depending on the instance of
    AdvancedMessageType returned by the check, this is the
    counterpart for it. Needed to make sense/use of an
    advancedMessage.
    TODO: Make a proposal for this.
    TODO: This would be used to fix/hotfix issues etc. that means,
      advancedMessageSetup would know how to fix an issue by
      looking at an advancedMessage.
    TODO: The naming is a bit odd.

    priority: inherited from our legacy checks. Need to see if we
    use this at all now.
    """
    super(FontBakeryCheck, self).__init__(checkfunc)
    self.id = id
    self.name = checkfunc.__name__ if name is None else name
    self.conditions = conditions or []
    self.rationale = rationale
    self.description, self.documentation = get_doc_desc(
                                      checkfunc, description, documentation)
    if not self.description:
      raise TypeError('{} needs a description.'.format(type(self).__name__))
    # self._arguments_setup = arguments_setup
    # self._conditions_setup = conditions_setup
    self._advancedMessageSetup = advancedMessageSetup

  # This was problematic. See: https://github.com/googlefonts/fontbakery/issues/2194
  # def __str__(self):
  #  return self.id

def condition(*args, **kwds):
  """Check wrapper, a factory for FontBakeryCondition

  Requires all arguments of FontBakeryCondition but not `func`
  which is passed via the decorator syntax.
  """
  if len(args) == 1 and len(kwds) == 0 and callable(args[0]):
    # used as `@decorator`
    func = args[0]
    return FontBakeryCondition(func)
  else:
    # used as `@decorator()` maybe with args
    def wrapper(func):
      return FontBakeryCondition(func, *args, **kwds)
  return wrapper

def check(*args, **kwds):
  """Check wrapper, a factory for FontBakeryCheck

  Requires all arguments of FontBakeryCheck but not `checkfunc`
  which is passed via the decorator syntax.
  """
  def wrapper(checkfunc):
    return FontBakeryCheck(checkfunc, *args, **kwds)
  return wrapper

# ExpectedValue is not a callable, but it belongs next to check and condition
_NOT_SET = object() # used as a marker
class FontBakeryExpectedValue:
  def __init__(self,
                 name, # unique name in global namespace
                 description=None, # short text, this is mandatory
                 documentation=None, # markdown?
                 default=_NOT_SET, # because None can be a valid default
                 validator=None, # function, see the docstring of `def validate`
                 force=False
                 ):
    self.name = name
    self.description = description
    self.documentation = documentation
    self._default = (True, default) if default is not _NOT_SET else (False, None)
    self._validator = validator
    self.force = force

  def __repr__(self):
    return'<{}:{}>'.format(type(self).__name__, self.name)

  @property
  def has_default(self):
    return self._default[0]

  @property
  def default(self):
    has_default, value = self._default
    if not has_default:
      raise AttributeError(f'{self} has no default value')
    return value

  def validate(self, value):
    """
      returns (bool valid, string|None message)
      If valid is True, message is None or can be ignored.
      If valid is False, message should be a string describing what
      is wrong with value.
    """
    return self._validator(value) if self._validator else (True, None)


class Disabled:
  def __init__(self, func):
    self.func = func


def disable(func):
  return Disabled(func)
