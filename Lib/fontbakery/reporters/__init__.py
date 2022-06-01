"""
Separation of Concerns Disclaimer:
While created specifically for checking fonts and font-families this
module has no domain knowledge about fonts. It can be used for any kind
of (document) checking. Please keep it so. It will be valuable for other
domains as well.
Domain specific knowledge should be encoded only in the Profile (Checks,
Conditions) and MAYBE in *customized* reporters e.g. subclasses.
"""
from collections import Counter

from fontbakery.checkrunner import (
              DEBUG
            , INFO
            , WARN
            , ERROR
            , STARTCHECK
            , SKIP
            , PASS
            , FAIL
            , ENDCHECK
            , SECTIONSUMMARY
            , START
            , END
            )
from fontbakery.errors import ProtocolViolationError

class FontbakeryReporter:
    def __init__(self, is_async=False, runner=None, output_file=None, loglevels=None):
        self._started = None
        self._ended = None
        self._order = None
        self._results = [] # ENDCHECK events in order of appearance
        self._indexes = {}
        self._tick = 0
        self._counter = Counter()
        self.loglevels = loglevels

        # Runner should know if it is async!
        self.is_async = is_async
        self.runner = runner

        self._worst_check_status = None
        self.output_file = output_file

    def run(self, order=None):
        """
        self.runner must be present
        """
        for event in self.runner.run(order=order):
            self.receive(event)

    @property
    def order(self):
        return self._order

    def write(self):
        if self.output_file is not None:
            raise NotImplementedError(
                f'{type(self)} does not implement the "write" method, '
                'but it has an "output_file".'
            )
        # reporters without an output file do nothing here

    @staticmethod
    def _get_key(identity):
        section, check, iterargs = identity
        return (str(section) if section else section
              , str(check) if check else check
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
        self._order = tuple(order)
        length = len(self._order)
        self._counter['(not finished)'] = length - len(self._results)
        self._indexes = dict(zip(map(self._get_key, self._order), range(length)))

    def _cleanup(self, event):
        pass

    def _output(self, event):
        pass

    def _register(self, event):
        status, message, identity = event
        self._tick += 1
        if status == START:
            self._set_order(message)
            self._started = event

        if status == END:
            self._ended = event

        if status == ENDCHECK:
            self._results.append(event)
            self._counter[message.name] += 1
            self._counter['(not finished)'] -= 1

    @property
    def worst_check_status(self):
        """ Returns a status or None if there was no check result """
        return self._worst_check_status

    def receive(self, event):
        status, message, identity = event
        if self._started is None and status != START:
            raise ProtocolViolationError(f'Received Event before status START:'
                                         f' {status} {message}.')
        if self._ended:
            status, message, identity = event
            raise ProtocolViolationError(f'Received Event after status END:'
                                         f' {status} {message}.')

        if status is ENDCHECK and (self._worst_check_status is None \
                                   or self._worst_check_status < message):
            # we only record ENDCHECK, because check runner may in the future
            # have tools to upgrade/downgrade the actually worst status
            # this should be future proof.
            self._worst_check_status = message

        self._register(event)
        self._cleanup(event)
        self._output(event)
