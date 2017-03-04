$PROJECT = fontbakery
$GCLOUD = /home/felipe/devel/prebuilt/google-cloud-sdk/bin/gcloud
$SERVICES = dashboard/services
$JOBS = dashboard/jobs

sudo docker build -t job-fb-worker-1 .
sudo docker build -t fb-dashboard-1 dashboard
sudo docker build -t job-fb-dispatcher-1 dashboard/dispatcher

sudo docker tag job-fb-worker-1 gcr.io/$PROJECT/job-fb-worker-1
sudo docker tag job-fb-dispatcher-1 gcr.io/$PROJECT/job-fb-dispatcher-1
sudo docker tag fb-dashboard-1 gcr.io/$PROJECT/fb-dashboard-1
sudo $GCLOUD docker -- push gcr.io/$PROJECT/job-fb-worker-1
sudo $GCLOUD docker -- push gcr.io/$PROJECT/job-fb-dispatcher-1
sudo $GCLOUD docker -- push gcr.io/$PROJECT/fb-dashboard-1

kubectl create -f $SERVICES/rabbitmq-service.yaml
kubectl create -f $SERVICES/rabbitmq-controller.yaml
kubectl create -f $SERVICES/rethinkdb-driver-service.yaml
kubectl create -f $SERVICES/rethinkdb-rc.yaml
kubectl create -f $SERVICES/rethinkdb-admin-pod.yaml
kubectl create -f $SERVICES/rethinkdb-admin-service.yaml
kubectl create -f $JOBS/dispatcher.yaml
kubectl create -f $JOBS/worker.yaml
kubectl create -f $JOBS/dashboard.yaml
