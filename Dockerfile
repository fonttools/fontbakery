FROM python:2.7

ADD requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update
RUN apt-get install -y mono-complete

ADD fontbakery-check-ttf.py /
ADD data/test/mada/*.ttf /test/
COPY prebuilt /prebuilt

CMD ["python2", "fontbakery-check-ttf.py", "test/*.ttf", "--verbose", "--json"]


