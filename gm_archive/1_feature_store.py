import os
import pandas as pd
from sklearn.datasets import load_breast_cancer
from google.cloud import aiplatform

# --- Configuration ---
PROJECT_ID = "udemy-mlops-471512"  # <--- REPLACE WITH YOUR GCP PROJECT ID
REGION = "us-central1" # Or your preferred region
FEATURESTORE_ID = "breast_cancer_featurestore"
ENTITY_TYPE_ID = "patient_data"
# This will be used as the entity ID in the Feature Store
ENTITY_ID_COLUMN = "patient_id"

# Initialize Vertex AI
aiplatform.init(project=PROJECT_ID, location=REGION)

print(f"Initializing Vertex AI for project: {PROJECT_ID}, region: {REGION}")

# --- 1. Load the Breast Cancer Wisconsin dataset ---
print("Loading Breast Cancer Wisconsin dataset...")
data = load_breast_cancer(as_frame=True)
df = data.frame
df['target'] = data.target # Add the target column explicitly

# Generate a unique patient_id for each row
df[ENTITY_ID_COLUMN] = [f"patient_{i}" for i in range(len(df))]

# Display first few rows and info
print("\nDataset head:")
print(df.head())
print("\nDataset info:")
df.info()

# Separate features and target for a clean feature set
# We'll ingest all feature columns and the 'target' as features
feature_columns = [col for col in df.columns if col not in [ENTITY_ID_COLUMN]]
print(f"\nFeatures to ingest: {feature_columns}")

# --- 2. Create a Vertex AI Feature Store instance ---
print(f"\nCreating Feature Store: {FEATURESTORE_ID} (this may take a few minutes)...")
try:
    feature_store = aiplatform.Featurestore.create(
        featurestore_id=FEATURESTORE_ID,
        project=PROJECT_ID,
        location=REGION,
        sync=True, # Wait for the creation to complete
        online_serving_config=aiplatform.gapic.OnlineServingConfig(
            fixed_node_count=1 # Use a small node count for this example
        )
    )
    print(f"Feature Store '{FEATURESTORE_ID}' created.")
except Exception as e:
    if "already exists" in str(e):
        print(f"Feature Store '{FEATURESTORE_ID}' already exists. Retrieving it.")
        feature_store = aiplatform.Featurestore(featurestore_name=FEATURESTORE_ID)
    else:
        raise e

# --- 3. Create an Entity Type ---
print(f"Creating Entity Type: {ENTITY_TYPE_ID}...")
try:
    entity_type = feature_store.create_entity_type(
        entity_type_id=ENTITY_TYPE_ID,
        description="Patient data for breast cancer diagnosis",
        sync=True
    )
    print(f"Entity Type '{ENTITY_TYPE_ID}' created.")
except Exception as e:
    if "already exists" in str(e):
        print(f"Entity Type '{ENTITY_TYPE_ID}' already exists. Retrieving it.")
        entity_type = feature_store.get_entity_type(entity_type_id=ENTITY_TYPE_ID)
    else:
        raise e

# --- 4. Define Features for the Entity Type ---
print(f"Creating Features for Entity Type '{ENTITY_TYPE_ID}'...")
# Determine feature value type based on pandas dtype
def get_feature_value_type(dtype):
    if pd.api.types.is_numeric_dtype(dtype):
        # For simplicity, treat all numeric as FLOAT for this dataset.
        # In a real scenario, you might have INT for counts, BOOL for flags.
        return aiplatform.gapic.Feature.ValueType.DOUBLE
    else:
        return aiplatform.gapic.Feature.ValueType.STRING # Fallback for other types

features_to_create = []
for col in feature_columns:
    # Check if feature already exists to avoid errors
    feature_exists = False
    for existing_feature in entity_type.list_features():
        if existing_feature.name.split('/')[-1] == col:
            print(f"  Feature '{col}' already exists. Skipping creation.")
            feature_exists = True
            break
    if not feature_exists:
        value_type = get_feature_value_type(df[col].dtype)
        print(f"  Adding feature '{col}' with ValueType: {aiplatform.gapic.Feature.ValueType(value_type).name}")
        features_to_create.append(
            aiplatform.Feature(
                feature_id=col,
                value_type=value_type,
                description=f"Feature: {col}"
            )
        )

if features_to_create:
    entity_type.batch_create_features(
        features=features_to_create,
        sync=True
    )
    print(f"Created {len(features_to_create)} new features.")
else:
    print("No new features to create.")


# --- 5. Ingest data into the Feature Store ---
print(f"\nIngesting data into Feature Store '{FEATURESTORE_ID}', Entity Type '{ENTITY_TYPE_ID}'...")

# The DataFrame needs to have the entity ID column set as the index
ingestion_df = df.set_index(ENTITY_ID_COLUMN)

# Save the DataFrame to a CSV in Cloud Storage for ingestion
BUCKET_NAME = f"{PROJECT_ID}-feature-store-data"
GCS_URI = f"gs://{BUCKET_NAME}/breast_cancer_data/data_for_ingestion.csv"

# Create a GCS bucket if it doesn't exist
print(f"Ensuring GCS bucket {BUCKET_NAME} exists...")
try:
    from google.cloud import storage
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.get_bucket(BUCKET_NAME)
    print(f"Bucket {BUCKET_NAME} already exists.")
except Exception as e:
    if "Not Found" in str(e) or "does not exist" in str(e):
        print(f"Bucket {BUCKET_NAME} not found, creating it...")
        bucket = storage_client.create_bucket(BUCKET_NAME, location=REGION)
        print(f"Bucket {BUCKET_NAME} created.")
    else:
        raise e

# Save DataFrame to GCS
print(f"Saving DataFrame to GCS: {GCS_URI}")
ingestion_df.to_csv(GCS_URI)

# Perform batch ingestion
try:
    ingestion_job = entity_type.ingest_from_gcs(
        feature_ids=feature_columns, # All columns except the index (entity_id)
        feature_time=pd.Timestamp.now(), # Use current time as feature time
        gcs_uri=GCS_URI,
        feature_data_format="csv",
        sync=True
    )
    print(f"Data ingestion job completed: {ingestion_job.name}")
except Exception as e:
    print(f"Error during ingestion: {e}")
    print("If you encounter 'Invalid argument: Column [X] not found in the input CSV file. Make sure column names match feature ids.',")
    print("ensure your CSV headers exactly match the feature IDs you defined.")

print("\n--- Feature Store Setup Complete ---")
print(f"You can view your Feature Store here: https://console.cloud.google.com/vertex-ai/feature-store/featurestores/{FEATURESTORE_ID}/entity-types/{ENTITY_TYPE_ID}/features?project={PROJECT_ID}&region={REGION}")