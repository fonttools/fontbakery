# Before using Font Bakery in prodution copy
# this file to local.cfg and update all properties
# listed here.
# $ cp local.example.cfg local.cfg
# To overide other options check config.py and copy
# name and new value here to update it.

# In pruduction mode please always use DEBUG=False
DEBUG = True

# Owerite Github OAuth settings
GITHUB_CONSUMER_KEY = ''
GITHUB_CONSUMER_SECRET = ''

SQLALCHEMY_ECHO = True
# Generate new strong SECRET_KEY using this command:
# >>> import os; os.urandom(24)
SECRET_KEY = '\x18K/\x0be\x8b9\xac\xf9\xac\x11\x88\x858\xa4~8\x03\x05\xdf\x03Y\r|'

# Database connection string:
# More info http://pythonhosted.org/Flask-SQLAlchemy/config.html
# Recommended backend is PostgreSQL
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost/bakery'

# Web hooks url. Use real domain name visible from
# internet because Github will use it.
# {id} is important
HOOK_URL = 'http://bakery.fontforge.org/api/webhook/{id}'
