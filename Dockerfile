FROM python:2.7

RUN apt-get update
RUN apt-get install -y mono-complete
RUN apt-get install -y git-core
RUN apt-get install -y unzip

ADD requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt

ADD prebuilt/ot-sanitise /usr/local/bin/
RUN python setup.py install

## Install fontforge.
#RUN apt-get install -y software-properties-common
#RUN add-apt-repository ppa:fontforge/fontforge
#RUN apt-get update
#RUN apt-get install -y fontforge-nox python-fontforge

ADD dashboard/containers/worker/fontbakery-gather-dashboard-data-from-git.py /

CMD ["python2", "fontbakery-gather-dashboard-data-from-git.py"]
