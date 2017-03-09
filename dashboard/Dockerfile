FROM python:2.7

RUN pip install flask
RUN pip install rethinkdb

COPY app.py /
COPY templates/dashboard.html /templates/
COPY templates/under_deployment.html /templates/
COPY templates/family_details.html /templates/
COPY templates/testsuite.html /templates/

CMD ["python2", "-u", "app.py"]
