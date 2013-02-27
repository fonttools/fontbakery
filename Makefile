VENV=venv

all: setup

ifdef DEV
	REQ=requiremets.dev.txt
else
	REQ=requiremets.txt
	@echo "Use `make DEV` for development environment"
endif

venv/bin/activate:
	virtualenv venv --distribute --relocatable

setup: venv/bin/activate requiremets.txt
	. venv/bin/activate; pip install -Ur requiremets.txt

run: venv/bin/activate requiremets.txt
	. venv/bin/activate; gunicorn -w 2 -b 0.0.0.0:5001 entry:app

babel: venv/bin/activate
	. venv/bin/activate; pybabel extract -F babel.cfg -o messages.pot .

# lazy babel scan
lazybabel: venv/bin/activate
	. venv/bin/activate; pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot .

# $LANG=ru
addlang: venv/bin/activate
	. venv/bin/activate; pybabel init -i messages.pot -d translations -l $LANG

upd: venv/bin/activate
	. venv/bin/activate; pybabel update -i messages.pot -d translations

celery: venv/bin/activate
	. venv/bin/activate; celery -A entry-celery worker

mail: setup
	python -m smtpd -n -c DebuggingServer localhost:20025
