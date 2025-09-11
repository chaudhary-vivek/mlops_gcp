export PROJECT_ID="udemy-mlops-471512"
export REGION="us-central1"
export BUCKET_NAME="gs://${PROJECT_ID}-mlops-bucket"

# Enable required APIs
gcloud services enable \
    compute.googleapis.com \
    storage.googleapis.com \
    bigquery.googleapis.com \
    aiplatform.googleapis.com \
    composer.googleapis.com \
    container.googleapis.com \
    cloudbuild.googleapis.com

# make storage bucket
gsutil mb -l  $REGION $BUCKET_NAME
