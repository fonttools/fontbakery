VENV=venv

# target: all — Default target. Bootstraps environment
all: setup

# ifdef DEV
# 	REQ=requiremets.dev.txt
# elseс
# 	REQ=requirements.txt
# 	@echo "Use `make DEV` for development environment"
# endif

.PHONY: setup run prun worker init clean help

venv/bin/activate:
	virtualenv-2.7 --system-site-packages venv

static/bootstrap/css/bootstrap.css:
	cd static && curl -O  http://getbootstrap.com/2.3.2/assets/bootstrap.zip && unzip bootstrap.zip

static/jquery-2.0.3.min.js:
	cd static && curl -O http://code.jquery.com/jquery-2.0.3.min.js

static/font-awesome.zip:
	cd static && curl -O http://fortawesome.github.io/Font-Awesome/assets/font-awesome.zip && unzip font-awesome.zip

static/ace/master:
	cd static/ace && curl -O https://codeload.github.com/ajaxorg/ace-builds/zip/master && unzip master

static/socket.io.min.js:
	cd static && curl -O http://cdnjs.cloudflare.com/ajax/libs/socket.io/0.9.16/socket.io.min.js 

static/jquery.pjax.js:
	cd static && curl -O https://raw.github.com/defunkt/jquery-pjax/master/jquery.pjax.js

static/jquery.tablesorter:
	cd static && curl -O http://tablesorter.com/__jquery.tablesorter.zip && unzip __jquery.tablesorter.zip -d tablesorter

static/jquery.number.min.js:
	cd static && curl -O https://raw.github.com/teamdf/jquery-number/master/jquery.number.min.js

# target: setup — bootstrap environment
setup: venv/bin/activate requirements.txt static/jquery-2.0.3.min.js static/bootstrap/css/bootstrap.css static/ace/master static/font-awesome.zip static/socket.io.min.js static/jquery.pjax.js static/jquery.tablesorter static/jquery.number.min.js
	. venv/bin/activate; pip install -Ur requirements.txt

# target: run — run project
run: venv/bin/activate requirements.txt
	. venv/bin/activate; python entry.py

# target: prun — production run project
prun: venv/bin/activate requirements.txt
	. venv/bin/activate; gunicorn --config gunicorn_config.py entry:app

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

# target: worker — background tasks worker
worker: venv/bin/activate
	. venv/bin/activate; rqworker

# target: mail — run mailserver
mail: 
	python -m smtpd -n -c DebuggingServer localhost:20025

# target: init — initial data setup
init: venv/bin/activate requirements.txt
	. venv/bin/activate; python init.py

# target: offline — add offline user
offline: venv/bin/activate
	. venv/bin/activate; python scripts/offline.py

# target: stats — update stats in database
stats: venv/bin/activate
	. venv/bin/activate; python scripts/statupdate.py

# target: clean — remove working files and reinit initial data
clean:
	rm -rf data/*; . venv/bin/activate; python init.py

# target: help — this help
help:
	@egrep "^# target:" [Mm]akefile
