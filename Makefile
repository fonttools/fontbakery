VENV=venv

all: setup

# ifdef DEV
# 	REQ=requiremets.dev.txt
# else
# 	REQ=requirements.txt
# 	@echo "Use `make DEV` for development environment"
# endif

venv/bin/activate:
	virtualenv --distribute venv

setup: venv/bin/activate requirements.txt
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
	. venv/bin/activate; celery -A entry-celery worker

freeze: venv/bin/activate
	. venv/bin/activate; pip freeze -r requirements.dev.txt > requirements.txt

mail: setup
	python -m smtpd -n -c DebuggingServer localhost:20025
