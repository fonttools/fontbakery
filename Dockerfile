FROM python:2.7

RUN apt-get update
RUN apt-get install -y mono-complete
RUN apt-get install -y git-core

ADD requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt

ADD prebuilt/ot-sanitise /usr/local/bin/
ADD fontbakery-check-ttf.py /
ADD checks.py /
ADD utils.py /
ADD targetfont.py /
ADD upstreamdirectory.py /
ADD fonts_public_pb2.py /
ADD pifont.py /
ADD fbchecklogger.py /
ADD constants.py /

ADD dashboard/containers/worker/fontbakery-gather-dashboard-data-from-git.py /

CMD ["python2", "fontbakery-gather-dashboard-data-from-git.py"]
