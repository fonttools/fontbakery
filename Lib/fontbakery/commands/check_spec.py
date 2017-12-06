#!/usr/bin/env python
# -*- coding: utf-8 -*-

# usage:
# $ fontbakery check-specification fontbakery.specifications.googlefonts -h
from __future__ import absolute_import, print_function, unicode_literals

import sys
import logging
import argparse
import glob
from collections import OrderedDict

from fontbakery.testrunner import (
              distribute_generator
            , TestRunner
            , Spec
            , DEBUG
            , INFO
            , WARN
            , ERROR
            , SKIP
            , PASS
            , FAIL
            )

log_levels =  OrderedDict((s.name,s) for s in sorted((
              DEBUG
            , INFO
            , WARN
            , ERROR
            , SKIP
            , PASS
            , FAIL
            )))

DEFAULT_LOG_LEVEL = WARN

from fontbakery.reporters.terminal import TerminalReporter
from fontbakery.reporters.serialize import SerializeReporter


def runner_factory(specification, label, items, explicit_tests=None, custom_order=None
                                                        , values=None):
  """ Convenience TestRunner factory. """
  values_ = {label: items}
  if values is not None:
    values_.update(values)
  return TestRunner( specification, values_
                   , explicit_tests=explicit_tests
                   , custom_order=custom_order
                   )

def main(args, specification=None, items_label=None, values=None):
  if args.list_tests:
    for section_name, section in specification._sections.items():
      tests = section.list_tests()
      sys.exit("Available tests on {} are:\n{}".format(section_name,
                                                       "\n".join(tests)))

  items = getattr(args, items_label)
  runner = runner_factory(specification, items_label, items
                     , explicit_tests=args.checkid
                     , custom_order=args.order
                     , values=values
                     )

  # the most verbose loglevel wins
  loglevel = min(args.loglevels) if args.loglevels else DEFAULT_LOG_LEVEL
  tr = TerminalReporter(runner=runner, is_async=False
                       , print_progress=not args.no_progress
                       , test_threshold=loglevel
                       , log_threshold=args.loglevel_messages or loglevel
                       , usecolor=not args.no_colors
                       , collect_results_by=args.gather_by
                       )
  reporters = [tr.receive]
  if args.json:
    sr = SerializeReporter(runner=runner, collect_results_by=args.gather_by)
    reporters.append(sr.receive)
  distribute_generator(runner.run(), reporters)

  if args.json:
    import json
    json.dump(sr.getdoc(), args.json, sort_keys=True, indent=4)
