# -*- coding: utf-8 -*-
from __future__ import (absolute_import,
                        print_function,
                        unicode_literals,
                        division)

from fontbakery.testrunner import (
              INFO
            , WARN
            , ERROR
            , SKIP
            , PASS
            , FAIL
            , Section
            , Spec
            )
import os
from fontbakery.callable import condition, test
from fontbakery.message import Message
from fontbakery.constants import(
        # TODO: priority levels are not yet part of the new runner/reporters.
        # How did we ever use this information?
        # Check priority levels:
        CRITICAL
      , IMPORTANT
#     , NORMAL
#     , LOW
#     , TRIVIAL
)

default_section = Section('Default')
specification = Spec(
    default_section=default_section
  , iterargs={'font_dir': 'font_dirs'}
  #, sections=[]
)

register_test = specification.register_test
register_condition = specification.register_condition


def has_dir(upstream_path, dir_name):
  path = os.path.join(upstream_path, dir_name)

  if os.path.isdir(path):
    yield PASS, ('Repo has "{}" dir'.format(dir_name))
  else:
    yield FAIL, ('Repo needs "{}" dir or must be similiar dir must be '
                 'renamed'.format(dir_name))


@register_test
@test(
    id='com.upstream.repo/test/001'
  , priority=CRITICAL
)
def com_upstream_repo_test_001(font_dir):
  """Check repo has font dir
  """
  return has_dir(font_dir, 'fonts')


@register_test
@test(
    id='com.upstream.repo/test/002'
  , priority=CRITICAL
)
def com_upstream_repo_test_002(font_dir):
  """Check repo has sources dir
  """
  return has_dir(font_dir, 'sources')

