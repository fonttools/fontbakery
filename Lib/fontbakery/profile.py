from typing import Iterable
from dataclasses import dataclass, field

from fontbakery.section import Section


@dataclass
class Profile:
    configuration_defaults: dict = field(default_factory=dict)
    sections: Iterable[Section] = field(default_factory=list)
    iterargs: dict = field(default_factory=dict)
    overrides: dict = field(default_factory=dict)
