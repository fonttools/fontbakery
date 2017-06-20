# -*- coding: <encoding name> -*-
from __future__ import absolute_import, print_function, unicode_literals
import sys
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

test_statuses = [ERROR, FAIL, SKIP, PASS]
test_statuses.sort(key=lambda s:s.weight)

class FontbakeryReporter(object):
  def __init__(self, runner=None):
    self.runner = runner

  def run(self):
    """
    self.runner must be present
    """
    for event in self.runner.run():
      self.receive(event)

  def receive_sync(event):
    # superclass must implement this if receive_async is not implemented
    # will receive events of the test runner protocol in order
    pass

  def receive_async(event):
    # superclass may implement this
    # will receive events of the test runner protocol out of order!
    # If this is implemented, receive_sync shouldn't be needed, because
    # it should handle the case of sync in-order receives just the same.
    pass

class TerminalProgress(FontbakeryReporter):
  def __init__(self, runner=None, stdout=sys.stdout, stderr=sys.stderr):
    super(TerminalReporter, self).__init__(runner)
    self.stdout = stdout
    self.stderr = stderr

  #use order to create a progressbar for each section
  #maybe create a subprogressbar for each font, if font is used
  #"font" would have to be specified as iterarg
  def receive_async(self, event):
    pass

class TerminalReporter(FontbakeryReporter):
  """
  yield for each test
  on endtest, make a summary of the test and yield that

  """
  def __init__(self, runner=None, print_func=print):
    super(TerminalReporter, self).__init__(runner)
    self._print = print_func

  def receive_sync(self, event):
    status, message, (section, test, iterargs) = event
    if status == START:
      order = message
      print('Start ... running {} individual test executions.'.format(len(order)))
      print()
      return

    if status == STARTSECTION:
      order = message
      print ('='*8, 'START {}'.format(section),'='*8)
      print('{} tests in section'.format(len(order)))
      print()
      return

    if status == STARTTEST:
      print('>> {} {} with {}'.format(test.name, test.id, iterargs))
      print('  ', test.description)
      return

    if status in (INFO, WARN, PASS, SKIP, FAIL, ERROR):
      print(' * {}: {}'.format(status.name, message))
      if (status == ERROR or status == FAIL) and hasattr(message, 'traceback'):
        print('        ','\n         '.join(message.traceback.split('\n')))
      return

    if status == ENDTEST:
      print('   Result: {}'.format(message.name))
      return

    if status == ENDSECTION:
      print()
      print('Section results:')
      print()
      for s in test_statuses:
        print('    {}: {}'.format(s.name, message[s.name]))
      print()
      print ('='*8, 'END {}'.format(section),'='*8)
      return

    if status == END:
      print()
      print('Testsuite results:')
      print()
      for s in test_statuses:
        print('    {}: {}'.format(s.name, message[s.name]))
      print()
      print ('DONE!')
      return

    print('Unexpected status: ', status)



