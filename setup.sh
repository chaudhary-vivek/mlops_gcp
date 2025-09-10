# Vars
PROJECT_ID=udemy-mlops-471512
REGION=us-central1
BUCKET=gs://$PROJECT_ID-mlops-artifacts
REPO=mlops-trainer
AR_REPO=$PROJECT_ID-docker
IMAGE=trainer
SA=vertex-runner@$PROJECT_ID.iam.gserviceaccount.com

gcloud config set project $PROJECT_ID
gcloud services enable aiplatform.googleapis.com \
  cloudbuild.googleapis.com artifactregistry.googleapis.com \
  bigquery.googleapis.com composer.googleapis.com \
  dataproc.googleapis.com monitoring.googleapis.com \
  logging.googleapis.com

gsutil mb -l $REGION $BUCKET

# Artifact Registry (Docker)
gcloud artifacts repositories create $AR_REPO --repository-format=docker \
  --location=$REGION --description="Trainer images"

# Runner service account + permissions (minimal working set)
gcloud iam service-accounts create vertex-runner --display-name "Vertex Runner"
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA" \
  --role="roles/aiplatform.admin"
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA" \
  --role="roles/storage.admin"
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA" \
  --role="roles/bigquery.user"
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA" \
  --role="roles/artifactregistry.reader"
