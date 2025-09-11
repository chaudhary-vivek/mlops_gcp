# monitoring.py
from google.cloud import aiplatform
from google.cloud.aiplatform import ModelDeploymentMonitoringJob

PROJECT_ID="udemy-mlops-471512"
REGION="us-central1"

def setup_model_monitoring(endpoint_resource_name: str):
    """Set up model monitoring for drift detection"""
    
    # Define monitoring config
    monitoring_config = {
        "objective_config": {
            "training_dataset": {
                "target_field": "species",
                "bigquery_source": {
                    "input_uri": f"bq://{PROJECT_ID}.iris_dataset.iris_data"
                },
                "data_format": "bigquery"
            },
            "training_prediction_skew_detection_config": {
                "skew_thresholds": {
                    "sepal_length": {"value": 0.1},
                    "sepal_width": {"value": 0.1},
                    "petal_length": {"value": 0.1},
                    "petal_width": {"value": 0.1},
                }
            },
            "prediction_drift_detection_config": {
                "drift_thresholds": {
                    "sepal_length": {"value": 0.1},
                    "sepal_width": {"value": 0.1},
                    "petal_length": {"value": 0.1},
                    "petal_width": {"value": 0.1},
                }
            }
        }
    }
    
    # Create monitoring job
    monitoring_job = ModelDeploymentMonitoringJob.create(
        display_name="iris-model-monitoring",
        endpoint=endpoint_resource_name,
        logging_sampling_strategy={
            "random_sample_config": {"sample_rate": 0.1}
        },
        model_deployment_monitoring_objective_configs=[monitoring_config],
        model_monitoring_alert_config={
            "email_alert_config": {
                "user_emails": ["your-email@domain.com"]
            }
        }
    )
    
    return monitoring_job