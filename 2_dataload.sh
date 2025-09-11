

# copy csv file to bucket
gsutil cp iris.csv ${BUCKET_NAME}/data/iris.csv

# create an empty schema locally
bq query --use_legacy_sql=false \
"CREATE SCHEMA \`${PROJECT_ID}.iris_dataset\`"

# Load from Cloud Storage to local BigQuery
bq load \
    --source_format=CSV \
    --autodetect \
    --replace \
    iris_dataset.iris_data \
    ${BUCKET_NAME}/data/iris.csv