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
	git clone https://github.com/khaledhosny/ots.git
	cd ots ; python gyp_ots ; make

# target: run — run project
run: venv/bin/activate requirements.txt
	. venv/bin/activate; python entry.py

# target: prun — production run project
prun: venv/bin/activate requirements.txt
	. venv/bin/activate; gunicorn --log-file bakery-error.log -p bakery.pid -D -w 4 --worker-class socketio.sgunicorn.GeventSocketIOWorker -b 0.0.0.0:5000 wsgi:app

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

shell: venv/bin/activate
	. venv/bin/activate; python

crawl: venv/bin/activate
	. venv/bin/activate && \
	cd scripts/scrapes/familynames && \
	rm -rf ../json/*.json && \
	scrapy crawl terminaldesign -o ../json/terminaldesign.json -t json --nolog && \
	scrapy crawl typography -o ../json/typography.json -t json --nolog && \
	scrapy crawl europatype -o ../json/europatype.json -t json --nolog && \
	scrapy crawl boldmonday -o ../json/boldmonday.json -t json --nolog && \
	scrapy crawl commercialtype -o ../json/commercialtype.json -t json --nolog && \
	scrapy crawl swisstypefaces -o ../json/swisstypefaces.json -t json --nolog && \
	scrapy crawl grillitype -o ../json/grillitype.json -t json --nolog && \
	scrapy crawl letterror -o ../json/letterror.json -t json --nolog && \
	scrapy crawl teff -o ../json/teff.json -t json --nolog && \
	scrapy crawl nouvellenoire -o ../json/nouvellenoire.json -t json --nolog && \
	scrapy crawl typedifferent -o ../json/typedifferent.json -t json --nolog && \
	scrapy crawl optimo -o ../json/optimo.json -t json --nolog

# target: help — this help
help:
	@egrep "^# target:" [Mm]akefile
