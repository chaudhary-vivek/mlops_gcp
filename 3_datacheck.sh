mlops_gcp % bq ls udemy-mlops-471512:iris_dataset   

bq query --use_legacy_sql=false \
"SELECT COUNT(*) AS row_count FROM \`udemy-mlops-471512.iris_dataset.iris_data\`"



