# -*- coding: utf-8 -*-
"""
Font Bakery reporters/terminal can report the events of the Font Bakery
TestRunner Protocol to the terminal (or by pipe to files). It understands
both, the synchronous and asynchronous execution model.

Separation of Concerns Disclaimer:
While created specifically for testing fonts and font-families this
module has no domain knowledge about fonts. It can be used for any kind
of (document) testing. Please keep it so. It will be valuable for other
domains as well.
Domain specific knowledge should be encoded only in the Spec (Tests,
Conditions) and MAYBE in *customized* reporters e.g. subclasses.

"""
from __future__ import absolute_import, print_function, unicode_literals, division
import sys
from collections import Counter
from functools import partial
try:
  from cStringIO import StringIO
except ImportError:
  # Python 3
  from StringIO import StringIO

# using this to override print function somewhere
try:
  import __builtin__
except ImportError:
  # Python 3
  import builtins as __builtin__


from fontbakery.testrunner import (
              INFO
            , WARN
            , ERROR
            , STARTSECTION
            , STARTTEST
            , SKIP
            , PASS
            , FAIL
            , ENDTEST
            , ENDSECTION
            , START
            , END
            )

statuses = (
              INFO
            , WARN
            , ERROR
            , STARTSECTION
            , STARTTEST
            , SKIP
            , PASS
            , FAIL
            , ENDTEST
            , ENDSECTION
            , START
            , END
            )
test_statuses = [ERROR, FAIL, SKIP, PASS]
test_statuses.sort(key=lambda s:s.weight, reverse=True)

RED_STR = '\033[1;31;40m{}\033[0m'.format
RED_BACKGROUND = '\033[1;37;41m{}\033[0m'.format
GREEN_STR = '\033[1;32;40m{}\033[0m'.format
YELLOW_STR = '\033[1;33;40m{}\033[0m'.format
BLUE_STR = '\033[1;34;40m{}\033[0m'.format
MAGENTA_STR = '\033[1;35;40m{}\033[0m'.format
CYAN_STR = '\033[1;36;40m{}\033[0m'.format
WHITE_STR = '\033[1;37;40m{}\033[0m'.format

def formatStatus(status, text=None, color=False):
  # status can be a status or a string
  name = getattr(status, 'name', status)
  if text is None:
    text = name
  if not color:
    return text
  try:
    return {
      INFO.name: CYAN_STR
    , WARN.name: YELLOW_STR
    , ERROR.name: RED_BACKGROUND
    , SKIP.name: BLUE_STR
    , PASS.name: GREEN_STR
    , FAIL.name: RED_STR
    }[name](text)
  except KeyError:
    return text

UNICORN = r"""
              \
               \
    EUREKA!     \\
                 \\
                  >\/7
              _.-(6'  \
             (=___._/` \
                  )  \ |
                 /   / |
                /    > /
               j    < _\
           _.-' :      ``.
           \ r=._\        `.
          <`\\_  \         .`-.
           \ r-7  `-. ._  ' .  `\
            \`,      `-.`7  7)   )
             \/         \|  \'  / `-._
                        ||    .'
                         \\  (
                          >\  >
                      ,.-' >.'
                     <.'_.''
              All tests are passing.
    <<Art by Colin J. Randall, cjr, 10mar02>>
"""

class FontbakeryReporter(object):
  def __init__(self, is_async=False, runner=None):
    self._order = None
    self._results = []
    self._indexes = {}
    self._tick = 0
    self._counter = Counter()

    self.is_async = is_async
    self.runner = runner

  def run(self):
    """
    self.runner must be present
    """
    for event in self.runner.run():
      self.receive(event)

  @property
  def order(self):
    return self._order

  def _get_key(self, identity):
    section, test, iterargs = identity
    return '{}'.format(section), '{}'.format(test), iterargs

  def _get_index(self, identity):
    key = self._get_key(identity)
    try:
      return self._indexes[key]
    except KeyError:
      self._indexes[key] = len(self._indexes)
      return self._indexes[key]

  def _set_order(self, order):
    self._order = order
    length = len(order)
    self._counter['(not finished)'] = length - len(self._results)
    self._indexes = dict(zip(map(self._get_key, order), range(length)))

  def _cleanup(self, (status, message, identity)):
    pass

  def _output(self, (status, message, identity)):
    pass

  def _register(self, event):
    status, message, identity = event
    self._tick += 1
    if status == START:
      self._set_order(message)

    if status == ENDTEST:
      self._results.append(event)
      self._counter[message.name] += 1
      self._counter['(not finished)'] -= 1

  def receive(self, event):
    self._register(event)
    self._cleanup(event)
    self._output(event)


