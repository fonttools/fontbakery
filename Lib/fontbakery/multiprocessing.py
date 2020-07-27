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
from contextlib import contextmanager
from functools import partial
from multiprocessing import Process, Queue
import queue

from fontbakery.reporters import FontbakeryReporter
from fontbakery.checkrunner import (  # NOQA
              INFO
            , WARN
            , ERROR
            , STARTCHECK
            , SKIP
            , PASS
            , FAIL
            , ENDCHECK
            , END
            , DEBUG
            , CheckRunner
            , session_protocol_generator
            , drive_session_protocol
            , get_profile_from_module_locator
            )
from fontbakery.message import Message


################
# WORKER/CHILD #
################

name2status = {status.name:status for status in \
               (DEBUG, PASS, SKIP, INFO, WARN, FAIL, ERROR)}

# Similar to DashbordWorkerReporter of Font Bakery Dashboard.
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

#This is the inverse of the serialization in WorkerToQueueReporter
def check_protocol_from_worker_data(profile, key_check_data):
    key, check_data = key_check_data
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

def _worker_jobs_generator(jobs_queue, profile, reporter):
    while True:
        try:
            job = jobs_queue.get(False)
        except queue.Empty:
            # This removes a race condition.
            # The queue looks empty, apparently that must not be the actual case,
            # but since the parent process is counting results to decide when
            # it's done, we flush here, besides the value of ticks_to_flush.
            # before.
            reporter.flush()
            # No held back results anymore, so parent process has complete control
            # and we won't block it in blocking waiting mode.
            job = jobs_queue.get(True)
        yield profile.deserialize_identity(job)

def multiprocessing_worker(jobs_queue, results_queue, profile_module_locator
                         , runner_kwds):
    profile = get_profile_from_module_locator(profile_module_locator)
    runner = CheckRunner(profile, **runner_kwds)
    reporter = WorkerToQueueReporter( results_queue
                                    , profile=profile
                                    , runner=runner
                                    , ticks_to_flush=5
                                    )

    next_check_gen = _worker_jobs_generator(jobs_queue, profile, reporter)
    runner.run_externally_controlled(reporter.receive, next_check_gen)

#####################
# DISPATCHER/PARENT #
#####################

def _results_generator(results_queue, len_results):
    count_results = 0
    while True:
        result_list = results_queue.get()
        for result in result_list:
            yield result
            count_results += 1
        if count_results >= len_results:
            return

@contextmanager
def _multiprocessing_checkrunner(jobs, process_count, *args):
    jobs_queue = Queue()
    results_queue = Queue()
    for job in jobs:
        jobs_queue.put(job)
    len_jobs = len(jobs)

    try:
        processes = []
        for _ in range(process_count):
            p = Process(target=multiprocessing_worker,
                        # NOTE: stuff is pickled here, but that
                        # seems to be no problem despite of
                        # e.g. pickling a profile (see #2982),
                        # which was fixed by using profile.module_locator
                        # instead. The other arguments seem easier
                        # to pickle.
                        args=(jobs_queue, results_queue, *args))
            processes.append(p)
            p.start()
        yield _results_generator(results_queue, len_jobs) # next_check_gen
    finally:
        for p in processes:
            p.terminate()
            p.join()

def multiprocessing_runner(process_count, runner, runner_kwds):
    # process_count is a positive int, never 0 at this point
    assert process_count > 0
    profile = runner.profile
    joblist = list(profile.serialize_order(runner.order))

    session_gen = session_protocol_generator(
                      partial(check_protocol_from_worker_data, profile),
                      runner.order)
    with _multiprocessing_checkrunner(joblist,
                                      process_count,
                                      profile.module_locator,
                                      runner_kwds) as next_check_gen:
        yield from drive_session_protocol(session_gen, next_check_gen)
