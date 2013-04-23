VENV=venv

all: setup

# ifdef DEV
# 	REQ=requiremets.dev.txt
# elseс
# 	REQ=requirements.txt
# 	@echo "Use `make DEV` for development environment"
# endif

venv/bin/activate:
	virtualenv --distribute venv

bakery/static/bootstrap/css/bootstrap.css:
	cd bakery/static && curl -O http://twitter.github.io/bootstrap/assets/bootstrap.zip && unzip bootstrap.zip

bakery/static/jquery-2.0.0.min.js:
	cd bakery/static && curl -O http://code.jquery.com/jquery-2.0.0.min.js

setup: venv/bin/activate requirements.txt bakery/static/jquery-2.0.0.min.js bakery/static/bootstrap/css/bootstrap.css
	. venv/bin/activate; pip install -Ur requirements.txt

run: venv/bin/activate requirements.txt
	. venv/bin/activate; gunicorn -w 2 -b 0.0.0.0:5001 entry:app

babel: venv/bin/activate
	. venv/bin/activate; pybabel extract -F babel.cfg -o messages.pot .

# lazy babel scan
lazybabel: venv/bin/activate
	. venv/bin/activate; pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot .

# $LANG=ru
addlang: venv/bin/activate
	. venv/bin/activate; pybabel init -i messages.pot -d translations -l $LANG

updlang: venv/bin/activate
	. venv/bin/activate; pybabel update -i messages.pot -d translations

celery: venv/bin/activate
	. venv/bin/activate; celery -A entry-celery worker --loglevel=info

freeze: venv/bin/activate
	. venv/bin/activate; pip freeze -r requirements.dev.txt > requirements.txt

mail: setup
	python -m smtpd -n -c DebuggingServer localhost:20025

init: venv/bin/activate requirements.txt
	. venv/bin/activate; python init.py
