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
from typing import Iterable, Optional
from dataclasses import dataclass

from fontbakery.checkrunner import CheckRunner
from fontbakery.status import END, ENDCHECK, START, Status
from fontbakery.errors import ProtocolViolationError
from fontbakery.events import EndCheckEvent, Identity, Event, StartEvent, EndEvent


@dataclass
class FontbakeryReporter:
    is_async: bool = False
    runner: Optional[CheckRunner] = None
    output_file: Optional[str] = None
    loglevels: Optional[Iterable[Status]] = None
    collect_results_by: Optional[str] = None
    succinct: bool = False

    def __post_init__(self):
        self._started = None
        self._ended = None
        self._order = None
        self._results = []  # ENDCHECK events in order of appearance
        self._indexes = {}
        self._tick = 0
        self._counter = Counter()
        self._worst_check_status = None
        self._minimum_weight = min(status.weight for status in self.loglevels)
        self._collected_results = {}

    def omit_loglevel(self, msg) -> bool:
        """Determine if message is below log level."""
        return Status(msg).weight < self._minimum_weight

    def run(self, order=None):
        """
        self.runner must be present
        """
        for event in self.runner.run(order=order):
            self.receive(event)

    def write(self):
        if self.output_file is not None:
            raise NotImplementedError(
                f'{type(self)} does not implement the "write" method, '
                'but it has an "output_file".'
            )
        # reporters without an output file do nothing here

    def _get_index(self, identity):
        assert isinstance(identity, Identity)
        key = identity.key
        try:
            return self._indexes[key]
        except KeyError:
            self._indexes[key] = len(self._indexes)
            return self._indexes[key]

    def _set_order(self, order: Iterable[Identity]):
        self._order = order
        length = len(self._order)
        self._counter["(not finished)"] = length - len(self._results)
        keys = [identity.key for identity in self._order]
        self._indexes = dict(zip(keys, range(length)))

    def _output(self, event):
        pass

    def _register(self, event):
        assert isinstance(event, Event)
        self._tick += 1
        if isinstance(event, StartEvent):
            self._set_order(event.order)
            self._started = event
            return

        elif isinstance(event, EndEvent):
            self._ended = event

            if self.collect_results_by:
                key = (
                    event.identity.check.id
                    if self.collect_results_by == "*check"
                    else dict(event.identity.iterargs).get(
                        self.collect_results_by, None
                    )
                )
                if key not in self._collected_results:
                    self._collected_results[key] = Counter()
                self._collected_results[key][event.message.name] += 1

        elif isinstance(event, EndCheckEvent):
            self._results.append(event)
            self._counter[event.summary_status.name] += 1
            self._counter["(not finished)"] -= 1

    @property
    def worst_check_status(self):
        """Returns a status or None if there was no check result"""
        return self._worst_check_status

    def receive(self, event):
        if self._started is None and not isinstance(event, StartEvent):
            raise ProtocolViolationError(
                f"Received Event before status START:"
                f" {event.status} {event.message}."
            )
        if self._ended:
            raise ProtocolViolationError(
                f"Received Event after status END:" f" {event.status} {event.message}."
            )

        if isinstance(event, EndCheckEvent) and (
            self._worst_check_status is None
            or self._worst_check_status < event.summary_status
        ):
            # Checks that are marked as "experimental" do not affect the
            # exit status code, so that they won't break a build on continuous
            # integration setups.
            if not event.identity.check.experimental:
                # we only record ENDCHECK, because check runner may in the future
                # have tools to upgrade/downgrade the actually worst status
                # this should be future proof.
                self._worst_check_status = event.summary_status

        self._register(event)
        self._output(event)
