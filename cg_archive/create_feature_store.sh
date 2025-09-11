# Create Feature Store
gcloud ai featurestores create census_fs \
  --region=$REGION \
  --online-store-fixed-node-count=1
  
# Create entity type
gcloud alpha aiplatform featurestores entity-types create person \
  --featurestore=census_fs --region=$REGION

# Create a few features (tabular)
gcloud alpha aiplatform featurestores entity-types features create age \
  --featurestore=census_fs --entity-type=person --value-type=INT64 --region=$REGION
# (repeat for hours_per_week, education_num, categorical encoded features, etc.)
