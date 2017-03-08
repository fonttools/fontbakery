PROJECT=fontbakery
GCLOUD="sudo /home/felipe/devel/prebuilt/google-cloud-sdk/bin/gcloud"
DOCKER="sudo docker"
SERVICES=dashboard/services
JOBS=dashboard/jobs

$DOCKER build -t job-fb-worker-1 .
$DOCKER tag job-fb-worker-1 gcr.io/$PROJECT/job-fb-worker-1
$GCLOUD docker -- push gcr.io/$PROJECT/job-fb-worker-1

$DOCKER build -t fb-dashboard-1 dashboard
$DOCKER tag fb-dashboard-1 gcr.io/$PROJECT/fb-dashboard-1
$GCLOUD docker -- push gcr.io/$PROJECT/fb-dashboard-1

$DOCKER build -t job-fb-dispatcher-1 dashboard/dispatcher
$DOCKER tag job-fb-dispatcher-1 gcr.io/$PROJECT/job-fb-dispatcher-1
$GCLOUD docker -- push gcr.io/$PROJECT/job-fb-dispatcher-1

$DOCKER build -t rethinkdb-2.3.5 dashboard/rethinkdb
$DOCKER tag rethinkdb-2.3.5 gcr.io/$PROJECT/rethinkdb-2.3.5
$GCLOUD docker -- push gcr.io/$PROJECT/rethinkdb-2.3.5

kubectl create -f $SERVICES/rabbitmq-service.yaml
kubectl create -f $SERVICES/rabbitmq-controller.yaml
kubectl create -f $SERVICES/rethinkdb-driver-service.yaml
kubectl create -f $SERVICES/rethinkdb-rc.yaml
kubectl create -f $SERVICES/rethinkdb-admin-service.yaml
kubectl create -f $SERVICES/flask-service.yaml
kubectl create -f $SERVICES/dashboard-rc.yaml

kubectl create -f $JOBS/worker.yaml
kubectl create -f $JOBS/dispatcher.yaml
