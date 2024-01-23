# This class is a temporary part of refactoring. If you see it still here
# in the future, refactor it away again...
from collections import namedtuple
from dataclasses import dataclass
from typing import Optional

from fontbakery.section import Section
from fontbakery.status import Status, START, ENDCHECK, STARTCHECK, END
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


class StartEvent(Event):
    def __init__(self, order):
        self.order = order
        self.status = START

    @property
    def message(self):
        return self.order

    @property
    def identity(self):
        return Identity(None, None, None)


class EndEvent(Event):
    def __init__(self, summary):
        self.summary = summary
        self.status = END

    @property
    def message(self):
        return self.summary

    @property
    def identity(self):
        return Identity(None, None, None)


@dataclass
class StartCheckEvent(Event):
    def __init__(self, identity):
        self.status = STARTCHECK
        self.identity = identity
        self.message = None


@dataclass
class EndCheckEvent(Event):
    def __init__(self, summary_status, identity):
        self.status = ENDCHECK
        self.summary_status = summary_status
        self.identity = identity

    @property
    def message(self):
        return self.summary_status
