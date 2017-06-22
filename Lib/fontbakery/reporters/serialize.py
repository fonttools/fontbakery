# -*- coding: utf-8 -*-
"""
Font Bakery reporters/serialize can report the events of the Font Bakery
TestRunner Protocol to a serializeable document. It uses json as a default
target.

Separation of Concerns Disclaimer:
While created specifically for testing fonts and font-families this
module has no domain knowledge about fonts. It can be used for any kind
of (document) testing. Please keep it so. It will be valuable for other
domains as well.
Domain specific knowledge should be encoded only in the Spec (Tests,
Conditions) and MAYBE in *customized* reporters e.g. subclasses.
"""

from .terminal import FontbakeryReporter

def SerializeReporter(FontbakeryReporter):
  def __init__(self
                   , **kwd):
    super(SerializeReporter, self).__init__(**kwd)
    self._sections = {}
    self._items = {}
    self._doc = None

  def _set_metadata(self, identity, item):
    section, test, iterargs = identity
    # If section is None this is the main doc.
    # If test is None this is `section`
    # otherwise this `test`
    pass

  def _register(self, event):
    status, message, identity = event
    section, test, iterargs = identity
    key = self._get_key(identity)

    # not item == True when item is empty
    item = self._items.get(key, {})
    if not item:
      # init
      if status in (START, END) and not item:
        item.update(dict(result=None, sections=[]))
      if status in (STARTSECTION, ENDSECTION):
        item.update(dict(key=key, result=None, tests=[]))
      if test:
        item.update(dict(key=key, result=None, logs=[]))
      self._set_metadata(identity, item)

    if status in (END, ENDSECTION):
      item['result'] = message # is a Counter
    if status in ENDTEST:
      item['result'] = message.name # is a Status
    if status >= DEBUG:
      item['logs'].append(dict(
                          status= status.name
                        , message= '{}'.message
                        , traceback= getattr(message, 'traceback', None)
                        )
                      )

  # todo: within the sections
  # add a cluster_by layer
  # so we can have a clustering by font!
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
      sectionDoc.tests.append(self._items[key])
      if sectionKey not in seen:
        seen.add(sectionKey)
        doc.sections.append(sectionDoc)
    self._doc = doc
    return doc
