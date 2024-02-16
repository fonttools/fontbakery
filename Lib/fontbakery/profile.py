from typing import Iterable, Optional
from dataclasses import dataclass, field


@dataclass
class Section:
    name: str
    checks: list = field(default_factory=list)
    description: Optional[str] = None

    def __repr__(self):
        return f"<Section: {self.name}>"

    def has_check(self, check_id):
        return any(check.id == check_id for check in self.checks)


@dataclass
class Profile:
    name: str
    configuration_defaults: dict = field(default_factory=dict)
    sections: Iterable[Section] = field(default_factory=list)
    iterargs: dict = field(default_factory=dict)
    overrides: dict = field(default_factory=dict)
