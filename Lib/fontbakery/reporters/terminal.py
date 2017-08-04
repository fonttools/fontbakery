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
import sys, os
from math import ceil
from collections import Counter
from functools import partial
try:
  from cStringIO import StringIO
except ImportError:
  # Python 3
  from StringIO import StringIO

from time import time

# using this to override print function somewhere
try:
  import __builtin__
except ImportError:
  # Python 3
  import builtins as __builtin__

from fontbakery.reporters import FontbakeryReporter

from fontbakery.testrunner import (
              DEBUG
            , INFO
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
            , Status
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
# these are displayed in the result counters
test_statuses = [ERROR, FAIL, SKIP, PASS, WARN, INFO]
test_statuses.sort(key=lambda s:s.weight, reverse=True)

RED_STR =        '\033[1;31;40m{}\033[0m'.format
RED_BACKGROUND = '\033[1;37;41m{}\033[0m'.format
GREEN_STR =      '\033[1;32;40m{}\033[0m'.format
YELLOW_STR =     '\033[1;33;40m{}\033[0m'.format
BLUE_STR =       '\033[1;34;40m{}\033[0m'.format
MAGENTA_STR =    '\033[1;35;40m{}\033[0m'.format
CYAN_STR =       '\033[1;36;40m{}\033[0m'.format
WHITE_STR =      '\033[1;37;40m{}\033[0m'.format

def highlight(color, text, use_color=False):
  if use_color:
    return color(text)
  else:
    return text

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
              No test is failing.
    <<Art by Colin J. Randall, cjr, 10mar02>>
"""

class ThrottledOut(object):
  def __init__(self, outFile, holdback_time=None, max_ticks=0, draw_progressbar=None):
    """ holdback_time: float, 1.0 = 1 second"""
    self._outFile = outFile
    self._holdback_time = holdback_time
    self._last_flush_time = None
    self._buffer = []
    self._draw_progressbar = draw_progressbar
    self._current_ticks = 0
    self._max_ticks = max_ticks

  def write(self, data):
    """only put to stdout every now and then"""
    self._buffer.append(data)
    self._current_ticks += 1
    # first entry ever will be flushed immediately

    flush=False
    if self._last_flush_time is None or \
                (self._holdback_time is None and self._max_ticks == 0):
      flush = True
    elif self._max_ticks and self._current_ticks >= self._max_ticks or \
         self._holdback_time and time() - self._holdback_time >= self._last_flush_time:
      flush=True

    if flush:
      self.flush();

  def flush(self, draw_progress=True):
    """call this at the very end, so that we can output the rest"""
    reset_progressbar = None
    if self._draw_progressbar and draw_progress:
      progressbar, reset_progressbar = self._draw_progressbar();
      self._buffer.append(progressbar)

    map(self._outFile.write, self._buffer)
    #self._outFile.flush() needed?
    self._buffer = []
    if reset_progressbar:
      # first thing on next flush is to reset the current progressbar
      self._buffer.append(reset_progressbar)
    self._current_ticks = 0
    self._last_flush_time = time()

class TerminalProgress(FontbakeryReporter):
  def __init__(self, print_progress=True
                   , stdout=sys.stdout
                   , structure_threshold=None
                   , usecolor=True
                   , unicorn=True
                   , **kwd):
    super(TerminalProgress, self).__init__(**kwd)

    # must be a tty for this!
    self._use_color = usecolor
    self._print_progress = stdout.isatty() and print_progress

    if self._print_progress:
      self.stdout = ThrottledOut(stdout, holdback_time=1/24, max_ticks=10
                               , draw_progressbar=self.draw_progressbar)
    else:
      self.stdout = stdout

    self._progressbar = []
    self._unicorn = unicorn

    self._structure_threshold = min(START.weight, structure_threshold) \
                        or START.weight # if structure_threshold is None
    if self._structure_threshold % 2:
      # always include the according START status
      self._structure_threshold -= 1

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
    elif self._print_progress:
      # the empty string will change the ticks counter when self.stdout is a ThrottledOut
      self.stdout.write('')
    status, _, _ = event
    if status == END and self._print_progress:
      # this flush is only relevant when self.stdout is a ThrottledOut
      self.stdout.flush(False)

  def _render_event(self, status, message, identity):
    output = StringIO()
    print = partial(__builtin__.print, file=output)

    if status == START and status.weight >= self._structure_threshold:
      order = message
      print('Start ... running {} individual test executions.'.format(len(order)))

    if status == END and status.weight >= self._structure_threshold:
      if self._print_progress:
        print(self._draw_progressbar().encode('utf-8'))
      print()
      if self._unicorn and len(self._order) \
              and self._counter[ERROR.name] + self._counter[FAIL.name] == 0:
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

  def _reset_progress(self, num_linebeaks):
    BACKSPACE = u'\b'
    TOLEFT = u'\u001b[1000D' # Move all the way left (max 1000 steps
    CLEARLINE = u'\u001b[2K'    # Clear the line
    UP =  '\u001b[1A' # moves cursor 1 up
    reset = (CLEARLINE + UP) * num_linebeaks + TOLEFT
    return reset

  def _draw_progressbar(self, columns=None, len_prefix=0, right_margin=0):
    """
    if columns is None, don't insert any extra line breaks
    """
    if self._order == None:
      total = len(self._results)
    else:
      total = max(len(self._order), len(self._results))

    percent = int(round(len(self._results)/total*100)) if total else 0

    needs_break = lambda count: columns and count > columns \
                                and (count % (columns - right_margin))

    status = type(b'status', (object,), dict(count=0,progressbar=[]))
    def _append(status, item, length=1, separator=''):
      # * assuming a standard item will take one column in the tty
      # * length must not be bigger than columns (=very narrow columns)
      progressbar = status.progressbar
      if needs_break(status.count + length + len(separator)):
        progressbar.append('\n')
        status.count = 0
      else:
        progressbar.append(separator)
      status.count += length + len(separator)
      progressbar.append(item)
    append=partial(_append, status)
    progressbar = status.progressbar

    append('', len_prefix)
    append('[')
    map(append, self._progressbar)
    append(']')
    percentstring = '{0:3d}%'.format(percent)
    append(percentstring, len(percentstring), ' ')
    return ''.join(progressbar)


  def draw_progressbar(self):
    # tty size
    rows, columns = map(int, os.popen('stty size', 'r').read().split())
    # this is the amout of space the spinner takes when rendered in the tty
    # NOTE: the color codes are not taking space in the tty, so we can't
    # just take the length of `spinner`.
    # 1 for the spinner + 1 for the separating space
    len_prefix = 2;
    progressbar = self._draw_progressbar(columns, len_prefix=2)
    counter = _render_results_counter(self._counter, color=self._use_color)

    spinnerstates = ' ░▒▓█▓▒░'
    spinner = spinnerstates[self._tick % len(spinnerstates)]
    if self._use_color:
      spinner = GREEN_STR(spinner)

    rendered = '\n{0}\n\n{2} {1}\n'.format(counter, progressbar, spinner)
    num_linebeaks = rendered.count('\n')
    return rendered, self._reset_progress(num_linebeaks)

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
    # especially DEBUG, INFO, WARNING and ERROR
    # FAIL, PASS and SKIP are only expected within tests though
    # Log statuses have weights >= 0
    log_threshold = log_threshold if type(log_threshold) is not Status \
                                  else log_threshold.weight
    self._log_threshold = min(ERROR.weight + 1 , max(0, log_threshold))

    # Use this to silence the output tests in async mode, it also activates
    # async mode if turned off.
    # You can't silence whole tests in sync output, as the events are
    # rendered as soon as they happen, you can however silence some log
    # messages in sync mode, use log_threshold for this.
    # default: no DEBUG output
    test_threshold = test_threshold if type(test_threshold) is not Status \
                                    else test_threshold.weight
    self._test_threshold = min(ERROR.weight + 1, max(PASS.weight, test_threshold))

    # if this is used we must use async rendering, otherwise we can't
    # suppress the output of tests, because we only know the final
    # status after ENDTEST.
    self._render_async = self.is_async or test_threshold is not None

  def _register(self, event):
    super(TerminalReporter, self)._register(event)
    status, message, (section, test, iterargs) = event

    if self.results_by and status == ENDTEST:

      key = test.id if self.results_by == '*test' \
                      else dict(iterargs).get(self.results_by, None)
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
      if self.runner:
        formatted_iterargs = tuple(
            ('{0}[{1}]'.format(*item), self.runner.get_iterarg(*item))
                                                    for item in iterargs)
      else:
        formatted_iterargs = iterargs

      # Omit printing of iterargs when there's none of them:
      with_string = ""
      if formatted_iterargs != ():
        with_string = " with {}".format(formatted_iterargs)

      print('>> {}{}'.format(
        highlight(CYAN_STR, test.id, use_color=self._use_color), with_string))

      print('  ',
        highlight(MAGENTA_STR, test.description, use_color=self._use_color))

    # Log statuses have weights >= 0
    # log_statuses = (INFO, WARN, PASS, SKIP, FAIL, ERROR, DEBUG)
    if status.weight >= self._log_threshold and structure_threshold:
      print(' * {}: {}'.format(formatStatus(status, color=self._use_color)
                                               , message).encode('utf-8'))
      if hasattr(message, 'traceback'):
        print('        ','\n         '.join(message.traceback.split('\n')))

    if status == ENDTEST and structure_threshold:
      print('\n   Result: {}\n'.format(formatStatus(message, color=self._use_color)))

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
        for key in self._collected_results:
          if self.results_by == '*test':
            val = key
          elif key is not None and self.runner:
            val = self.runner.get_iterarg(self.results_by, key)
          elif key is not None:
            val = key
          else:
            val = '(not using "{}")'.format(self.results_by)
          print('{}: {}'.format(self.results_by, val))
          print(_render_results_counter(self._collected_results[key],
                                                color=self._use_color))
          print()

      print('Total:')
      print()
      print(_render_results_counter(message, color=self._use_color))
      print()

      # same end message as parent
      text = super(TerminalReporter, self)._render_event(*event)
      if text:
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
