from fontbakery.errors import SetupError


class Section:
    """ An ordered set of checks.

    Used to structure checks in a profile. A profile consists
    of one or more sections.
    """
    def __init__(self, name, checks=None, order=None, description=None):
        self.name = name
        self.description = description
        self._add_check_callback = None
        self._remove_check_callback = None
        self._checks = [] if checks is None else list(checks)
        self._checkid2index = {check.id:i for i, check in enumerate(self._checks)}
        # a list of iterarg-names
        self._order = order or []

    def clone(self, filter_func=None):
        checks = self.checks if not filter_func else filter(filter_func, self.checks)
        return Section(self.name,
                       checks=checks,
                       order=self.order,
                       description=self.description)

    def __repr__(self):
        return f'<Section: {self.name}>'

    # This was problematic. See: https://github.com/googlefonts/fontbakery/issues/2194
    # def __str__(self):
    #     return self.name

    def __eq__(self, other):
        """ True if other.checks has the same checks in the same order"""
        if hasattr(other, "checks"):
            return self._checks == other.checks
        else:
            return False

    @property
    def order(self):
        return self._order[:]

    @property
    def checks(self):
        return self._checks

    def on_add_check(self, callback):
        if self._add_check_callback is not None:
            # allow only one, otherwise, skipping registration in
            # add_check becomes problematic, can't skip just for some
            # callbacks.
            raise Exception(f'{self} already has an on_add_check callback')
        self._add_check_callback = callback

    def on_remove_check(self, callback):
        if self._remove_check_callback is not None:
            # allow only one, otherwise, skipping un-registration in
            # remove_check becomes problematic, can't skip just for some
            # callbacks.
            raise Exception(f'{self} already has an on_add_check callback')
        self._remove_check_callback = callback

    def add_check(self, check):
        """
        Please use rather `register_check` as a decorator.
        """
        if self._add_check_callback is not None:
            if not self._add_check_callback(self, check):
                # rejected, skip!
                return False

        self._checkid2index[check.id] = len(self._checks)
        self._checks.append(check)
        return True

    def remove_check(self, check_id):
        index = self._checkid2index[check_id]
        if self._remove_check_callback is not None:
            if not self._remove_check_callback(self, check_id):
                # rejected, skip!
                return False
        del self._checks[index]
        # Fixing the index, maybe an ordered dict would work here the same
        # but simpler. Could also rebuild the entire index.
        del self._checkid2index[check_id]
        for cid, idx in self._checkid2index.items():
            if idx > index:
                self._checkid2index[cid] = idx - 1
        return True

    def replace_check(self, override_check_id, new_check):
        index = self._checkid2index[override_check_id]
        if self._remove_check_callback is not None:
            if not self._remove_check_callback(self, override_check_id):
                # rejected, skip!
                return False

        if self._add_check_callback is not None:
            if not self._add_check_callback(self, new_check):
                # rejected, skip!
                # But first restore the old check registration.
                # Maybe a resource manager would be nice here.
                # Also, raising and failing could be an option.
                self._add_check_callback(self, self.get_check(override_check_id))
                return False

        del self._checkid2index[override_check_id]
        self._checkid2index[new_check.id] = index
        self._checks[index] = new_check
        return True

    def merge_section(self, section, filter_func=None):
        """
        Add section.checks to self, if not skipped by self._add_check_callback.
        order, description, etc. are not updated.
        """
        for check in section.checks:
            if filter_func and not filter_func(check):
                continue
            self.add_check(check)

    def get_check(self, check_id):
        index = self._checkid2index[check_id]
        return self._checks[index]

    def register_check(self, func):
        """
        # register in `special_section`
        @my_section.register_check
        @check(id='com.example.fontbakery/check/0')
        def my_check():
          yield PASS, 'example'
        """
        if not self.add_check(func):
            raise SetupError(f'Can\'t add check {func} to section {self}.')
        return func
