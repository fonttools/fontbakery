#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from fontbakery.testrunner import (
              DEBUG
            , INFO
            , WARN
            , ERROR
            , SKIP
            , PASS
            , FAIL
            , distribute_generator
            , Section
            , TestRunner
            , Spec
            )
from fontbakery.reporters.terminal import TerminalReporter
from fontbakery.reporters.serialize import SerializeReporter
from fontbakery.callable import condition, test

default_section = Section('Default')
specification = Spec(
    default_section=default_section
  , iterargs={'font': 'fonts'}
)
register_condition = specification.register_condition
register_test = specification.register_test



@register_condition
@condition
def fontNameNumber(font):
  return int(font.split('_')[1])

@register_condition
@condition
def isOddFontName(fontNameNumber):
  #raise Exception('Just to see how much we can extract from this')
  return  fontNameNumber % 2 == 1

@register_test
@test(
    id='com.google.fonts/1'
  , conditions=['isOddFontName']
)
def oddNameBiggerThanOne(fontNameNumber):
  """Is the odd fontname bigger than one?"""
  return PASS if fontNameNumber > 1 else FAIL, fontNameNumber

@register_test
@test(
    id='com.google.fonts/2'
  , conditions=['not isOddFontName']
)
def evenNameBiggerThanTwo(fontNameNumber):
  """Is the even fontname bigger than two?"""
  return PASS if fontNameNumber > 2 else FAIL, fontNameNumber

@register_test
@test(
    id='com.google.fonts/3'
)
def fontNameStartsWithFont_(font):
  """Fontname starts with "font_"."""
  test = 'font_2'
  for i in range(len(test)):
    if len(font) >= i and font[i] == test[i]:
      yield PASS, 'Char at index {} is "{}".'.format(i, test[i])
    else:
      yield FAIL, 'Char at index {} is not "{}" in "{}".'.format(i, test[i], font)
      1/0

if __name__ == '__main__':
  fonts = ['font_1', 'font_2', 'font_3', 'font_4']
  runner = TestRunner(specification, {'fonts': fonts})
  tr = TerminalReporter(runner=runner, is_async=False, print_progress=True
                                              , collect_results_by='font')
  # sr = SerializeReporter(runner=runner, collect_results_by='font')
  distribute_generator(runner.run(), [tr.receive])# sr.receive
