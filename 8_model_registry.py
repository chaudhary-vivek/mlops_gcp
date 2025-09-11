# model_registry.py
from google.cloud import aiplatform

PROJECT_ID="udemy-mlops-471512"
REGION="us-central1"

def register_model_version(model_path: str, version_description: str):
    """Register a new model version"""
    
    aiplatform.init(project=PROJECT_ID, location=REGION)
    
    # Upload new model version
    model = aiplatform.Model.upload(
        display_name="iris-classifier",
        artifact_uri=model_path,
        serving_container_image_uri="gcr.io/cloud-aiplatform/prediction/sklearn-cpu.1-0:latest",
        version_description=version_description,
        version_aliases=["latest"],
        labels={"framework": "scikit-learn", "task": "classification"}
    )
    
    return model

def promote_model_to_production(model_id: str, version_id: str):
    """Promote model version to production"""
    
    model = aiplatform.Model(model_name=model_id)
    
    # Add production alias
    model.add_version_aliases(
        version_aliases=["production", "stable"],
        version=version_id
    )
    
    # Remove from staging
    model.remove_version_aliases(
        version_aliases=["staging"],
        version=version_id
    )
    
    return model