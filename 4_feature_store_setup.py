# feature_store_setup.py
from google.cloud import aiplatform
from google.cloud.aiplatform import Feature, Featurestore, EntityType

PROJECT_ID="udemy-mlops-471512"
REGION="us-central1"

aiplatform.init(project=PROJECT_ID, location=REGION)

# Create Feature Store
# featurestore = Featurestore.create(
#     featurestore_id="iris_featurestore",
#     labels={"env": "development"}
# )

# OR use existing feature store
featurestore = aiplatform.Featurestore("iris_featurestore") 

# Create Entity Type
entity_type = EntityType.create(
    entity_type_id="iris_entity",
    featurestore_name=featurestore.resource_name,
    labels={"purpose": "iris_classification"}
)

# Create Features
features = [
    Feature.create(
        feature_id="sepal_length",
        entity_type_name=entity_type.resource_name,
        value_type="DOUBLE"
    ),
    Feature.create(
        feature_id="sepal_width",
        entity_type_name=entity_type.resource_name,
        value_type="DOUBLE"
    ),
    Feature.create(
        feature_id="petal_length",
        entity_type_name=entity_type.resource_name,
        value_type="DOUBLE"
    ),
    Feature.create(
        feature_id="petal_width",
        entity_type_name=entity_type.resource_name,
        value_type="DOUBLE"
    ),
]