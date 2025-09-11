# training_pipeline.py
from kfp.v2 import dsl
from kfp.v2.dsl import component, Input, Output, Dataset, Model, Metrics
from typing import NamedTuple

PROJECT_ID="udemy-mlops-471512"
REGION="us-central1"

@component(
    base_image="python:3.9",
    packages_to_install=[
        "pandas==1.5.3",
        "scikit-learn==1.3.0",
        "google-cloud-bigquery==3.11.4",
        "google-cloud-storage==2.10.0"
    ]
)
def load_data(
    project_id: str,
    dataset: Output[Dataset]
) -> NamedTuple('Outputs', [('num_samples', int)]):
    """Load data from BigQuery"""
    import pandas as pd
    from google.cloud import bigquery
    
    client = bigquery.Client(project=project_id)
    
    query = f"""
    SELECT sepal_length, sepal_width, petal_length, petal_width, species
    FROM `{project_id}.iris_dataset.iris_data`
    """
    
    df = client.query(query).to_dataframe()
    df.to_csv(dataset.path, index=False)
    
    from collections import namedtuple
    Outputs = namedtuple('Outputs', ['num_samples'])
    return Outputs(num_samples=len(df))

@component(
    base_image="python:3.9",
    packages_to_install=[
        "pandas==1.5.3",
        "scikit-learn==1.3.0",
        "joblib==1.3.2"
    ]
)
def train_model(
    dataset: Input[Dataset],
    model: Output[Model],
    metrics: Output[Metrics],
    learning_rate: float = 0.01,
    max_iter: int = 1000
) -> NamedTuple('Outputs', [('accuracy', float)]):
    """Train logistic regression model"""
    import pandas as pd
    import joblib
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import LabelEncoder
    from sklearn.metrics import accuracy_score, classification_report
    import json
    
    # Load data
    df = pd.read_csv(dataset.path)
    
    # Prepare features and target
    X = df[['sepal_length', 'sepal_width', 'petal_length', 'petal_width']]
    le = LabelEncoder()
    y = le.fit_transform(df['species'])
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train model
    clf = LogisticRegression(
        C=1/learning_rate,
        max_iter=max_iter,
        random_state=42
    )
    clf.fit(X_train, y_train)
    
    # Evaluate
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    # Save model and label encoder
    model_artifacts = {
        'model': clf,
        'label_encoder': le,
        'feature_names': list(X.columns)
    }
    joblib.dump(model_artifacts, model.path)
    
    # Save metrics
    metrics_dict = {
        'accuracy': accuracy,
        'samples_count': len(df)
    }
    with open(metrics.path, 'w') as f:
        json.dump(metrics_dict, f)
    
    from collections import namedtuple
    Outputs = namedtuple('Outputs', ['accuracy'])
    return Outputs(accuracy=accuracy)

@component(
    base_image="python:3.9",
    packages_to_install=[
        "google-cloud-aiplatform==1.36.0",
        "joblib==1.3.2"
    ]
)
def deploy_model(
    model: Input[Model],
    project_id: str,
    region: str,
    model_name: str,
    endpoint_name: str
) -> str:
    """Deploy model to Vertex AI endpoint"""
    from google.cloud import aiplatform
    import joblib
    
    aiplatform.init(project=project_id, location=region)
    
    # Upload model to Model Registry
    vertex_model = aiplatform.Model.upload(
        display_name=model_name,
        artifact_uri=model.uri,
        serving_container_image_uri="gcr.io/cloud-aiplatform/prediction/sklearn-cpu.1-0:latest"
    )
    
    # Create endpoint
    endpoint = aiplatform.Endpoint.create(display_name=endpoint_name)
    
    # Deploy model to endpoint
    vertex_model.deploy(
        endpoint=endpoint,
        deployed_model_display_name=f"{model_name}-deployed",
        machine_type="n1-standard-2",
        min_replica_count=1,
        max_replica_count=3
    )
    
    return endpoint.resource_name

@dsl.pipeline(
    name="iris-classification-pipeline",
    description="Complete MLOps pipeline for Iris classification"
)
def iris_training_pipeline(
    project_id: str = PROJECT_ID,
    region: str = REGION,
    model_name: str = "iris-classifier",
    endpoint_name: str = "iris-endpoint",
    learning_rate: float = 0.01,
    max_iter: int = 1000
):
    """Main training pipeline"""
    
    # Load data
    load_data_op = load_data(project_id=project_id)
    
    # Train model
    train_model_op = train_model(
        dataset=load_data_op.outputs['dataset'],
        learning_rate=learning_rate,
        max_iter=max_iter
    )
    
    # Deploy model
    deploy_model_op = deploy_model(
        model=train_model_op.outputs['model'],
        project_id=project_id,
        region=region,
        model_name=model_name,
        endpoint_name=endpoint_name
    )