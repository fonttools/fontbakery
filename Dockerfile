FROM python:2.7

ADD requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt

ADD fontbakery-check-ttf.py /
ADD prebuilt/ot-sanitise /opt/bin/
ADD data/test/mada/*.ttf /test/

env PATH /opt/bin/:$PATH
CMD ["python2", "fontbakery-check-ttf.py", "test/*.ttf", "--verbose", "--json"]


