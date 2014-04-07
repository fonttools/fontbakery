VENV=venv

# target: all — Default target. Bootstraps environment
all: setup

# ifdef DEV
# 	REQ=requiremets.dev.txt
# else
# 	REQ=requirements.txt
# 	@echo "Use `make DEV` for development environment"
# endif

ifdef VENVRUN
else
VENVRUN=virtualenv-2.7
endif


.PHONY: setup run prun worker init clean help

venv/bin/activate:
	$(VENVRUN) --system-site-packages venv

static/bower.json:
	cd static && bower install

# target: setup — bootstrap environment
setup: venv/bin/activate requirements.txt static/bower.json
	. venv/bin/activate; pip install -Ur requirements.txt

# target: run — run project
run: venv/bin/activate requirements.txt
	. venv/bin/activate; python entry.py

# target: prun — production run project
prun: venv/bin/activate requirements.txt
	. venv/bin/activate; gunicorn -c gunicorn_config.py --worker-class socketio.sgunicorn.GeventSocketIOWorker wsgi:app

babel: venv/bin/activate
	. venv/bin/activate; pybabel extract -F babel.cfg -o bakery/translations/messages.pot bakery

# lazy babel scan
lazybabel: venv/bin/activate
	. venv/bin/activate; pybabel extract -F babel.cfg -k lazy_gettext -o bakery/translations/messages.pot bakery

# $LANG=ru
addlang: venv/bin/activate
	. venv/bin/activate; pybabel init -i bakery/translations/messages.pot -d bakery/translations -l $(LANG)

updlang: venv/bin/activate
	. venv/bin/activate; pybabel update -i bakery/translations/messages.pot -d bakery/translations

# target: worker — background tasks worker
worker: venv/bin/activate
	. venv/bin/activate; rqworker

# target: mail — run mailserver
mail:
	python -m smtpd -n -c DebuggingServer localhost:20025

# target: init — initial data setup
init: venv/bin/activate requirements.txt
	. venv/bin/activate; python init.py
	make stats

# target: offline — add offline user
offline: venv/bin/activate
	. venv/bin/activate; python scripts/offline.py

# target: stats — update stats in database
stats: venv/bin/activate
	. venv/bin/activate; python scripts/statupdate.py

# target: clean — remove working files and reinit initial data
clean:
	rm -rf data/*; . venv/bin/activate; python init.py

crawl: venv/bin/activate
	. venv/bin/activate && \
	cd scripts/scrapes/familynames && \
	scrapy crawl terminaldesign -o ../json/terminaldesign.json -t json --nolog && \
	scrapy crawl typography -o ../json/typography.json -t json --nolog && \
	scrapy crawl europatype -o ../json/europatype.json -t json --nolog && \
	scrapy crawl boldmonday -o ../json/boldmonday.json -t json --nolog

# target: help — this help
help:
	@egrep "^# target:" [Mm]akefile
