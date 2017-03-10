FROM python:2.7

RUN apt-get update
RUN apt-get install -y mono-complete
RUN apt-get install -y git-core

ADD requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt

COPY prebuilt /prebuilt
ADD fontbakery-check-ttf.py /
ADD dashboard/containers/worker/fontbakery-gather-dashboard-data-from-git.py /

CMD ["python2", "fontbakery-gather-dashboard-data-from-git.py"]
