# dags/iris_mlops_dag.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.google.cloud.operators.vertex_ai import (
    CreateCustomPythonPackageTrainingJobOperator,
    RunPipelineJobOperator
)
from airflow.providers.google.cloud.operators.bigquery import BigQueryCheckOperator
from airflow.providers.google.cloud.operators.gcs import GCSFileExistsSensor

default_args = {
    'owner': 'mlops-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'iris_mlops_pipeline',
    default_args=default_args,
    description='Complete MLOps pipeline for Iris classification',
    schedule_interval='@daily',
    catchup=False,
    max_active_runs=1,
    tags=['mlops', 'iris', 'classification']
)

# Check if new data is available
data_check = BigQueryCheckOperator(
    task_id='check_data_freshness',
    sql=f"""
    SELECT COUNT(*) as count
    FROM `{PROJECT_ID}.iris_dataset.iris_data`
    WHERE feature_timestamp >= CURRENT_TIMESTAMP() - INTERVAL 1 DAY
    """,
    dag=dag
)

# Run the ML pipeline
run_pipeline = RunPipelineJobOperator(
    task_id='run_training_pipeline',
    region=REGION,
    project_id=PROJECT_ID,
    display_name='iris-training-pipeline-{{ ds }}',
    pipeline_spec_path='gs://your-bucket/pipeline_spec.json',
    dag=dag
)

# Set up dependencies
data_check >> run_pipeline