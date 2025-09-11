# deploy.py
import os
from google.cloud import aiplatform
from kfp.v2 import compiler

# Set environment variables
PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION")
BUCKET_NAME = os.getenv("BUCKET_NAME")

def deploy_complete_pipeline():
    """Deploy the complete MLOps pipeline"""
    
    # Initialize Vertex AI
    aiplatform.init(project=PROJECT_ID, location=REGION, staging_bucket=f"{BUCKET_NAME}")
    
    # 1. Compile the pipeline
    compiler.Compiler().compile(
        pipeline_func=iris_training_pipeline,
        package_path="iris_pipeline.json"
    )
    
    # 2. Create and run the pipeline job
    job = aiplatform.PipelineJob(
        display_name="iris-mlops-pipeline",
        template_path="iris_pipeline.json",
        parameter_values={
            "project_id": PROJECT_ID,
            "region": REGION,
            "model_name": "iris-classifier-v1",
            "endpoint_name": "iris-production-endpoint"
        }
    )
    
    job.submit()
    
    # 3. Set up monitoring after deployment
    # This would be called after the pipeline completes
    # setup_model_monitoring(endpoint.resource_name)
    
    return job

if __name__ == "__main__":
    job = deploy_complete_pipeline()
    print(f"Pipeline job submitted: {job.resource_name}")