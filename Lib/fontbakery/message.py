# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals, division

class Message(object):
  def __init__(self, code, message):
    """
      Status messages to be yielded by FontBakeryTest

      code: (string|number) a test internal, unique code to describe a
            specific failure condition. A short string is preferred, it
            makes a better experience to read the code.
            Never use the same code at two different yields, this is meant
            for unit testing to identify a specific condition of the test.
            A yield within a loop would (usually) have the same code for
            each iteration, unless there's a good reason not to do so.

      message: (string) human readable message.

      In the future, this class could be extended to hold even more
      information if useful, e.g. a hint how to fix a specific condition.
    """
    self.code = code
    self.message = message

  def __repr__(self):
    return '{1} [code: {0}]'.format(self.code, self.message)
