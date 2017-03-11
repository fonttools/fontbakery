FROM python:2.7

RUN pip install flask
RUN pip install rethinkdb

COPY app.py /
COPY templates/dashboard.html /templates/
COPY templates/under_deployment.html /templates/
COPY templates/family_details.html /templates/
COPY templates/testsuite.html /templates/
COPY static/css/dashboard.css /static/css/
COPY static/css/family_details.css /static/css/
COPY static/css/testsuite.css /static/css/
COPY static/js/family_details.js /static/js/
COPY static/js/stupidtable/stupidtable.min.js /static/js/

CMD ["python2", "-u", "app.py"]
