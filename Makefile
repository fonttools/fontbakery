VENV=venv

# target: all — Default target. Bootstraps environment
all: setup

# ifdef DEV
# 	REQ=requiremets.dev.txt
# elseс
# 	REQ=requirements.txt
# 	@echo "Use `make DEV` for development environment"
# endif

venv/bin/activate:
	virtualenv-2.7 --system-site-packages venv

bakery/static/bootstrap/css/bootstrap.css:
	cd bakery/static && curl -O  http://getbootstrap.com/2.3.2/assets/bootstrap.zip && unzip bootstrap.zip

bakery/static/jquery-2.0.0.min.js:
	cd bakery/static && curl -O http://code.jquery.com/jquery-2.0.0.min.js

bakery/static/font-awesome.zip:
	cd bakery/static && curl -O http://fortawesome.github.io/Font-Awesome/assets/font-awesome.zip && unzip font-awesome.zip

bakery/static/ace/master:
	cd bakery/static/ace && curl -O https://codeload.github.com/ajaxorg/ace-builds/zip/master && unzip master

bakery/static/socket.io.min.js:
	cd bakery/static && curl -O http://cdnjs.cloudflare.com/ajax/libs/socket.io/0.9.16/socket.io.min.js 

bakery/static/jquery.pjax.js:
	cd bakery/static && curl -O https://raw.github.com/defunkt/jquery-pjax/master/jquery.pjax.js

# target: setup — bootstrap environment
setup: venv/bin/activate requirements.txt bakery/static/jquery-2.0.0.min.js bakery/static/bootstrap/css/bootstrap.css bakery/static/ace/master bakery/static/font-awesome.zip bakery/static/socket.io.min.js bakery/static/jquery.pjax.js
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
mail: setup
	python -m smtpd -n -c DebuggingServer localhost:20025

# target: init — initial data setup
init: venv/bin/activate requirements.txt
	. venv/bin/activate; python init.py

# target: clean — remove working files and reinit initial data
clean:
	rm -rf data/*; . venv/bin/activate; python init.py

# target: help — this help
help:
	@egrep "^# target:" [Mm]akefile
