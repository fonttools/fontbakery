# -*- coding: utf-8 -*-
"""
Font Bakery reporters/serialize can report the events of the Font Bakery
TestRunner Protocol to a serializeable document e.g. for usage with `json.dumps`.

Separation of Concerns Disclaimer:
While created specifically for testing fonts and font-families this
module has no domain knowledge about fonts. It can be used for any kind
of (document) testing. Please keep it so. It will be valuable for other
domains as well.
Domain specific knowledge should be encoded only in the Spec (Tests,
Conditions) and MAYBE in *customized* reporters e.g. subclasses.
"""
from __future__ import absolute_import, print_function, unicode_literals, division

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
            )
from fontbakery.reporters import FontbakeryReporter

class SerializeReporter(FontbakeryReporter):
  """
  usage:
  >> sr = SerializeReporter(runner=runner, collect_results_by='font')
  >> sr.run()
  >> import json
  >> print(json.dumps(sr.getdoc(), sort_keys=True, indent=4))
  """


  def __init__(self, collect_results_by=None
                   , **kwd):
    super(SerializeReporter, self).__init__(**kwd)
    self._results_by = collect_results_by
    self._items = {}
    self._doc = None

    # used when self._results_by is set
    # this way we minimize our knowledge of the specification
    self._max_cluster_by_index = None
    self._observed_tests = {}

  def _set_metadata(self, identity, item):
    section, test, iterargs = identity
    # If section is None this is the main doc.
    # If test is None this is `section`
    # otherwise this `test`
    pass

  def _register(self, event):
    super(SerializeReporter, self)._register(event)
    status, message, identity = event
    section, test, iterargs = identity
    key = self._get_key(identity)

    # not item == True when item is empty
    item = self._items.get(key, {})
    if not item:
      self._items[key] = item
      # init
      if status in (START, END) and not item:
        item.update(dict(result=None, sections=[]))
        if self._results_by:
          # give the consumer a clue that/how the sections
          # are structured differently.
          item['clusteredBy'] = self._results_by
      if status in (STARTSECTION, ENDSECTION):
        item.update(dict(key=key, result=None, tests=[]))
      if test:
        item.update(dict(key=key, result=None, logs=[]))
        if self._results_by:
          if self._results_by == '*test':
            if test.id not in self._observed_tests:
              self._observed_tests[test.id] = len(self._observed_tests)
            index = self._observed_tests[test.id]
            value = test.id
          else:
            index = dict(iterargs).get(self._results_by, None)
            value = None
            if self.runner:
              value = self.runner.get_iterarg(self._results_by, index)

          if index is not None:
            self._max_cluster_by_index = max(index, self._max_cluster_by_index)

          item['clustered'] = {
              'name': self._results_by
            , 'index': index # None if this test did not require self.results_by
          }
          if value: # Not set if self.runner was not defined on initialization
            item['clustered']['value'] = value
      self._set_metadata(identity, item)

    if status in (END, ENDSECTION):
      item['result'] = message # is a Counter
    if status == ENDTEST:
      item['result'] = message.name # is a Status
    if status >= DEBUG:
      item['logs'].append(dict(
                          status= status.name
                        , message= '{}'.format(message)
                        , traceback= getattr(message, 'traceback', None)
                        )
                      )

  def getdoc(self):
    if not self._ended:
      raise Exception('Can\'t create doc before END status was recevived.')
    if self._doc is not None:
      return self._doc
    doc = self._items[self._get_key((None, None, None))]
    seen = set()
    sectionorder = []
    # this puts all in the original order
    for identity in self._order:
      key = self._get_key(identity)
      section, _, _ = identity
      sectionKey = self._get_key((section, None, None))
      sectionDoc = self._items[sectionKey]

      test = self._items[key]
      if self._results_by:
        if not len(sectionDoc['tests']):
          clusterlen = self._max_cluster_by_index + 1
          if self._results_by != '*test':
            # + 1 for rests bucket
            clusterlen += 1
          sectionDoc['tests'] = [[] for _ in range(clusterlen)]
        index = test['clustered']['index']
        if index is None:
          # last element collects unclustered
          index = -1
        sectionDoc['tests'][index].append(test)
      else:
        sectionDoc['tests'].append(test)
      if sectionKey not in seen:
        seen.add(sectionKey)
        doc['sections'].append(sectionDoc)
    self._doc = doc
    return doc

