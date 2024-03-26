from dataclasses import dataclass
from typing import Optional

from fontbakery.profile import Section
from fontbakery.status import Status, PASS
from fontbakery.callable import FontBakeryCheck
from fontbakery.message import Message


@dataclass
class Identity:
    """An identity is an individual execution of a check: a combination of
    a check's section, the check itself, and the arguments which are used to
    call it. A check may be called multiple different times with different
    arguments; an identity uniquely identifies one of those calls."""

    section: Optional[Section]
    check: Optional[FontBakeryCheck]
    iterargs: tuple

    @property
    def key(self) -> tuple:
        """A tuple serializing the identity so that it can be used in
        dictionaries, sets, JSON files, etc."""
        return (
            str(self.section) if self.section else self.section,
            str(self.check) if self.check else self.check,
            self.iterargs,
        )


@dataclass
class Subresult:
    """Checks yield one or more subresults, each of which has a status and a
    message. We wrap the status and message into a Subresult object for
    type safety and tidiness."""

    status: Status
    message: Message


class CheckResult:
    """The result of a particular check invocation (its identity), made up
    of the identity plus a list of subresults yielded by the check."""

    def __init__(self, identity):
        self.identity = identity
        self.results = []

    def append(self, result):
        self.results.append(result)

    def extend(self, results):
        self.results.extend(results)

    @property
    def summary_status(self):
        """The highest status in the list of subresults."""
        if not self.results:
            # assume that if no result was yielded, then everything is fine:
            self.results = [Subresult(PASS, Message("ok", "All looks good!"))]
        _summary_status = max(result.status for result in self.results)
        return _summary_status

    def getData(self, runner):
        """Return the result as a dictionary with data suitable for serialization."""
        check = self.identity.check
        module = check.__module__.replace("fontbakery.checks.", "")
        if not isinstance(check.proposal, list):
            proposal = [check.proposal]
        else:
            proposal = check.proposal
        json = {
            "key": self.identity.key,
            "description": check.description,
            "documentation": check.documentation,
            "rationale": check.rationale,
            "experimental": check.experimental,
            "proposal": proposal,
            "severity": check.severity,
            "result": self.summary_status.name,
            "module": module,
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
