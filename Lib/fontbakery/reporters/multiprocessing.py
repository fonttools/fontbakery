"""
Separation of Concerns Disclaimer:
While created specifically for checking fonts and font-families this
module has no domain knowledge about fonts. It can be used for any kind
of (document) checking. Please keep it so. It will be valuable for other
domains as well.
Domain specific knowledge should be encoded only in the Profile (Checks,
Conditions) and MAYBE in *customized* reporters e.g. subclasses.

"""
from collections import OrderedDict
from fontbakery.reporters import FontbakeryReporter
from fontbakery.checkrunner import (  # NOQA
              INFO
            , WARN
            , ERROR
#            , STARTSECTION
            , STARTCHECK
            , SKIP
            , PASS
            , FAIL
            , ENDCHECK
#            , ENDSECTION
#            , START
            , END
            , DEBUG
#            , Status
            )
from fontbakery.message import Message

name2status = {status.name:status for status in (
                            DEBUG, PASS, SKIP, INFO, WARN, FAIL, ERROR)}

# somehowsimilar to DashbordWorkerReporter of Font Bakery Dashboard
class WorkerToQueueReporter(FontbakeryReporter):
  def __init__(self, queue, profile, ticks_to_flush = None, **kwd):
    super().__init__(**kwd)
    self._queue = queue
    self._profile = profile
    self.ticks_to_flush = ticks_to_flush or 1

    self._current = None
    self._collectedChecks = None

  def _register(self, event):
    super()._register(event)
    status, message, identity = event
    _section, check, _iterargs = identity
    if status == END:
      self.flush()
      return

    if not check:
      return

    key = self._profile.serialize_identity(identity)

    if status == STARTCHECK:
        self._current = {
            'statuses': []
        }

    if status == ENDCHECK:
        # Do more? Anything more would make access easier but also be a
        # derivative of the actual data, i.e. not SSOT. Calculating (and
        # thus interpreting) results for the checks is probably not too
        # expensive to do it on the fly.
        self._current['result'] = message.name
        self._save_result(key, self._current)
        self._current = None

    if status >= DEBUG:
      # message can be a lot here, currently we know about:
      #    string, an Exception, a Message. Probably we should leave it
      #    like this. Message should be the ultimate answer if it's not
      #    an Exception or a string.
      # turn everything in a fontbakery/Message like object
      # `code` may be used for overwriting special failing statuses
      # otherwise, code must be none
      #
      # Optional keys are:
      #  "code": used to explicitly overwrite specific (FAIL) statuses
      #  "traceback": only provided if message is an Excepion and likely
      #               if status is "ERROR"
      log = {'status': status.name}

      if hasattr(message, 'traceback'):
        # message is likely a FontbakeryError if this is not None
        log['traceback'] = message.traceback
      if isinstance(message, Message):
        # Ducktyping could be a valid option here.
        # in that case, a FontbakeryError could also provide a `code` attribute
        # which would allow to skip that error explicitly. However
        # ERROR statuses should never be skiped explicitly, the cause
        # of the error must be repaired!
        log.update(message.getData())
      else:
        log['message'] = f'{message}'
      self._current['statuses'].append(log)

  def _save_result(self, key, check_result):
    """ send check_result to the queue"""
    if self._collectedChecks is None:
      # order is not really relevant in multiprocessing, however, we keep
      # it as long as possible, could be good for debugging.
      self._collectedChecks = OrderedDict()
    self._collectedChecks[key] = check_result
    if len(self._collectedChecks) >= self.ticks_to_flush:
      self.flush()

  def flush(self):
    if self._collectedChecks:
      self._queue.put(tuple(self._collectedChecks.items()))
    self._collectedChecks = None


def deserialize_queue_check(profile, key, check_data):
  identity = profile.deserialize_identity(key)
  yield STARTCHECK, None, identity  ## = event

  for log in check_data['statuses']:
    status = name2status[log['status']]
    if 'code' in log:
      message = Message(log['code'], log['message'])
    elif 'traceback' in log:
      # not to happy with this generic exception, let's se how it plays out
      message = Exception(log['message'])
      setattr(message, 'traceback', log['traceback'])
    else:
      message = log['message']
    yield status, message, identity ### = event

  status = name2status[check_data['result']]
  yield ENDCHECK, status, identity ## = event
