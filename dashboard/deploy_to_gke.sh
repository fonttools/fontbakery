PROJECT=fontbakery
GCLOUD="sudo /home/felipe/devel/prebuilt/google-cloud-sdk/bin/gcloud"
DOCKER="sudo docker"

$DOCKER build -t job-fb-worker-1 containers/worker
$DOCKER tag job-fb-worker-1 gcr.io/$PROJECT/job-fb-worker-1
$GCLOUD docker -- push gcr.io/$PROJECT/job-fb-worker-1

$DOCKER build -t fb-dashboard-1 containers/web
$DOCKER tag fb-dashboard-1 gcr.io/$PROJECT/fb-dashboard-1
$GCLOUD docker -- push gcr.io/$PROJECT/fb-dashboard-1

$DOCKER build -t job-fb-dispatcher-1 containers/dispatcher
$DOCKER tag job-fb-dispatcher-1 gcr.io/$PROJECT/job-fb-dispatcher-1
$GCLOUD docker -- push gcr.io/$PROJECT/job-fb-dispatcher-1

$DOCKER build -t rethinkdb-2.3.5 containers/rethinkdb
$DOCKER tag rethinkdb-2.3.5 gcr.io/$PROJECT/rethinkdb-2.3.5
$GCLOUD docker -- push gcr.io/$PROJECT/rethinkdb-2.3.5

kubectl create -f services/rabbitmq-service.yaml
kubectl create -f services/rabbitmq-controller.yaml
kubectl create -f services/rethinkdb-driver-service.yaml
kubectl create -f services/rethinkdb-rc.yaml
kubectl create -f services/rethinkdb-admin-service.yaml
kubectl create -f services/flask-service.yaml
kubectl create -f services/dashboard-rc.yaml

kubectl create -f jobs/worker.yaml
kubectl create -f jobs/dispatcher.yaml
