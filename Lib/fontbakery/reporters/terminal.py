"""
Font Bakery reporters/terminal can report the events of the Font Bakery
CheckRunner Protocol to the terminal (or by pipe to files). It understands
both, the synchronous and asynchronous execution model.

Separation of Concerns Disclaimer:
While created specifically for checking fonts and font-families this
module has no domain knowledge about fonts. It can be used for any kind
of (document) checking. Please keep it so. It will be valuable for other
domains as well.
Domain specific knowledge should be encoded only in the Profile (Checks,
Conditions) and MAYBE in *customized* reporters e.g. subclasses.

"""
import sys
import os
import subprocess
from collections import Counter
from functools import partial
import builtins # using this to override print function somewhere
from io import StringIO
from time import time

from fontbakery.reporters import FontbakeryReporter
from fontbakery.checkrunner import (  # NOQA
              INFO
            , WARN
            , ERROR
            , STARTSECTION
            , STARTCHECK
            , SKIP
            , PASS
            , FAIL
            , ENDCHECK
            , ENDSECTION
            , START
            , END
            , DEBUG
            , Status
            )

statuses = (
              INFO
            , WARN
            , ERROR
            , STARTSECTION
            , STARTCHECK
            , SKIP
            , PASS
            , FAIL
            , ENDCHECK
            , ENDSECTION
            , START
            , END
            , DEBUG
            )
# these are displayed in the result counters
check_statuses = [ERROR, FAIL, SKIP, PASS, WARN, INFO]
check_statuses.sort(key=lambda s:s.weight, reverse=True)


def formatStatus(theme, status, text=None):
  # status can be a status or a string
  name = getattr(status, 'name', status)
  if text is None:
    text = name
  try:
    return theme[name](text)
  except KeyError:
    return text

CUPCAKE = r"""
                           ,@.
                         ,@.@@,.
                   ,@@,.@@@.  @.@@@,.
                 ,@@. @@@.     @@. @@,.
         ,@@@.@,.@.              @.  @@@@,.@.@@,.
    ,@@.@.     @@.@@.            @,.    .@’ @’  @@,
  ,@@. @.          .@@.@@@.  @@’                  @,
 ,@.  @@.                                          @,
 @.     @,@@,.     ,                             .@@,
 @,.       .@,@@,.         .@@,.  ,       .@@,  @, @,
 @.                             .@. @ @@,.    ,      @
  @,.@@.     @,.      @@,.      @.           @,.    @’
   @@||@,.  @’@,.       @@,.  @@ @,.        @’@@,  @’
      \\@@@@’  @,.      @’@@@@’   @@,.   @@@’ //@@@’
       |||||||| @@,.  @@’ |||||||  |@@@|@||  ||
        \\\\\\\  ||@@@||  |||||||  |||||||  //
         |||||||  ||||||  ||||||   ||||||  ||
          \\\\\\  ||||||  ||||||  ||||||  //
           ||||||  |||||  |||||   |||||  ||
            \\\\\  |||||  |||||  |||||  //
             |||||  ||||  |||||  ||||  ||
              \\\\  ||||  ||||  ||||  //
               ||||||||||||||||||||||||

         No check is failing. Get a cupcake!
       <<Art by Tony de Marco, July 26, 2018>>
"""

class ThrottledOut:
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
      self.flush()

  def flush(self, draw_progress=True):
    """call this at the very end, so that we can output the rest"""
    reset_progressbar = None
    if self._draw_progressbar and draw_progress:
      progressbar, reset_progressbar = self._draw_progressbar()
      self._buffer.append(progressbar)

    for line in self._buffer:
      self._outFile.write(line)
    #self._outFile.flush() needed?
    self._buffer = []
    if reset_progressbar:
      # first thing on next flush is to reset the current progressbar
      self._buffer.append(reset_progressbar)
    self._current_ticks = 0
    self._last_flush_time = time()


from fontbakery.constants import LIGHT_THEME

