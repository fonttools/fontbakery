FROM python:2.7

RUN pip install flask
RUN pip install rethinkdb

COPY app.py /
COPY templates/dashboard.html /templates/
COPY static/css/dashboard.css /static/css/

CMD ["python2", "-u", "app.py"]