class TerminalProgress(FontbakeryReporter):
  def __init__(self, print_progress=True
                   , stdout=sys.stdout
                   , structure_threshold=None
                   , usecolor=True
                   , unicorn=True
                   , **kwd):
    super(TerminalProgress, self).__init__(**kwd)

    self.stdout = stdout
    # must be a tty for this!
    self._use_color = usecolor
    self._print_progress = self.stdout.isatty() and print_progress
    self._progressbar = []
    self._last_progress_lines = 0
    self._unicorn = unicorn

    self._structure_threshold = min(START.weight, structure_threshold) \
                        or START.weight # if structure_threshold is None
    if self._structure_threshold % 2:
      # always include the according START status
      self._structure_threshold -= 1

  def _cleanup(self, (status, message, identity)):
    super(TerminalProgress, self)._cleanup((status, message, identity))
    self.reset_last_progress()

  def _register(self, event):
    super(TerminalProgress, self)._register(event)
    status, message, identity = event
    if status == ENDTEST and self._print_progress:
      self._set_progress_event(event)

  def _output(self, event):
    super(TerminalProgress, self)._output(event)
    text = self._render_event(*event)
    if text:
      self.stdout.write(text)
    status, _, _ = event
    if status != END and self._print_progress:
      self.draw_progress()

  def _render_event(self, status, message, identity):
    output = StringIO()
    print = partial(__builtin__.print, file=output)

    if status == START and status.weight >= self._structure_threshold:
      order = message
      print('Start ... running {} individual test executions.'.format(len(order)))

    if status == END and status.weight >= self._structure_threshold:
      if self._print_progress:
        print(self.draw_progressbar().encode('utf-8'))
      print()
      if self._unicorn and self._counter[PASS.name] == len(self._results):
        unicorn = UNICORN
        if self._use_color:
          unicorn = MAGENTA_STR(UNICORN)
        print(unicorn)
      print('DONE!')

    return output.getvalue()

  def _set_order(self, order):
    super(TerminalProgress, self)._set_order(order)
    if self._print_progress:
      # set/reset
      self._progressbar = list('.'*len(order))
      map(self._set_progress_event, self._results)

  def _set_progress_event(self, event):
      _, status, identity = event;
      index = self._get_index(identity)
      self._progressbar[index] = formatStatus(status, status.name[0]
                                                , color=self._use_color)

  def _get_index(self, identity):
    index = super(TerminalProgress, self)._get_index(identity)
    if self._print_progress and len(self._indexes) < len(self._progressbar):
      self._progressbar.append('.')
    return index

  def reset_last_progress(self):
    BACKSPACE = u'\b'
    TOLEFT = u'\u001b[1000D' # Move all the way left (max 1000 steps
    CLEARLINE = u'\u001b[2K'    # Clear the line
    UP =  '\u001b[1A' # moves cursor 1 up
    reset = (CLEARLINE + UP) * self._last_progress_lines + TOLEFT
    self.stdout.write(reset)
    self.stdout.flush()

  def draw_progressbar(self):
    if self._order == None:
      total = len(self._results)
    else:
      total = max(len(self._order), len(self._results))

    percent = int(round(len(self._results)/total*100)) if total else 0
    barformat = '[{0}] {1: 3d}% '.format
    return barformat(''.join(self._progressbar), percent)

  def draw_progress(self):
    progressbar = self.draw_progressbar()
    counter = _render_results_counter(self._counter, color=self._use_color)

    spinnerstates = ' ░▒▓█▓▒░'
    spinner = spinnerstates[self._tick % len(spinnerstates)]
    if self._use_color:
      spinner = GREEN_STR(spinner)

    rendered = '\n{0}\n\n{2} {1}'.format(counter, progressbar, spinner)
    self._last_progress_lines = rendered.count('\n')
    self.stdout.write(rendered)
    self.stdout.flush()

    import time
    time.sleep(.05)

def _render_results_counter(counter,color=False):
  format = '    {}: {}'.format
  result = []

  seen = set()
  for s in test_statuses:
    name = s.name
    seen.add(name)
    result.append(format(formatStatus(s, color=color), counter[name]))

  # there may be custom statuses
  for name in counter:
    if name not in seen:
      seen.add(name)
      result.append(format(formatStatus(name,color=color), counter[name]))
  return '\n'.join(result)

