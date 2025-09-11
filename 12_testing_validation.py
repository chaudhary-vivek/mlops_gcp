# test_pipeline.py
import requests
import json
from google.cloud import aiplatform

PROJECT_ID="udemy-mlops-471512"
REGION="us-central1"

def test_model_endpoint():
    """Test the deployed model endpoint"""
    
    # Initialize client
    aiplatform.init(project=PROJECT_ID, location=REGION)
    
    # Get endpoint
    endpoint = aiplatform.Endpoint("your-endpoint-resource-name")
    
    # Test data
    test_instances = [
        [5.1, 3.5, 1.4, 0.2],  # Setosa
        [7.0, 3.2, 4.7, 1.4],  # Versicolor
        [6.3, 3.3, 6.0, 2.5]   # Virginica
    ]
    
    # Get predictions
    predictions = endpoint.predict(instances=test_instances)
    
    print("Predictions:", predictions.predictions)
    
    # Get explanations if available
    try:
        predictions, explanations = endpoint.explain(instances=test_instances)
        print("Explanations:", explanations)
    except Exception as e:
        print(f"Explanations not available: {e}")

def validate_model_performance():
    """Validate model performance against test data"""
    
    # This would include more comprehensive validation
    # including A/B testing, shadow mode deployment, etc.
    pass

if __name__ == "__main__":
    test_model_endpoint()