class TerminalProgress(FontbakeryReporter):
  def __init__(self, print_progress=True
                   , stdout=sys.stdout
                   , structure_threshold=None
                   , theme=LIGHT_THEME
                   , succinct=None
                   , cupcake=True
                     # a tuple of structural statuses to be skipped
                     # e.g. (STARTSECTION, ENDSECTION)
                   , skip_status_report=None
                   , **kwd):
    super(TerminalProgress, self).__init__(**kwd)

    self.theme = theme
    self.succinct = succinct
    self._print_progress = stdout.isatty() and print_progress

    if self._print_progress:
      self.stdout = ThrottledOut(stdout, holdback_time=1/24, max_ticks=10
                               , draw_progressbar=self.draw_progressbar)
    else:
      self.stdout = stdout

    self._progressbar = []
    self._cupcake = cupcake
    self._skip_status_report = skip_status_report or tuple()
    if structure_threshold:
      self._structure_threshold = min(START.weight, structure_threshold)
    else:
      self._structure_threshold = START.weight
    if self._structure_threshold % 2:
      # always include the according START status
      self._structure_threshold -= 1

  def _register(self, event):
    super(TerminalProgress, self)._register(event)
    status, message, identity = event
    if status == ENDCHECK and self._print_progress:
      self._set_progress_event(event)

  def _output(self, event):
    super(TerminalProgress, self)._output(event)
    text = self._render_event(event)
    if text:
      self.stdout.write(text)
    elif self._print_progress:
      # the empty string will change the ticks counter when self.stdout is a ThrottledOut
      self.stdout.write('')
    status, _, _ = event
    if status == END and self._print_progress:
      # this flush is only relevant when self.stdout is a ThrottledOut
      self.stdout.flush(False)

  def _render_event(self, event):
    status, message, (section, check, iterargs) = event
    output = StringIO()
    print = partial(builtins.print, file=output)

    if not status.weight >= self._structure_threshold \
                                      or status in self._skip_status_report:
      return output.getvalue()

    if status == START:
      order = message
      print('Start ... running {} individual check executions.'.format(len(order)))

    if status == END:
      if self._print_progress:
        print(self._draw_progressbar())#.encode('utf-8'))
      print('')
      if self._cupcake and len(self._order) \
              and self._counter[ERROR.name] + self._counter[FAIL.name] == 0 \
              and self._counter[PASS.name] > 20:
        print(self.theme["cupcake"](CUPCAKE))
      print('DONE!')
    return output.getvalue()

  def _set_order(self, order):
    super(TerminalProgress, self)._set_order(order)
    if self._print_progress:
      # set/reset
      self._progressbar = list('.'*len(order))
      for event in self._results:
        self._set_progress_event(event)

  def _set_progress_event(self, event):
      _, status, identity = event
      index = self._get_index(identity)
      self._progressbar[index] = formatStatus(self.theme,
                                              status,
                                              status.name[0])

  def _get_index(self, identity):
    index = super(TerminalProgress, self)._get_index(identity)
    if self._print_progress and len(self._indexes) < len(self._progressbar):
      self._progressbar.append('.')
    return index

  def _reset_progress(self, num_linebeaks):
    # BACKSPACE = u'\b'
    TOLEFT = '\u001b[1000D' # Move all the way left (max 1000 steps
    CLEARLINE = '\u001b[2K'    # Clear the line
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

    # together with unicode_literals `str('status')` seems the best
    # py2 and py3 compatible solution
    status = type(str('status'), (object,), dict(count=0,progressbar=[]))
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
    for item in self._progressbar:
      append(item)
    append(']')
    percentstring = f'{percent:3d}%'
    append(percentstring, len(percentstring), ' ')
    return ''.join(progressbar)


  def draw_progressbar(self):
    # tty size
    if sys.platform == "win32":
      mode = subprocess.Popen(
          "mode", shell=True, stdout=subprocess.PIPE).stdout.readlines()
      columns_entry = [s for s in mode if b"Columns" in s]
      columns = int(columns_entry[0].split()[1])
    else:
      columns = int(os.popen('stty size').read().split()[1])
    # this is the amout of space the spinner takes when rendered in the tty
    # NOTE: the color codes are not taking space in the tty, so we can't
    # just take the length of `spinner`.
    # 1 for the spinner + 1 for the separating space
    progressbar = self._draw_progressbar(columns, len_prefix=2)
    counter = _render_results_counter(self.theme, self._counter)

    spinnerstates = ' ░▒▓█▓▒░'
    spinner = spinnerstates[self._tick % len(spinnerstates)]
    spinner = self.theme["spinner"](spinner)

    rendered = f'\n{counter}\n\n{spinner} {progressbar}\n'
    num_linebeaks = rendered.count('\n')
    return rendered, self._reset_progress(num_linebeaks)