class TerminalReporter(TerminalProgress):
  """
  yield for each test
  on endtest, make a summary of the test and yield that
  """
  def __init__(self, collect_results_by=None
                   , test_threshold=None
                   , log_threshold=None
                   , **kwd):
    super(TerminalReporter, self).__init__(**kwd)
    self.results_by = collect_results_by
    self._collected_results = {}
    self._event_buffers = {}

    # logs can occur at any point in the logging protocol
    # especially INFO, WARNING and ERROR
    # FAIL, PASS and SKIP are only expected within tests though
    # Log statuses have weights >= 0
    self._log_threshold = min(ERROR.weight + 1 , max(0, log_threshold))

    # Use this to silence the output tests
    self._test_threshold = min(ERROR.weight + 1, max(PASS.weight, test_threshold))

    # if this is used we must use async rendering, otherwise we can't
    # suppress the output of tests, because we only know the final
    # status after ENDTEST.
    self._render_async = self.is_async or test_threshold is not None

  def _register(self, event):
    super(TerminalReporter, self)._register(event)
    status, message, (section, test, iterargs) = event

    if self.results_by and status == ENDTEST:
      key = dict(iterargs).get(self.results_by, None)
      if key not in self._collected_results:
        self._collected_results[key] = Counter()
      self._collected_results[key][message.name] += 1

  def _render_event_sync(self, print, event):
    status, message, (section, test, iterargs) = event

    structure_threshold = status.weight >= self._structure_threshold

    if status == START and structure_threshold:
      text = super(TerminalReporter, self)._render_event(*event)
      if text:
        self.stdout.write(text)

    if status == STARTSECTION and structure_threshold:
      order = message
      print ('='*8, '{}'.format(section),'='*8)
      print('{} tests in section'.format(len(order)))
      print()

    if status == STARTTEST and structure_threshold:
      print('>> {} {} with {}'.format(test.name, test.id, iterargs))
      print('  ', test.description)

    # Log statuses have weights >= 0
    # log_statuses = (INFO, WARN, PASS, SKIP, FAIL, ERROR)
    if status.weight >= self._log_threshold and structure_threshold:
      print(' * {}: {}'.format(formatStatus(status, color=self._use_color), message))
      if (status == ERROR or status == FAIL) and hasattr(message, 'traceback'):
        print('        ','\n         '.join(message.traceback.split('\n')))

    if status == ENDTEST and structure_threshold:
      print('   Result: {}'.format(formatStatus(message, color=self._use_color)))

    if status == ENDSECTION and structure_threshold:
      print()
      print('Section results:')
      print()
      print(_render_results_counter(message, color=self._use_color))
      print()
      print ('='*8, 'END {}'.format(section),'='*8)

    if status == END and structure_threshold:
      print()
      if self.results_by:
        print('Collected results by', self.results_by)
        for index in self._collected_results:
          if self.runner:
            val = self.runner.get_iterarg(self.results_by, index)
          else:
            val = index
          print('{}: {}'.format(self.results_by, val))
          print(_render_results_counter(self._collected_results[index],
                                                color=self._use_color))
          print()

      print('Total:')
      print()
      print(_render_results_counter(message, color=self._use_color))
      print()

      # same end message as parent
      text = super(TerminalReporter, self)._render_event(*event)
      print(text)

    if status not in statuses and structure_threshold:
      print('-'*8, status , '-'*8)

  def _render_event_async(self, print, event):
    status, message, identity = event
    (section, test, iterargs) = identity
    key = self._get_key(identity)
    logs = self._event_buffers.get(key, None)
    if logs is None:
      self._event_buffers[key] = logs = {
          'start': None
        , 'logs': []
        , 'end': None
      }

    # STARTSECTION, STARTTEST
    if status.weight < 0 and status.weight % 2 == 0 :
      logs['start'] = event
    # ENDTEST, ENDSECTION
    elif status.weight < 0 and status.weight % 2 == 1 :
      logs['end'] = event
    else:
      logs['logs'].append(event)

    if status == ENDTEST and message.weight >= self._test_threshold \
          or status == ENDSECTION:
      for e in [logs['start']] + logs['logs'] + [logs['end']]:
        self._render_event_sync(print, e)

    if not section:
      self._render_event_sync(print, event)

  def _render_event(self, *event):
    status, message, (section, test, iterargs) = event
    output = StringIO()
    print = partial(__builtin__.print, file=output)

    if self._render_async:
      self._render_event_async(print, event)
    else:
      self._render_event_sync(print, event)
    return output.getvalue()
