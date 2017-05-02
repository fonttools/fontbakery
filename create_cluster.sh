PROJECT=fontbakery
# @felipe, maybe you could put gcloud on your PATH?
GCLOUD="sudo $(which gcloud || echo '/home/felipe/devel/prebuilt/google-cloud-sdk/bin/gcloud')"
DOCKER="sudo docker"

$GCLOUD container clusters create fbakery-dashboard --zone us-central1-a

