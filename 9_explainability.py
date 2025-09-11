# explainability.py
from google.cloud import aiplatform

PROJECT_ID="udemy-mlops-471512"
REGION="us-central1"

def setup_model_explanations():
    """Set up model explanations using Vertex AI"""
    
    # Define explanation parameters
    explanation_parameters = aiplatform.explain.ExplanationParameters(
        {
            "sampled_shapley_attribution": {
                "path_count": 10
            }
        }
    )
    
    # Deploy model with explanations
    model = aiplatform.Model("projects/{}/locations/{}/models/{}".format(
        PROJECT_ID, REGION, "your-model-id"
    ))
    
    endpoint = aiplatform.Endpoint.create(
        display_name="iris-endpoint-with-explanations"
    )
    
    model.deploy(
        endpoint=endpoint,
        deployed_model_display_name="iris-with-explanations",
        explanation_parameters=explanation_parameters,
        machine_type="n1-standard-2"
    )
    
    return endpoint

def get_prediction_with_explanation(endpoint_name: str, instances: list):
    """Get prediction with explanation"""
    
    endpoint = aiplatform.Endpoint(endpoint_name)
    
    response = endpoint.explain(instances=instances)
    
    predictions = response.predictions
    explanations = response.explanations
    
    return predictions, explanations