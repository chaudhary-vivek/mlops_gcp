# Set your project ID and region
export PROJECT_ID="udemy-mlops-new"
export REGION="us-central1" 
export BUCKET_NAME="gs://${PROJECT_ID}-iris-mlops"

# Configure gcloud
gcloud config set project $PROJECT_ID
gcloud config set compute/region $REGION

# Enable necessary APIs
gcloud services enable \
    aiplatform.googleapis.com \
    composer.googleapis.com \
    containerregistry.googleapis.com \
    cloudbuild.googleapis.com

# Create a Cloud Storage bucket
gsutil mb -l $REGION $BUCKET_NAME