def _render_results_counter(theme, counter):
  format = '    {}: {}'.format
  result = []

  seen = set()
  for s in check_statuses:
    name = s.name
    seen.add(name)
    result.append(format(formatStatus(theme, s), counter[name]))

  # there may be custom statuses
  for name in counter:
    if name not in seen:
      seen.add(name)
      result.append(format(formatStatus(theme, name), counter[name]))
  return '\n'.join(result)

class TerminalReporter(TerminalProgress):
  """
  yield for each check
  on endcheck, make a summary of the check and yield that
  """
  def __init__(self, collect_results_by=None
                   , check_threshold=None
                   , log_threshold=None
                   , **kwd):
    super(TerminalReporter, self).__init__(**kwd)
    self.results_by = collect_results_by
    self._collected_results = {}
    self._event_buffers = {}

    # logs can occur at any point in the logging protocol
    # especially DEBUG, INFO, WARNING and ERROR
    # FAIL, PASS and SKIP are only expected within checks though
    # Log statuses have weights >= 0
    log_threshold = log_threshold if type(log_threshold) is not Status \
                                  else log_threshold.weight
    self._log_threshold = min(ERROR.weight + 1 , max(0, log_threshold))

    # Use this to silence the output checks in async mode, it also activates
    # async mode if turned off.
    # You can't silence whole checks in sync output, as the events are
    # rendered as soon as they happen, you can however silence some log
    # messages in sync mode, use log_threshold for this.
    # default: no DEBUG output
    check_threshold = check_threshold if type(check_threshold) is not Status \
                                    else check_threshold.weight
    self._check_threshold = min(ERROR.weight + 1, max(PASS.weight, check_threshold))

    # if this is used we must use async rendering, otherwise we can't
    # suppress the output of checks, because we only know the final
    # status after ENDCHECK.
    self._render_async = self.is_async or check_threshold is not None

  def _register(self, event):
    super(TerminalReporter, self)._register(event)
    status, message, (section, check, iterargs) = event

    if self.results_by and status == ENDCHECK:

      key = check.id if self.results_by == '*check' \
                      else dict(iterargs).get(self.results_by, None)
      if key not in self._collected_results:
        self._collected_results[key] = Counter()
      self._collected_results[key][message.name] += 1

  def _render_event_sync(self, print, event):
    status, message, (section, check, iterargs) = event

    if not status.weight >= self._structure_threshold \
                                      or status in self._skip_status_report:
      return

    if status == START:
      text = super(TerminalReporter, self)._render_event(event)
      if text:
        self.stdout.write(text)

    if status == STARTSECTION:
      order = message
      print('='*8, str(section),'='*8)
      print('{} {} in section'.format(len(order)
                          , len(order) == 1 and 'check' or 'checks' ))
      print('')

    if status == STARTCHECK:
      if self.runner:
        formatted_iterargs = tuple(
            ('{}[{}]'.format(*item), self.runner.get_iterarg(*item))
                                                    for item in iterargs)
      else:
        formatted_iterargs = iterargs

      if self.succinct:
        with_string = "All fonts"
        if formatted_iterargs != ():
          with_string = os.path.basename(f"{formatted_iterargs[0][1]}")

        print((" >> Check:   {}\n"
               "    Desc:    {}\n"
               "    Files:   {}").format(
          self.theme["check-id"](check.id),
          self.theme["description"](check.description),
          with_string))

      else:
        # Omit printing of iterargs when there's none of them:
        with_string = ""
        if formatted_iterargs != ():
          with_string = f"with {formatted_iterargs[0][1]}"

        print((' >> {}\n'
               '    {}\n'
               '    {}\n').format(
          self.theme["check-id"](check.id),
          self.theme["description"](check.description),
          with_string))

        if check.rationale:
          from fontbakery.utils import text_flow, unindent_rationale
          content = unindent_rationale(check.rationale).strip()
          print('    ' + self.theme["rationale-title"]("  Rationale:" + " " * 64) + '\n'
                + text_flow(content,
                            width=76,
                            indent=4,
                            left_margin=2,
                            space_padding=True,
                            text_color=self.theme["rationale-text"]))

    # Log statuses have weights >= 0
    # log_statuses = (INFO, WARN, PASS, SKIP, FAIL, ERROR, DEBUG)
    if status.weight >= self._log_threshold:
      print('    * {}: {}'.format(formatStatus(self.theme, status),
                                    message))
      if hasattr(message, 'traceback'):
        print('        ','\n         '.join(message.traceback.split('\n')))


    if status == ENDCHECK:
      if not self.succinct:
        print('\n')
      print('    Result: {}\n'.format(formatStatus(self.theme, message)))

    if status == ENDSECTION:
      print('')
      print('Section results:')
      print('')
      print(_render_results_counter(self.theme, message))
      print('')
      print ('='*8, f'END {section}','='*8)

    if status == END:
      print('')
      if self.results_by:
        print('Collected results by', self.results_by)
        for key in self._collected_results:
          if self.results_by == '*check':
            val = key
          elif key is not None and self.runner:
            val = self.runner.get_iterarg(self.results_by, key)
          elif key is not None:
            val = key
          else:
            val = f'(not using "{self.results_by}")'
          print(f'{self.results_by}: {val}')
          print(_render_results_counter(self.theme, self._collected_results[key]))
          print('')

      print('Total:')
      print('')
      print(_render_results_counter(self.theme, message))
      print('')

      # same end message as parent
      text = super(TerminalReporter, self)._render_event(event)
      if text:
        print(text)

      print(f"    {self.theme['header']('Meaning of check results:')}\n"
            f"\n"
            f"    An {formatStatus(self.theme, 'ERROR')} is something"
            f" wrong with FontBakery itself, possibly a bug.\n"
            f"    A {formatStatus(self.theme, 'FAIL')} is a problem"
            f" with the font that must be fixed.\n"
            f"    A {formatStatus(self.theme, 'WARN')} is something"
            f" that you should consider addressing.\n"
            f"    An {formatStatus(self.theme, 'INFO')} result simply"
            f" prints something useful. Typically stats.\n"
            f"    A {formatStatus(self.theme, 'PASS')} means the font looks good"
            f" for the given checking routine.\n"
            f"    And a {formatStatus(self.theme, 'SKIP')} happens when the check"
            f" does not apply to the given font.\n"
            f"\n"
            f"    If you get {formatStatus(self.theme, 'ERROR')}s,"
            f" please help us improve the tool by reporting them at\n"
            f"    {self.theme['url']('https://github.com/googlefonts/fontbakery/issues')}\n"
            f"\n"
            f"    (but other kinds of bug reports and/or\n"
            f"     feature requests are also always welcome, of course!)\n")

    if status not in statuses:
      print('-'*8, status , '-'*8)

  def _render_event_async(self, print, event):
    status, message, identity = event
    (section, check, iterargs) = identity
    key = self._get_key(identity)
    logs = self._event_buffers.get(key, None)
    if logs is None:
      self._event_buffers[key] = logs = {
          'start': None
        , 'logs': []
        , 'end': None
      }
    if status is STARTSECTION:
      self._render_event_sync(print, event)
    # (STARTSECTION), STARTCHECK
    elif status.weight < 0 and status.weight % 2 == 0 :
      logs['start'] = event
    # ENDCHECK, ENDSECTION
    elif status.weight < 0 and status.weight % 2 == 1 :
      logs['end'] = event
    else:
      logs['logs'].append(event)

    if status == ENDCHECK and message.weight >= self._check_threshold \
          or status == ENDSECTION:
      for e in [logs['start']] + logs['logs'] + [logs['end']]:
        if e is not None:
          self._render_event_sync(print, e)

    if not section:
      self._render_event_sync(print, event)

  def _render_event(self, event):
    status, message, (section, check, iterargs) = event
    output = StringIO()
    print = partial(builtins.print, file=output)

    if self._render_async:
      self._render_event_async(print, event)
    else:
      self._render_event_sync(print, event)

    return output.getvalue()
