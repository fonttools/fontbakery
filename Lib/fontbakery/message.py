class Message:
  """Status messages to be yielded by FontBakeryCheck"""
  def __init__(self, code, message):
    """
      code: (string|number) a check internal, unique code to describe a
            specific failure condition. A short string is preferred, it
            makes a better experience to read the code.
            Never use the same code at two different yields, this is meant
            for unit testing to identify a specific condition of the check.
            A yield within a loop would (usually) have the same code for
            each iteration, unless there's a good reason not to do so.

      message: (string) human readable message.

      In the future, this class could be extended to hold even more
      information if useful, e.g. a hint how to fix a specific condition.
    """
    self.code = code
    self.message = message

  def __repr__(self):
    return f'{self.message} [code: {self.code}]'

  def getData(self):
    """ return a dictionary with data suitable for serialization,
        i.e. only stuff that is allowed in JSON.
    """
    return {
        'code': self.code
      , 'message': self.message
    }
