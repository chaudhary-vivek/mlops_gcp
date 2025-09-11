# Vars
PROJECT_ID=udemy-mlops-471512
REGION=us-central1
BUCKET=gs://$PROJECT_ID-mlops-artifacts
REPO=mlops-trainer
AR_REPO=$PROJECT_ID-docker
IMAGE=trainer
SA=vertex-runner@$PROJECT_ID.iam.gserviceaccount.com

# setting project
gcloud config set project $PROJECT_ID

# enabling
# aiplatform
# bigquery
# composer
# dataproc
# monitoring
# logging
gcloud services enable aiplatform.googleapis.com \
  cloudbuild.googleapis.com artifactregistry.googleapis.com \
  bigquery.googleapis.com composer.googleapis.com \
  dataproc.googleapis.com monitoring.googleapis.com \
  logging.googleapis.com

# google storage make bucket -location region bucket name
gsutil mb -l $REGION $BUCKET

# Acreates a new artifact repo in specified loaction with type docker
gcloud artifacts repositories create $AR_REPO --repository-format=docker \
  --location=$REGION --description="Trainer images"

# Create a new service account named "vertex-runner" with display name "Vertex Runner"
gcloud iam service-accounts create vertex-runner --display-name "Vertex Runner"
# Grant the service account AI Platform Admin role (full access to Vertex AI resources)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA" \
  --role="roles/aiplatform.admin"
# Grant the service account Storage Admin role (manage Cloud Storage buckets/objects)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA" \
  --role="roles/storage.admin"
# Grant the service account BigQuery User role (query and run jobs in BigQuery)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA" \
  --role="roles/bigquery.user"
# Grant the service account Artifact Registry Reader role (pull Docker images from Artifact Registry)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA" \
  --role="roles/artifactregistry.reader"
