from typing import Optional

from fontbakery.configuration import Configuration
from fontbakery.status import Status


class Profile:
    """
    Profiles may specify default configuration values (used to parameterize
    checks), which are then overridden by values in the user's configuration
    file.
    """

    configuration_defaults = {}

    def __init__(
        self,
        sections=None,
        iterargs=None,
        overrides=None,
    ):
        """
          sections: a list of sections, which are ideally ordered sets of
              individual checks.
              It makes no sense to have checks repeatedly, they yield the same
              results anyway, thus we don't allow this.
          iterargs: maping 'singular' variable names to the iterable in values
              e.g.: `{'font': 'fonts'}` in this case fonts must be iterable AND
              'font' may not be a value NOR a condition name.

        We will:
          a) get all needed values/variable names from here
          b) add some validation, so that we know the values match
             our expectations! These values must be treated as user input!
        """
        self.iterargs = iterargs
        self.sections = sections
        self.overrides = overrides or {}

    def should_override(self, check_id, code) -> Optional[Status]:
        if check_id in self.overrides:
            for override in self.overrides[check_id]:
                if code == override["code"]:
                    return Status(override["status"])
        return None

    def merge_default_config(self, user_config):
        """
        Forms a configuration object based on defaults provided by the profile,
        overridden by values in the user's configuration file.
        """
        copy = Configuration(**self.configuration_defaults)
        copy.update(user_config)
        return copy
