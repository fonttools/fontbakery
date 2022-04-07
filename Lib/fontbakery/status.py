class Status:
    """If you create a custom Status symbol, please keep in mind that
    all statuses are registered globally and that can cause name collisions.

    However, it's an intended use case for your checks to be able to yield
    custom statuses. Interpreters of the check protocol will have to skip
    statuses unknown to them or treat them in an otherwise non-fatal fashion.
    """

    def __new__(cls, name, weight=0):
        """Don't create two instances with same name.

        >>> a = Status('PASS')
        >>> a
        <Status hello>
        >>> b = Status('PASS')
        >>> b
        <Status hello>
        >>> b is a
        True
        >>> b == a
        True
        """
        instance = cls.__instances.get(name, None)
        if instance is None:
            instance = cls.__instances[name] = super(Status, cls).__new__(cls)
            setattr(instance, "_Status__name", name)
            setattr(instance, "_Status__weight", weight)
        return instance

    __instances = {}

    def __str__(self):
        return f"<Status {self.__name}>"

    @property
    def name(self):
        return self.__name

    @property
    def weight(self):
        return self.__weight

    def __gt__(self, other):
        return self.weight > other.weight

    def __ge__(self, other):
        return self.weight >= other.weight

    def __lt__(self, other):
        return self.weight < other.weight

    def __le__(self, other):
        return self.weight <= other.weight

    __repr__ = __str__


# Status messages of the check runner protocol

# Structuring statuses
#  * begin with "START" and "END"
#  * have weights < 0
#  * START statuses have even weight, corresponding END statuses have odd
#    weights, such that START.weight + 1 == END.weight
#  * the bigger the weight the bigger is the structure, structuring on a macro-level
#  * different structures can have the same weights, if they occur on the same level
#  * ENDCHECK is the biggest structuring status
#
# Log statuses
#  * have weights >= 0
#  * the more important the status the bigger the weight
#  * ERROR has the biggest weight
#  * PASS is the lowest status a check can have,
#    i.e.: a check run must at least yield one log that is >= PASS
#
# From all the statuses that can occur within a check, the "worst" one
# is defining for the check overall status:
# ERROR > FAIL > WARN > INFO > SKIP > PASS > DEBUG
# Anything from WARN to PASS does not make a check fail.
# A result < PASS creates an ERROR. That means, DEBUG is not a valid
# result of a check, nor is any of the structuring statuses.
# A check with SKIP can't (MUST NOT) create any other event.

# Log statuses
# only between STARTCHECK and ENDCHECK:
DEBUG = Status("DEBUG", 0)  # Silent by default
PASS = Status("PASS", 1)
SKIP = Status(
    "SKIP", 2
)  # SKIP is heavier than PASS because it's likely more interesting to
# see what got skipped, to reveal blind spots.
INFO = Status("INFO", 3)
WARN = Status(
    "WARN", 4
)  # A check that results in WARN may indicate a problem, but also may be OK.
FAIL = Status("FAIL", 5)  # A FAIL is a problem detected in the font or family.
ERROR = Status(
    "ERROR", 6
)  # Something a programmer must fix. It will make a check fail as well.

# Start of the suite of checks. Must be always the first message, even in async mode.
# Message is the full execution order of the whole profile
START = Status("START", -6)
# Only between START and before the first SECTIONSUMMARY and END
# Message is None.
STARTCHECK = Status("STARTCHECK", -2)
# Ends the last check started by STARTCHECK.
# Message the the result status of the whole check, one of PASS, SKIP, FAIL, ERROR.
ENDCHECK = Status("ENDCHECK", -1)
# After the last ENDCHECK one SECTIONSUMMARY for each section before END.
# Message is a tuple of:
#   * the actual execution order of the section in the check runner session
#     as reported. Especially in async mode, the order can differ significantly
#     from the actual order of checks in the session.
#   * a Counter dictionary where the keys are Status.name of
#     the ENDCHECK message. If serialized, some existing statuses may not be
#     in the counter because they never occurred in the section.
SECTIONSUMMARY = Status("SECTIONSUMMARY", -3)
# End of the suite of checks. Must be always the last message, even in async mode.
# Message is a counter as described in SECTIONSUMMARY, but with the collected
# results of all checks in all sections.
END = Status("END", -5)
