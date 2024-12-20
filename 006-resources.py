from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from datetime import datetime

default_args = {
    'start_date': datetime(2023, 1, 1),
}

with DAG(
    'example_kubernetes_resources',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    task = KubernetesPodOperator(
        task_id='example_task',
        name='example_pod',
        namespace='airflow',
        image='ubuntu:20.04',
        container_resources={
            'requests': {
                'memory': '4Gi',
                'cpu': '5'
            },
            'limits': {
                'memory': '8Gi',
                'cpu': '7'
            },
        },
        cmds=["bash", "-c"],
        arguments=[
            "apt update && apt install -y stress && "
            "stress --cpu 5 --timeout 300 && "
            "echo 'Hello, Airflow!'"
        ],
    )

task