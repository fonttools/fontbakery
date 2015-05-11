import logging
import sys


class WhitespaceRemovingFormatter(logging.Formatter):
    def format(self, record):
        import re
        record.msg = re.sub('\n+', ' ', record.msg.strip())
        return super(WhitespaceRemovingFormatter, self).format(record)


logger = logging.getLogger('fontbakery')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler(stream=sys.stdout)
# ch.setLevel(logging.ERROR)

# create formatter
formatter = WhitespaceRemovingFormatter('%(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)
