class Section:
    """An ordered set of checks.

    Used to structure checks in a profile. A profile consists
    of one or more sections.
    """

    def __init__(self, name, checks=None, description=None):
        self.name = name
        self.description = description
        self.checks = [] if checks is None else list(checks)
        self._checkid2index = {check.id: i for i, check in enumerate(self.checks)}

    def __repr__(self):
        return f"<Section: {self.name}>"

    def add_check(self, check):
        self._checkid2index[check.id] = len(self.checks)
        self.checks.append(check)
        return True

    def has_check(self, check_id):
        return check_id in self._checkid2index
