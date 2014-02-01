# Fresh installation test
#
# To run this: sudo docker build .

FROM stackbrew/ubuntu:saucy
MAINTAINER Font Backery devs

RUN apt-get update
RUN apt-get install -y python-software-properties python-pip python-setuptools python-dev build-essential python

ADD ./ /code/

ENV DEBIAN_FRONTEND noninteractive
RUN cat /code/packages.txt | xargs apt-get -y --force-yes install

RUN ldconfig

# RUN grep -v distribute /code/requirements.txt | xargs pip install

RUN cd /code/ && make setup

RUN cd /code/src/ && python manage.py test