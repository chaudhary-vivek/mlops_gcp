# add permission
gcloud projects add-iam-policy-binding udemy-mlops-471512 \
    --member="serviceAccount:vertex-runner@udemy-mlops-471512.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountAdmin"

gcloud projects add-iam-policy-binding udemy-mlops-471512 \
    --member="serviceAccount:service-275750962721@cloudcomposer-accounts.iam.gserviceaccount.com" \
    --role="roles/composer.ServiceAgentV2Ext"


# create composer environment
gcloud composer environments create iris-mlops-env\
    --location=us-central1 \
    --service-account=vertex-runner@udemy-mlops-471512.iam.gserviceaccount.com \
    --image-version=composer-2.14.1-airflow-2.9.3 

# check version
gcloud composer environments describe iris-mlops-env \
    --location=us-central1 \
    --format="value(config.softwareConfig.imageVersion)"


# create composer
gcloud composer environments create iris-mlops-env \
    --location=us-central1 \
    --service-account=vertex-runner@udemy-mlops-471512.iam.gserviceaccount.com \
    --image-version=composer-2.14.1-airflow-2.9.3 
