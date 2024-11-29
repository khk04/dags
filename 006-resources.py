from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from datetime import datetime

default_args = {
    'start_date': datetime(2023, 1, 1),
}

with DAG(
    '006-pod-resources-example',
    default_args=default_args,
    schedule_interval=None,
) as dag:

    k = KubernetesPodOperator(
        namespace='default',
        image="ubuntu:16.04",
        cmds=["bash", "-cx"],
        arguments=["echo", "10"],
        labels={"foo": "bar"},
        name="airflow-test-pod",
        task_id="task-one",
        get_logs=True,
        resources={
            'request_memory': '64Mi',
            'request_cpu': '250m',
            'limit_memory': '128Mi',
            'limit_cpu': '500m',
        },
    )
