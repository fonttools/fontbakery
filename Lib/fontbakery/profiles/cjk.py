from fontbakery.checkrunner import Section, PASS, FAIL, WARN, INFO #, ERROR, SKIP
from fontbakery.callable import condition, check
from fontbakery.message import Message
from fontbakery.fonts_profile import profile_factory

profile = profile_factory(default_section=Section("CJK"))


CJK_PROFILE_CHECKS = \
[
  'com.google.fonts/check/cjk/example',
]

@condition
def some_condition():
  """ Some condition docstring."""
  # FIXME: Use this as a template to create new conditions.
  return True


@check(
  id='com.google.fonts/check/cjk/example',
)
def com_google_fonts_check_cjk_example(ttFont):
  """ Example check docstring. """
  failed = False
  if "some condition":
    failed = True
    foo = 123
    yield FAIL, Message("why-did-it-fail-keyword",
                        (f"Something is bad because of {foo}."
                         " Please considering fixing by doing so and so."))
  elif "a warning":
    failed = True
    yield WARN, (f"Beware of so and so!")

  elif "informative message":
    yield INFO, (f"This is an INFO msg...")

  if not failed:
    yield PASS, ("All looks great!")


profile.auto_register(globals())
profile.test_expected_checks(CJK_PROFILE_CHECKS, exclusive=True)
