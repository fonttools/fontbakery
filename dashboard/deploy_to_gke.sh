# envvars_setup.sh
PROJECT=fontbakery
GCLOUD="sudo /home/felipe/devel/prebuilt/google-cloud-sdk/bin/gcloud"
DOCKER="sudo docker"

# update_database:
$DOCKER build -t rethinkdb-2.3.5 containers/rethinkdb
$DOCKER tag rethinkdb-2.3.5 gcr.io/$PROJECT/rethinkdb-2.3.5
$GCLOUD docker -- push gcr.io/$PROJECT/rethinkdb-2.3.5
kubectl delete rc rethinkdb-rc
kubectl create -f services/rethinkdb-driver-service.yaml
kubectl create -f services/rethinkdb-rc.yaml
kubectl create -f services/rethinkdb-admin-service.yaml

# update flask service
# Note: This will affect the publicly accessinble IP address.
kubectl delete svc flaskapp-service
kubectl create -f services/flask-service.yaml

# update_frontend:
$DOCKER build -t fb-dashboard-1 containers/web
$DOCKER tag fb-dashboard-1 gcr.io/$PROJECT/fb-dashboard-1
$GCLOUD docker -- push gcr.io/$PROJECT/fb-dashboard-1
kubectl delete rc dashboard-rc
kubectl create -f services/dashboard-rc.yaml


#   -> "kill all":
kubectl delete svc rabbitmq-service
kubectl delete rc rabbitmq-controller
kubectl delete job job-fb-worker-1
kubectl delete job job-fb-dispatcher-1

# update_queue_service:
kubectl delete svc rabbitmq-service
kubectl delete rc rabbitmq-controller
kubectl create -f services/rabbitmq-service.yaml
kubectl create -f services/rabbitmq-controller.yaml

# update_workers:
$DOCKER build -t job-fb-worker-1 ..
$DOCKER tag job-fb-worker-1 gcr.io/$PROJECT/job-fb-worker-1
$GCLOUD docker -- push gcr.io/$PROJECT/job-fb-worker-1
kubectl delete job job-fb-worker-1
kubectl create -f jobs/worker.yaml

# update_dispatcher:
$DOCKER build -t job-fb-dispatcher-1 containers/dispatcher
$DOCKER tag job-fb-dispatcher-1 gcr.io/$PROJECT/job-fb-dispatcher-1
$GCLOUD docker -- push gcr.io/$PROJECT/job-fb-dispatcher-1
kubectl delete job job-fb-dispatcher-1
kubectl create -f jobs/dispatcher.yaml

# overall status:
kubectl get jobs
kubectl get pods
kubectl get svc
kubectl get rc




