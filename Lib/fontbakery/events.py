# This class is a temporary part of refactoring. If you see it still here
# in the future, refactor it away again...
from collections import namedtuple
from dataclasses import dataclass
from typing import Optional

from fontbakery.section import Section
from fontbakery.status import Status, START, ENDCHECK, STARTCHECK, END, ERROR, PASS
from fontbakery.callable import FontBakeryCheck
from fontbakery.message import Message


@dataclass
class Identity:
    section: Optional[Section]
    check: Optional[FontBakeryCheck]
    iterargs: dict

    @property
    def key(self):
        return (
            str(self.section) if self.section else self.section,
            str(self.check) if self.check else self.check,
            self.iterargs,
        )


@dataclass
class Event:
    status: Status
    message: Message
    identity: Identity


class CheckResult:
    def __init__(self, identity):
        self.identity = identity
        self.results = []

    def append(self, result):
        self.results.append(result)

    def extend(self, results):
        self.results.extend(results)

    @property
    def summary_status(self):
        _summary_status = max(result.status for result in self.results)
        if _summary_status is None:
            _summary_status = ERROR
            self.append(
                Event(
                    ERROR,
                    (f"The check {self.identity.check} did not yield any status"),
                    self.identity,
                )
            )
        elif _summary_status < PASS:
            _summary_status = ERROR
            # got to yield it,so we can see it in the report
            self.append(
                Event(
                    ERROR,
                    (
                        f"The most significant status of {self.identity.check}"
                        f" was only {_summary_status} but"
                        f" the minimum is {PASS}"
                    ),
                    self.identity,
                )
            )
        return _summary_status

    def getData(self, runner):
        check = self.identity.check
        json = {
            "key": self.identity.key,
            "description": check.description,
            "documentation": check.documentation,
            "rationale": check.rationale,
            "experimental": check.experimental,
            "severity": check.severity,
            "result": self.summary_status.name,
            "logs": [],
        }
        # This is a big hack
        if json["key"][2] != ():
            json["filename"] = runner.get_iterarg(*json["key"][2][0])
        for result in self.results:
            if isinstance(result.message, Message):
                message = result.message.getData()
            else:
                message = {"message": result.message}
            json["logs"].append({"status": result.status.name, "message": message})
        return json
