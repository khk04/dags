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
            'requests': {
                'memory': '16Gi',
                'cpu': '4000m'
            },
            'limits': {
                'memory': '16Gi',
                'cpu': '4000m'
            }
        },
    )

    stress_test = KubernetesPodOperator(
        namespace='default',
        image="alpine",
        cmds=["sh", "-c"],
        arguments=["apk add --no-cache stress-ng && stress-ng --cpu 4 --timeout 60s"],
        labels={"foo": "bar"},
        name="stress-test-pod",
        task_id="task-stress",
        get_logs=True,
        resources={
            'requests': {
                'memory': '16Gi',
                'cpu': '4000m'
            },
            'limits': {
                'memory': '16Gi',
                'cpu': '4000m'
            }
        },
    )

    k >> stress_test
