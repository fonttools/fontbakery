# -*- coding: utf-8 -*-
"""
Separation of Concerns Disclaimer:
While created specifically for testing fonts and font-families this
module has no domain knowledge about fonts. It can be used for any kind
of (document) testing. Please keep it so. It will be valuable for other
domains as well.
Domain specific knowledge should be encoded only in the Spec (Tests,
Conditions) and MAYBE in *customized* reporters e.g. subclasses.
"""
from __future__ import absolute_import, print_function, unicode_literals, division
from collections import Counter

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
            , ProtocolViolationError
            )

class FontbakeryReporter(object):
  def __init__(self, is_async=False, runner=None):
    self._started = None
    self._ended = None
    self._order = None
    self._results = [] # ENDTEST events in order of appearance
    self._indexes = {}
    self._tick = 0
    self._counter = Counter()

    # Runner should know if it is async!
    self.is_async = is_async
    self.runner = runner

  def run(self, order=None):
    """
    self.runner must be present
    """
    for event in self.runner.run(order=order):
      self.receive(event)

  @property
  def order(self):
    return self._order

  def _get_key(self, identity):
    section, test, iterargs = identity
    return ('{}'.format(section) if section else section
          , '{}'.format(test) if test else test
          , iterargs
          )

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
      self._started = event

    if status == END:
      self._ended = event

    if status == ENDTEST:
      self._results.append(event)
      self._counter[message.name] += 1
      self._counter['(not finished)'] -= 1

  def receive(self, event):
    status, message, identity = event
    if self._started is None and status != START:
      raise ProtocolViolationError('Received Event before status START: '\
                                      ' {} {}.'.format(status, message))
    if self._ended:
      status, message, identity = event
      raise ProtocolViolationError('Received Event after status END: '\
                                        '{} {}.'.format(status, message))
    self._register(event)
    self._cleanup(event)
    self._output(event)
