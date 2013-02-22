run:
	gunicorn -w 2 -b 0.0.0.0:4000 bakery:app

babel:
	pybabel extract -F babel.cfg -o messages.pot .

# lazy babel scan
lazybabel:
	pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot .

# $LANG=ru
addlang:
	pybabel init -i messages.pot -d translations -l $LANG

upd:
	pybabel update -i messages.pot -d translations

celery:
	venv/bin/celery -A bakery worker

mail:
	python -m smtpd -n -c DebuggingServer localhost:20025
