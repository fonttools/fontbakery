FROM python:2.7

RUN apt-get update
RUN pip install pika

ADD dispatch-jobs.py /
ADD fontprojects.py /

CMD ["python2", "dispatch-jobs.py"]
