"""
Separation of Concerns Disclaimer:
While created specifically for checking fonts and font-families this
module has no domain knowledge about fonts. It can be used for any kind
of (document) checking. Please keep it so. It will be valuable for other
domains as well.
Domain specific knowledge should be encoded only in the Profile (Checks,
Conditions) and MAYBE in *customized* reporters e.g. subclasses.
"""
from collections import Counter, defaultdict
from typing import Iterable, Optional
from dataclasses import dataclass

from fontbakery.checkrunner import CheckRunner
from fontbakery.status import Status
from fontbakery.errors import ProtocolViolationError
from fontbakery.result import CheckResult, Identity


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
        self._results = []  # Check results in order of appearance
        self._indexes = {}
        self._tick = 0
        self._counter = Counter()
        self._worst_check_status = None
        self._minimum_weight = min(status.weight for status in self.loglevels)
        self._collected_results = {}
        self._sectioncounter = defaultdict(Counter)

    def omit_loglevel(self, msg) -> bool:
        """Determine if message is below log level."""
        return Status(msg).weight < self._minimum_weight

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

    @property
    def worst_check_status(self):
        """Returns a status or None if there was no check result"""
        return self._worst_check_status

    def start(self, order):
        self._order = order
        length = len(self._order)
        self._counter["(not finished)"] = length - len(self._results)
        keys = [identity.key for identity in self._order]
        self._indexes = dict(zip(keys, range(length)))
        self._started = True

    def end(self):
        self._ended = True
        # if self.collect_results_by:
        #     key = (
        #         event.identity.check.id
        #         if self.collect_results_by == "*check"
        #         else dict(event.identity.iterargs).get(
        #             self.collect_results_by, None
        #         )
        #     )
        #     if key not in self._collected_results:
        #         self._collected_results[key] = Counter()
        #     self._collected_results[key][event.message.name] += 1

    def receive_result(self, checkresult: CheckResult):
        self._tick += 1
        if self._started is None:
            raise ProtocolViolationError("Received result before status START.")
        if self._ended:
            raise ProtocolViolationError("Received result after status END.")

        if (
            (
                self._worst_check_status is None
                or self._worst_check_status < checkresult.summary_status
            )
            # Checks that are marked as "experimental" do not affect the
            # exit status code, so that they won't break a build on continuous
            # integration setups.
            and not checkresult.identity.check.experimental
        ):
            self._worst_check_status = checkresult.summary_status

        self._results.append(checkresult)
        self._counter[checkresult.summary_status.name] += 1
        self._counter["(not finished)"] -= 1
        self._sectioncounter[checkresult.identity.section.name][
            checkresult.summary_status.name
        ] += 1
