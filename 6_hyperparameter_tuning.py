# hyperparameter_tuning.py
from google.cloud import aiplatform
from google.cloud.aiplatform import hyperparameter_tuning as hpt

def create_hyperparameter_tuning_job():
    """Create hyperparameter tuning job"""
    
    # Define the worker pool spec
    worker_pool_specs = [
        {
            "machine_spec": {
                "machine_type": "n1-standard-4",
            },
            "replica_count": 1,
            "container_spec": {
                "image_uri": "gcr.io/cloud-aiplatform/training/sklearn-cpu.1-0:latest",
                "command": ["python", "train.py"],
                "args": [
                    "--learning_rate", "{{trial.parameters.learning_rate}}",
                    "--max_iter", "{{trial.parameters.max_iter}}",
                ]
            },
        }
    ]
    
    # Define hyperparameter search space
    parameter_spec = {
        "learning_rate": hpt.DoubleParameterSpec(min=0.001, max=0.1, scale="log"),
        "max_iter": hpt.IntegerParameterSpec(min=100, max=2000, scale="linear"),
    }
    
    # Define optimization metric
    metric_spec = hpt.MetricSpec(metric_id="accuracy", goal="MAXIMIZE")
    
    # Create the tuning job
    job = aiplatform.HyperparameterTuningJob(
        display_name="iris-hyperparameter-tuning",
        custom_job_spec=worker_pool_specs,
        parameter_spec=parameter_spec,
        metric_spec=metric_spec,
        max_trial_count=20,
        parallel_trial_count=4,
    )
    
    job.run()
    
    return job