"""
Font Bakery reporters/serialize can report the events of the Font Bakery
CheckRunner Protocol to a serializeable document e.g. for usage with `json.dumps`.

Separation of Concerns Disclaimer:
While created specifically for checking fonts and font-families this
module has no domain knowledge about fonts. It can be used for any kind
of (document) checking. Please keep it so. It will be valuable for other
domains as well.
Domain specific knowledge should be encoded only in the Profile (Checks,
Conditions) and MAYBE in *customized* reporters e.g. subclasses.
"""
from fontbakery.checkrunner import (
              DEBUG
            , STARTSECTION
            , ENDSECTION
            , ENDCHECK
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
    # this way we minimize our knowledge of the profile
    self._max_cluster_by_index = None
    self._observed_checks = {}

  def _set_metadata(self, identity, item):
    section, check, iterargs = identity
    # If section is None this is the main doc.
    # If check is None this is `section`
    # otherwise this `check`
    pass

  def _register(self, event):
    super(SerializeReporter, self)._register(event)
    status, message, identity = event
    section, check, iterargs = identity
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
        item.update(dict(key=key, result=None, checks=[]))
      if check:
        item.update(dict(key=key, result=None, logs=[]))
        if self._results_by:
          if self._results_by == '*check':
            if check.id not in self._observed_checks:
              self._observed_checks[check.id] = len(self._observed_checks)
            index = self._observed_checks[check.id]
            value = check.id
          else:
            index = dict(iterargs).get(self._results_by, None)
            value = None
            if self.runner:
              value = self.runner.get_iterarg(self._results_by, index)

          if index is not None:
            if self._max_cluster_by_index is not None:
              self._max_cluster_by_index = max(index, self._max_cluster_by_index)
            else:
              self._max_cluster_by_index = index

          item['clustered'] = {
              'name': self._results_by
            , 'index': index # None if this check did not require self.results_by
          }
          if value: # Not set if self.runner was not defined on initialization
            item['clustered']['value'] = value
      self._set_metadata(identity, item)

    if check:
      item['description'] = check.description
      if check.rationale:
        item['rationale'] = check.rationale
      if item["key"][2] != ():
        item['filename'] = self.runner.get_iterarg(*item["key"][2][0])

    if status in (END, ENDSECTION):
      item['result'] = message # is a Counter
    if status == ENDCHECK:
      item['result'] = message.name # is a Status
    if status >= DEBUG:
      item['logs'].append(dict(
                          status= status.name
                        , message= f'{message}'
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

      check = self._items[key]
      if self._results_by:
        if not len(sectionDoc['checks']):
          clusterlen = self._max_cluster_by_index + 1
          if self._results_by != '*check':
            # + 1 for rests bucket
            clusterlen += 1
          sectionDoc['checks'] = [[] for _ in range(clusterlen)]
        index = check['clustered']['index']
        if index is None:
          # last element collects unclustered
          index = -1
        sectionDoc['checks'][index].append(check)
      else:
        sectionDoc['checks'].append(check)
      if sectionKey not in seen:
        seen.add(sectionKey)
        doc['sections'].append(sectionDoc)
    self._doc = doc
    return doc
