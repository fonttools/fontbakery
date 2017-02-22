FROM python:2.7

RUN pip install flask
RUN pip install rethinkdb

ADD app.py /

CMD ["python2", "-u", "app.py"]
