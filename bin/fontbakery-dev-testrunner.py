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

conditions={}
def registerCondition(condition):
  conditions[condition.name] = condition
  return condition

tests=[]
def registerTest(test):
  tests.append(test)
  return test

@registerCondition
@condition
def fontNameNumber(font):
  return int(font.split('_')[1])
registerCondition(fontNameNumber)

@registerCondition
@condition
def isOddFontName(fontNameNumber):
  #raise Exception('Just to see how much we can extract from this')
  return  fontNameNumber % 2 == 1
registerCondition(isOddFontName)

@registerTest
@test(
    id='com.google.fonts/1'
  , conditions=['isOddFontName']
  , description='Is the odd fontname bigger than one?'
)
def oddNameBiggerThanOne(fontNameNumber):
  return PASS if fontNameNumber > 1 else FAIL, fontNameNumber

@registerTest
@test(
    id='com.google.fonts/2'
  , conditions=['not isOddFontName']
  , description='Is the even fontname bigger than two?'
)
def evenNameBiggerThanTwo(fontNameNumber):
  return PASS if fontNameNumber > 2 else FAIL, fontNameNumber

@registerTest
@test(
    id='com.google.fonts/3'
  , description='Fontname starts with "font_".'
)
def fontNameStartsWithFont_(font):
  test = 'font_2'
  for i in range(len(test)):
    if len(font) >= i and font[i] == test[i]:
      yield PASS, 'Char at index {} is "{}".'.format(i, test[i])
    else:
      yield FAIL, 'Char at index {} is not "{}" in "{}".'.format(i, test[i], font)
      1/0

testsections=[Section('Default', tests), Section('Special', tests)] # order=['*test']

googleSpec = Spec(
    conditions=conditions
  , testsections=testsections
  , iterargs={'font': 'fonts'}
)
fonts = ['font_1', 'font_2', 'font_3', 'font_4']


if __name__ == '__main__':
  runner = TestRunner(googleSpec, {'fonts': fonts})
  tr = TerminalReporter(runner=runner, is_async=False, print_progress=True
                                              , collect_results_by='font')
  # sr = SerializeReporter(runner=runner, collect_results_by='font')
  distribute_generator(runner.run(), [tr.receive])# sr.receive
